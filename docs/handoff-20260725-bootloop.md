# Handoff: bootloader solved, Android now bootloops at the zygote handoff

Date: 2026-07-25, early morning

Read `MEMORY.md` first, as always. The two entries dated 2026-07-25 supersede
every earlier root-cause claim. `docs/handoff-20260724-evening.md` and
`docs/xbl-unbootable-root-cause-20260724.md` are now **historical** — their
conclusions were wrong, and `docs/xbl-boot-lun-degraded-state-20260724.md`
records the intermediate step that disproved them.

## The one-paragraph version

The bootloader problem is **solved**. `No valid operating system could be
found` and the recurring near-brick are gone, and their cause is proven: QTI
boot control skipped `xbl`, `xbl_config`, `multiimgoem` and `multiimgqti` when
switching slots, on the upstream premise that UFS selects them via the boot
LUN. That premise is false on this device. MBM switches all 24 A/B partitions
by GPT attribute and never touches the boot LUN. Skipping four of them left a
split boot chain, and MBM responded by refusing to enumerate the partition
table at all. The fix is written and hardware-verified but **not committed**.
Android now boots far enough to complete `post-fs-data` with working
encryption, then dies at the zygote handoff and reboots after ~37 seconds.

## Root cause, proven twice

Measured with `tools/capture-gpt.sh`, not reasoned:

1. `fastboot set_active b` — MBM's own slot switch — sets **all 24** A/B
   partitions to `0x04 active`, including `xbl_b`, `xbl_config_b`,
   `multiimgoem_b`, `multiimgqti_b`, and clears the `_a` copies to `0x00`.
   `running-boot-lun` stayed `2`, so it does not touch `bBootLunEn`.
2. On the failure path, ABL exhausted `boot_b`'s retries, marked it
   `0x80 unbootable`, fell back to slot A, **and flipped `xbl_a` and
   `multiimgoem_a` back to `0x04 active` itself.**

The attribute *encoding* is not the issue — QTI-style `0x3f`/`0x3a` on
`boot_a`/`boot_b` coexisted with a perfectly healthy bootloader.

This retroactively explains every earlier dead end: the original
`0x80`-on-`xbl_b` bug, the later "leave them untouched" fix that also failed,
why `fastboot set_active` always worked, and why firmware sync, AVB flags and
the boot LUN were all irrelevant.

## The fix — WRITTEN, VERIFIED, NOT COMMITTED

Five files behind one Soong config bool, `XBL_SLOT_BY_GPT_ATTRIBUTES`, meaning
"this device selects the XBL chain by GPT attributes, like its bootloader
actually does".

`hardware/qcom-caf/bootctrl` (fork `ARLBR10/android_hardware_qcom_bootctrl`,
on top of `6863795`, working tree dirty):

