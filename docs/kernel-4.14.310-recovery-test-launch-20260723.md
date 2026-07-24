# Linux 4.14.310 Recovery Test Result

Date: 2026-07-23

## Source

- Starting hardware-tested branch/commit:
  `wip/odessa-4.14.283-final-boot-fix` at `f22e2c86abfb843192099a3e141c0ce4ca01154a`.
- Authoritative Android-common milestone:
  `9b19b769a59207ac22f4555dfd668fd7c5b8a7e8`,
  `Merge 4.14.310 into android-4.14-stable`.
- Worktree: `/tmp/opencode/sm6150-4.14.310-boot-test`.
- Branch: `wip/odessa-4.14.310-boot-test`.
- Final merge commit: `d3fa64ad9611ea74e514d256d814f20f834e249b`.
- Commit parents: `f22e2c86abfb843192099a3e141c0ce4ca01154a` and
  `9b19b769a59207ac22f4555dfd668fd7c5b8a7e8`.
- Commit tree: `a31297b3d95179c4b4ff30040f03c99d3f31c785`, exactly
  matching the previously built and flashed candidate tree.
- Pushed branch: `origin/wip/odessa-4.14.310-boot-test` at
  `https://github.com/ARLBR10/android_kernel_motorola_sm6150.git`.
- The worktree is clean and synchronized with its upstream. The main kernel
  checkout remains at `41038075962c29364e02cbe5a548904b1f88e028`.

The merge preserves the boundary-valid Qualcomm early-RNG no-sleep behavior,
coherent Qualcomm/Motorola DWC3 implementation, and hardware-tested extcon
allocation fix. Speculative page fault remains disabled. Exact Android-common
4.14.310 `mm/memory.c` and ext4 code are retained. Failed UFS, nodemask, trace,
and mailbox diagnostic reverts and post-4.14.310 behavior are absent. Full
changed/conflict-resolution lists and source provenance are in the ignored
package.

## Build And Package

- Toolchain/build: Android clang r563880c, `LLVM=1 LLVM_IAS=1`,
  `vendor/odessa_defconfig`, `LOCALVERSION=+`, `KBUILD_BUILD_VERSION=310`,
  `-j8`.
- Kernel release: `4.14.310-perf+`.
- Config SHA-256:
  `012f349bd642d2981feceb316df04c24fe14628e62cc38688dd6e86a84f9f54b`.
- Image SHA-256:
  `66115534b78b409dccf9bdadb49a0a252d86aa779a171b33be05ca60b5641509`.
- Read-only ignored package:
  `lineageos/.downloads/diagnostic-recovery-4.14.310-boot-test-20260723/`.
- Recovery SHA-256:
  `aa7be7b89a5906eb2f6a6c5db8ec8bd081163f5e28e2b04d9162a41ad1b4c03a`.
- DTBO SHA-256:
  `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`.
- Vbmeta SHA-256:
  `84d95ae3cda01974feee4c997e6680d76d1e9b4230754798dfa0c723582f198d`.

The established one-variable script was reused byte-identically. Ramdisk,
embedded base DTB, embedded recovery DTBO, external DTBO, header-v2 metadata,
command line, OS metadata, and control images were preserved. `SHA256SUMS.txt`
passed. Recovery and DTBO AVB verification passed. Top-level flags-0 test-key
vbmeta follow-chain verification passed for boot, recovery, DTBO, product,
system, and vendor, including all three hashtrees.

## Device Launch

Immediately before partition writes, fastboot reported `product: odessa` and
`is-userspace: no`. The following and only the following partitions were
written:

- `dtbo_b`: send `OKAY`, write `OKAY`.
- `recovery_b`: send `OKAY`, write `OKAY`.
- `vbmeta_b`: send `OKAY`, write `OKAY`; expected rollback warning
  `0 vs 16` appeared.

`fastboot set_active b` returned `OKAY`. `fastboot reboot recovery` returned
`OKAY`. No `boot_b`, slot-A, firmware, super/dynamic, userdata, or other
partition was written. No rollback or slot-A validation was performed per the
user's instruction.

## Hardware Result

PASS: the user reported that the exact flashed 4.14.310 candidate successfully
booted the Lineage Recovery UI on slot B.

This validates Recovery UI boot for the tested kernel and recovery-control
stack only. Recovery ADB, normal Android boot, slot A, firmware, dynamic
partitions, userdata, and the broader hardware matrix were not tested by this
operation.
