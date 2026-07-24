# Linux 4.14.283 Bootloop Handoff

Date: 2026-07-23

This document hands the Odessa recovery-kernel regression investigation to the
next agent. Read `MEMORY.md` as well, but use this document as the concise
starting point for the current failure.

## User direction and current safety state

- The user wants the bootloop fixed and asked not to spend time validating
  slot A or recovery A after each failed slot-B test.
- Respect that preference for routine checks, but continue to state the risk
  before every partition write and use only explicit slot-B partition names.
- The accepted diagnostic operation writes only `dtbo_b`, `recovery_b`, and
  `vbmeta_b`, selects B, and requests Recovery. Do not write `boot_b`, firmware,
  dynamic partitions, `super`, userdata, or any slot-A partition.
- The last operation selected slot B and booted the nodemask candidate. The
  user reported a bootloop. Do not assume the phone's current mode or active
  slot; it may have returned to bootloader with B active.
- Immediately before these latest tests, bootloader fastboot had reported slot
  A bootable but `slot-successful:a: no`. The user explicitly declined the
  proposed slot-A validation. Automatic fallback is therefore not confirmed.
- The exact-device Motorola Software Fix restore route remains the full
  fallback. Do not improvise a stock fastboot script.

## Fixed test model

All useful candidates are one-variable Lineage Recovery images. They preserve
the same recovery ramdisk, embedded base DTB, embedded recovery DTBO, external
DTBO, header-v2 metadata, command line, OS metadata, and control images. Only
the kernel, recovery AVB footer, and dependent top-level diagnostic vbmeta
change.

The authoritative boundaries are:

- Motorola parent: `92a96be148a072185131f60977af463c918b58cd`.
- Android-common 4.14.282: `1f161a096b52aff01e5ababb9da7e76e5e4e12ff`.
- Android-common 4.14.283: `bc1a5b8c02ae4f3f821f3b325bad7bf87e679450`.
- Reproducible 4.14.282 synthesis: `2cfed6f0b1c45932868990ab79fa70c5b6cfd5c8`.
- Reproducible 4.14.283 synthesis: `1bd9d46c6b5f2870903474452f93d5ef71d1ee09`.

Both boundaries use `CONFIG_SPECULATIVE_PAGE_FAULT=n`, retain the
boundary-valid Qualcomm early-RNG no-sleep correction, and preserve exact
Android-common `mm/memory.c` with SHA-256
`2abb8a7dd65a6c42ff5aab03e8dd665a1dc6b481fb39dcb8de6d0152094e9277`.

## Verified pass/fail matrix

| Candidate | Source | Result |
| --- | --- | --- |
| 4.14.282 with generic imported DWC3 | `2cfed6f0b1c4` | Recovery UI boots, but no USB enumeration or ADB |
| 4.14.282 with coherent Qualcomm DWC3 | `0625428fb4ec` | PASS: Recovery UI, USB gadget, FunctionFS, and ADB |
| Original reproducible 4.14.283 | `1bd9d46c6b5f` | FAIL: bootloop before Recovery UI |
| 4.14.283 with coherent Qualcomm DWC3 | `6a01c7ef2a18` | FAIL: bootloop before Recovery UI |
| 4.14.283 with Qualcomm DWC3 and UFS `wmb()` restore | uncommitted on `6a01c7e` | FAIL: bootloop before Recovery UI |
| 4.14.283 with Qualcomm DWC3 and 4.14.282 nodemask semantics | uncommitted on `6a01c7e` | FAIL: bootloop before Recovery UI |
| 4.14.283 with Qualcomm DWC3 and 4.14.282 trace semantics | uncommitted on `6a01c7e` | FAIL: bootloop before Recovery UI |
| 4.14.283 with Qualcomm DWC3 and 4.14.282 mailbox semantics | uncommitted on `6a01c7e` | FAIL: bootloop before Recovery UI |
| 4.14.283 with Qualcomm DWC3 and 4.14.282 extcon semantics | uncommitted on `6a01c7e` | PASS: Recovery UI and USB/ADB enumeration |

The coherent DWC3 restoration is required for USB/ADB observability but does
not fix the 4.14.283 bootloop. Keep it in all future candidates.

## DWC3 fix that must be retained

Branch: `wip/odessa-4.14.283-usb-adb-fix`

Commit: `6a01c7ef2a186f243fb35d5b08942dbbd0684ee5`

This is exact 4.14.283 candidate `1bd9d46` plus only:

- `drivers/usb/dwc3/core.c`
- `drivers/usb/dwc3/gadget.c`

Those files restore the coherent Motorola/Qualcomm controller integration
already hardware-verified on 4.14.282. The corrected 4.14.283 package is:

`lineageos/.downloads/diagnostic-recovery-4.14.283-qualcomm-dwc3-20260722/`