| file | change |
| --- | --- |
| `1.1/libboot_control_qti/libboot_control_qti.cpp` | `ptn_selected_by_ufs_boot_lun()` returns false under the flag |
| `boot_control.cpp` | same, kept in sync (dead code, but this repo's two-copies trap has already cost two hardware cycles) |
| `1.1/libboot_control_qti/Android.bp` | `-DXBL_SLOT_BY_GPT_ATTRIBUTES` via `select()` |
| `gpt-utils/gpt-utils.cpp` | `gpt_utils_set_xbl_boot_partition()` is a no-op under the flag |
| `gpt-utils/Android.bp` | same `select()` |

`device/motorola/sm6150-common` (on top of `aed760a0`, working tree dirty):
`common.mk` sets `$(call soong_config_set_bool,QTI_GPT_UTILS,XBL_SLOT_BY_GPT_ATTRIBUTES,true)`.

In both `Android.bp` files the **`default:` arm preserves upstream behaviour**,
so an unset variable cannot silently enable the quirk. That is deliberate: the
inverse mistake with `USE_BSG_FRAMEWORK` cost this project a cycle.

**Commit and push both repos, then update the `hardware/qcom-caf/bootctrl` pin
in `manifests/odessa.xml`.** Until then a `repo sync` discards the fix and the
build is not reproducible.

## Current state of the phone

- Slot B holds the LineageOS build from
  `lineage-23.2-20260725-UNOFFICIAL-odessa.zip` (also hardlinked as
  `...-20260724-GPTFIX-TRY2-...`), SHA-256
  `a47ea93a754b10d605a32ab908e67022860c338441b0d24c9631f18f41da8320`.
- Slot A holds stock Android 11 `RPAS31.Q2-59-17-4-3-9`.
- `recovery_a` and `recovery_b` both hold Lineage Recovery. The build with the
  boot-control fix embeds
  `85f22aacfaae987fabc236033d747d1250e8b469902189cdf07790e794f9af05` at
  `/system/bin/hw/android.hardware.boot-service.qti.recovery` — check that
  hash on device before trusting any install result.
- A failed boot now degrades **gracefully**: ABL retries, marks `boot_b`
  unbootable, falls back to slot A. `fastboot set_active b` re-arms it. No
  `gpt.bin` reflash, no Rescue.

## The new problem

Boot sequence on screen: black → Motorola logo → bootloader-unlocked warning →
Motorola logo held ~10–15 s → reset. No LineageOS boot animation. The second
logo is the continuous-splash framebuffer inherited from ABL, so the kernel is
running throughout.

From `/sys/fs/pstore/pmsg-ramoops-0` (saved to ignored
`lineageos/.downloads/pmsg-bootloop-20260725.bin`, 120,589 bytes — contains
device identifiers, never commit unredacted):

**Works.** `apexd` activated APEXes. `vold` generated the "key storage" and
standard storage keys, ran `fscrypt_prepare_user_storage`, and completed
`vold_prepare_subdirs` for `/data/misc_ce/apexdata/...` and
`/data/misc/profiles/cur/0`. `keystore2` reached
`maintenance.rs:287 - await a change to 'apexd.status'`. `odsign`/`odrefresh`
completed: "Boot images on /system OK", "on-device signing done". **FBE and
metadata encryption are functional.**

**Missing.** Zero log lines from `zygote`, `system_server`, `servicemanager`,
`bootanimation`, `installd`, `statsd`. The 120 KB buffer never wrapped inside
its 256 KB zone, so that is the complete userspace log — those processes never
logged at all.

**Why it reboots.** `init.zygote64.rc` has
`critical window=${zygote.critical_window.minute:-off} target=zygote-fatal`,
and `zygote.critical_window.minute=10` **is** set in the build. Four fast
failures triggers the reboot: 4 × ~8 s matches the observed ~37 s cycle.

**Leading hypothesis.** Zygote fails at the dynamic-linker/exec stage. That
output goes to stderr → kmsg, the one buffer that did not survive, which is
consistent with a critical service failing repeatedly while writing nothing to
pmsg. Not proven.

## Checked and eliminated — do not redo

All free, host-side:

- `init.zygote64_32.rc` appears to define only `zygote_secondary`, but it
  **imports `init.zygote64.rc`**, which defines the primary critical `zygote`.
  Not a defect.
- `ro.zygote=zygote64_32`; all three `init.zygote*.rc` files are installed.
- `system/lib/libart.so` missing is **normal** — libart ships in the ART APEX.
- All 13 direct `NEEDED` libraries of `app_process64` resolve, including
  `libnativeloader.so` and `libsigchain.so` from `apex/com.android.art/lib64`.
- The boot ramdisk `fstab.qcom` is correct.
- Boot image and vbmeta are structurally equivalent to the known-booting
  TequilaOS configuration: header v2, 4096-byte pages, embedded dtb, AOSP test
  key, flags 3, rollback index 0.

## Two real defects the log exposed — fix after boot, not before

- `time_daemon` (`QC-time-services`) loops `ats_0`..`ats_15` with
  `genoff_post_init:Error in accessing storage` / `Unable to open file`,
  reading `/mnt/vendor/persist/time/ats_N`.
- `libperfmgr` emits repeated
  `Failed to read Node[N]'s <HoldFd|AllowFailure|WriteOnly|Paths|DefaultIndex>`
  — the Power HAL's `powerhint.json` is not parsing.

Neither is obviously the reboot cause. Do not let them distract from zygote.

## Recommended next step

Stop fighting ramoops and make the failure live-debuggable. The region came
back with roughly 28% single-bit corruption at `ecc: 0/0`,
`console-ramoops-0` did not survive at all, and each capture costs a full
reboot cycle plus a correctly-timed key press. Reed-Solomon with `ecc-size`
corrects a few percent of bytes per block; it will not rescue 28%.

One rebuild, one install:

1. Unset `zygote.critical_window.minute` (its default is `off`) so a zygote
   failure no longer reboots the device. It will sit in a restart loop with the
   system up.
2. Get `adbd` up early. It **never enumerated** during the 37-second window,
   verified with a host-side `adb`/`fastboot` state watcher. This blocks all
   future bring-up and is a bug worth fixing on its own.

Then `adb shell dmesg` and `logcat` read the real reason directly, and this
becomes ordinary iterative debugging instead of one-shot forensics.

## Process lessons that cost real cycles

- **Never force the phone off with the Power key when a kernel log is wanted.**
  Ramoops lives in reserved DRAM. Two captures were lost this way. Catch the
  reset with **Volume Down** into the bootloader, then select Recovery — warm
  the whole way.
- **The boot must actually run and fail.** Going bootloader → Recovery without
  letting a boot attempt happen leaves pstore empty.
- **Verify which binary is under test.** Compare
  `adb shell sha256sum /system/bin/hw/android.hardware.boot-service.qti.recovery`
  against the same path unpacked from the image being flashed. Build timestamps
  do not distinguish builds on this tree.
- **Check the shipping binary, not the convenient one.** `libgptutils.qti` is
  linked *statically*; the `vendor/lib*/libgptutils.qti.so` left in `out/` is
  stale and unused. Verifying it produced a false negative and nearly triggered
  a pointless rebuild.
- **An OTA zip and a separately flashed `recovery.img` can be from different
  builds.** The `GPTFIX` zip embedded the dead-code boot-control binary while
  the flashed recovery had the real fix.
- **In the degraded bootloader state only unsuffixed partition names work**
  (`has-slot:boot: no`), which is why the stock `flashfile.xml` still functions.
- **Recovery shortcut:** `fastboot flash bootloader bootloader.img` from the
  official RPAS31 package restores the partition view and `running-boot-lun`.
  A full Software Fix Rescue is not required.
- Five confident root causes were wrong before measurement settled this. Prefer
  a measurement over a sixth theory.

## Repository state

Uncommitted:

- `hardware/qcom-caf/bootctrl`: five files (the fix above).
- `device/motorola/sm6150-common`: `common.mk`.
- Project repo: `MEMORY.md` updated; `docs/xbl-boot-lun-degraded-state-20260724.md`
  and this file are untracked; `CLAUDE.md` untracked; several `gptcap-*/`
  capture directories are untracked and gitignored.

Nothing has been pushed. The `manifests/odessa.xml` bootctrl pin still points
at `6863795`, which does **not** contain the fix.