- Kernel Image: `0326aebc1e345ba8ec093f890e2157cf5bbeb6055f397c66b7930ec45d95dc98`.
- Recovery: `3b0c4040dfbe83886070a52f69316c094110c2311f1f08e7173173f0f2c7891a`.
- DTBO: `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`.
- Vbmeta: `70b2d6b6e47a96f395da27832bed488e6ff37f935a0511fbc68c7bc1a74b6cec`.

## Ruled-out focused hypotheses

### Qualcomm UFS ref-clock readback

Stable commit `cf90ea494bb4c0231214e905e4bc977cd9cbdae7` replaces a
post-`writel_relaxed()` `wmb()` with a same-register `readl()` in
`drivers/scsi/ufs/ufs-qcom.c`.

The exact one-file revert was built and tested. It still bootlooped, so this
commit is not the sole cause. Do not keep modifying the barrier without new
evidence. Advanced Qualcomm 4.14 downstreams also retain the upstream
`readl()` behavior.

Worktree: `/tmp/opencode/sm6150-4.14.283-ufs-fix`

Package:
`lineageos/.downloads/diagnostic-recovery-4.14.283-qualcomm-dwc3-ufs-fix-20260723/`

- Patch SHA-256: `6259e256c064aa9f2967261d9efa089a899aaeae8acb4f230dcdf4de997dc40d`.
- Recovery: `de328441f51244fadf5b2c040d1e8d2493269d05c36fac3b81c336e0768b801e`.

### Nodemask/cpuset/IRQ-affinity closure

The linked-object comparison found that the 4.14.283 nodemask changes alter
generated code in `kernel/cgroup/cpuset.o` and `kernel/irq/affinity.o`, even
though those `.c` files are absent from a simple source-diff audit. A candidate
restored `include/linux/nodemask.h` and `lib/nodemask.c` to 4.14.282 semantics.
Its nodemask executable `.text` matched 4.14.282 byte-for-byte, but it still
bootlooped. Do not repeat it.

Worktree: `/tmp/opencode/sm6150-4.14.283-nodemask-fix`

Package:
`lineageos/.downloads/diagnostic-recovery-4.14.283-qualcomm-dwc3-nodemask-fix-20260723/`

- Patch SHA-256: `357fb798c4cf12dd3c18aaf473be7dac981791119a90b4d656fee5f8b54dd3e0`.
- Recovery: `1864aae86b2888cf260216badb3648d7a453a3801162ad74b725d24300171e8e`.
- Kernel Image: `4bdcf4a8f5ac90dff75638553a0aed08ec87c26750f4a589fb685fc926f75e9e`.
- Vbmeta: `19c9d086a3a429a643d9a47fe252fc1cb21f4a8e9161bf11ed9ffa2d675743f1`.

### Changes not worth another immediate test

- Generic MSM DSI commit `ac70d51feabc37ded85be090fbf28541606b057f`:
  Odessa has `CONFIG_DRM_MSM_DSI=n` and uses
  `CONFIG_DRM_MSM_DSI_STAGING=y`; the changed generic `dsi_host.c` is not
  linked.
- SMP2P `of_node_put()` commit
  `7f868a3a4950919fed3dcada35fbff8b18c24fa2`: with dynamic OF disabled,
  the added operation compiles away and `.282`/`.283` allocated object code is
  identical.
- SMSM is not linked.
- USB quirks only add a Dell VID/PID entry and cannot match Odessa's internal
  controller.
- PSI trigger, ptrace, networking, Bluetooth, and audio changes require later
  userspace/runtime activity and are poor pre-Recovery candidates.

## Linked-kernel analysis

The generated `.282` and `.283` configurations are functionally identical;
only the version comment differs. A linked-object comparison found:

- 35 directly changed source compilation units linked into `vmlinux`.
- Four of those have identical allocated code/data after preprocessing.
- Header changes affect ten additional linked objects.
- In total, 41 behavior-bearing linked object deltas remain.

The 4.14.283 build output used for this analysis is under:

`lineageos/.downloads/diagnostic-recovery-4.14.283-qualcomm-dwc3-20260722/kernel-out/`

The known-good 4.14.282 full output was produced under:

`/tmp/opencode/sm6150-4.14.282-usb-qualcomm-out-clang/`

Do not return to source-file counting alone. Inspect linked object code,
header-propagated changes, initcall level, and whether the changed function is
actually reachable before Recovery UI.

## Recommended next candidate

Start from `6a01c7ef2a186f243fb35d5b08942dbbd0684ee5`. Do not stack
the failed UFS or nodemask diagnostics.

The trace initialization pair was tested and failed to resolve the bootloop:
`kernel/trace/trace.c`:

- `be1f323fb9d9b14a505ca22d742d321769454de1`
- `0816ec55fc0b2a4abe7048f13e6fac652670922a`

The next focused group is therefore the mailbox core closure described below.

Why trace was tested:

- `tracer_init_tracefs()` is a level-5 filesystem initcall and definitely runs
  before level-6 UFS, DRM, DWC3, extcon, and most device drivers.
- The trace-to-printk raw-spinlock hunk is probably dormant because the command
  line has no trace options, but the trace-option initialization hunk executes
  during tracefs setup.
- It is a clean one-file, two-commit diagnostic group.

The mailbox group failed and the extcon group passed. Do not proceed to ext4
until a forward-safe extcon fix has been tested.

Original remaining group order:

1. Mailbox core closure: restore `drivers/mailbox/mailbox.c` and
   `include/linux/mailbox_controller.h` together, reverting
   `e75b5ea2d6b15ba769d7c00261506ba35f13143e` diagnostically.
2. Extcon registration: restore `drivers/extcon/extcon.c`, reverting
   `6e721f3ad0535b24f19a62420f4da95212cf069c` diagnostically.
3. Recovery-filesystem group: restore `fs/ext4/inline.c` and
   `fs/ext4/namei.c` together from the passing 4.14.282 candidate. Treat this
   only as a diagnostic because the 4.14.283 ext4 changes include security and
   correctness fixes plus a local interface bridge.

If these focused groups all fail, stop doing isolated guesses. Build a
coarse grouped revert that restores all pre-Recovery behavior-bearing linked
objects to the passing 4.14.282 state while retaining the 4.14.283 version and
unrelated stable fixes. Once that boots, add groups back using the hardware
oracle. Do not fake `SUBLEVEL`, copy later 4.14.336 files into the boundary, or
remove AVB/VINTF checks.

## Packaging requirements

For every candidate:

- Build genuine `4.14.283-perf+` with Android clang r563880c, LLVM/IAS,
  `vendor/odessa_defconfig`, and the established `-j8` command.
- Keep the generated config unchanged.
- Preserve exact boundary `mm/memory.c`.
- Save the exact source patch and SHA-256 in the ignored package directory.
- Require `git diff --check` and an exact changed-file allowlist.
- Compare ramdisk, embedded DTB, embedded recovery DTBO, external DTBO,
  header metadata, and control images against the established template.
- Verify recovery and DTBO AVB plus top-level vbmeta follow-chain through boot,
  recovery, DTBO, product, system, and vendor.
- Use immutable candidate directories under `lineageos/.downloads/`; never
  flash mutable loose files from `out/`.

## Repository state

- Main kernel checkout should remain on `lineage-23.2` at
  `41038075962c29364e02cbe5a548904b1f88e028` and clean.
- Corrected 4.14.283 DWC3 branch:
  `wip/odessa-4.14.283-usb-adb-fix` at `6a01c7ef2a18`.
- Failed UFS diagnostic branch/worktree:
  `wip/odessa-4.14.283-ufs-fix`,
  `/tmp/opencode/sm6150-4.14.283-ufs-fix`, one uncommitted UFS file.
- Failed nodemask diagnostic branch/worktree:
  `wip/odessa-4.14.283-nodemask-fix`,
  `/tmp/opencode/sm6150-4.14.283-nodemask-fix`, two uncommitted nodemask files.
- Do not commit, remove, or overwrite those diagnostic worktrees until their
  ignored provenance packages have been checked if cleanup is requested.

No bootloop fix is confirmed yet. The only confirmed fixes are the separate
4.14.282 Qualcomm DWC3 Recovery USB/ADB repair and the source/build correctness
of the diagnostic packages.

## Extcon root cause found after handoff

The passing one-file extcon restore isolates stable commit
`6e721f3ad0535b24f19a62420f4da95212cf069c`. The upstream change delays
`device_register()` until after `dev_set_drvdata()` and converts upstream
`edev->nh` from devm allocation to `kcalloc`, because the extcon device is not
initialized before `device_register()`. Motorola's local `edev->bnh`
allocation remained `devm_kzalloc(&edev->dev, ...)` before registration. This
uses the uninitialized device-resource lock and can hang during early extcon
registration. Retain the stable ordering and convert local `bnh` to explicit
allocation with balanced error/unregister frees; do not keep the broad extcon
revert as the final fix.

That forward-safe fix was subsequently built and hardware-tested. It allocates
`bnh` with `kcalloc` and adds balanced frees on registration failure and
unregister, while retaining all other 4.14.283 changes. Recovery booted on slot
B. The hardware-tested source is preserved byte-identically in
`/tmp/opencode/sm6150-4.14.283-final-boot-fix` on branch
`wip/odessa-4.14.283-final-boot-fix` at commit `f22e2c86abfb`; only
`drivers/extcon/extcon.c` differs from corrected baseline `6a01c7ef2a18`.
