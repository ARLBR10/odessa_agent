# SM6150 Kernel Range Review 2026-07-20

This is a host-only source review. No phone command, flash, boot, sideload, or
partition operation was performed for this review.

## Reviewed range

- Repository: `lineageos/kernel/motorola/sm6150`
- Base: `92a96be148a072185131f60977af463c918b58cd`
- Tip: `41038075962c29364e02cbe5a548904b1f88e028`
- Base subject: `sm6150: Fix fingerprint and hardening issues`
- Tip subject: `random: Avoid scheduler sleep during early Qualcomm init`
- Commits in range: 288
- Files changed: 6,268
- Insertions: 78,697
- Deletions: 54,419
- File status: 6,168 modified, 46 added, 54 deleted

The range is dominated by an Android Common Kernel stable update. It should not
be treated as one Odessa-specific patch.

## Commit structure

The effective review boundary is:

1. `92a96be148a072185131f60977af463c918b58cd..70f404ff7c1f`: upstream and
   Android Common Kernel changes.
2. `98efff6a92e3`: Odessa-relevant PMD/PUD page-table backport.
3. `b9df0469a7a2`: Odessa FCM 6 kernel configuration changes.
4. `41038075962c`: Qualcomm early-RNG scheduler-sleep change.

The merge commit `70f404ff7c1f` brings the kernel from Linux `4.14.190` to
Android Common Kernel `4.14.336`. Its second parent is the Android Common
Kernel `4.14.336` merge, and its first parent is the reviewed base.

## Upstream stable update

The upstream portion changes 6,265 files, with 78,410 insertions and 54,371
deletions. It updates broad kernel subsystems rather than adding Odessa device
logic:

- ARM, arm64, x86, MIPS, PowerPC, RISC-V, Xen, and KVM code.
- ext4, btrfs, f2fs, NFS, nilfs2, UDF, block, and memory-management code.
- IPv4, IPv6, netfilter, Bluetooth, Wi-Fi, USB, Xen networking, and XFRM.
- Qualcomm, GPU, MMC, storage, audio, media, power, and thermal drivers.
- Kernel hardening, Spectre/SRSO mitigations, SELinux, IMA, AppArmor, and
  cryptographic code.
- `perf`, selftests, build scripts, documentation, and developer tooling.
- New Blake2 crypto implementation and NCSI support.
- Removal of DECnet, obsolete drivers, and old emulator configurations.

Notable upstream file operations include:

- Added Blake2 implementation files under `crypto/` and `lib/crypto/`.
- Added NCSI netlink files under `net/ncsi/`.
- Added XFRM compatibility support in `net/xfrm/xfrm_compat.c`.
- Removed DECnet files under `net/decnet/` and related headers.
- Removed the obsolete `drivers/block/sx8.c` driver.
- Removed old Ranchu/Goldfish configurations and several obsolete headers.
- Added kernel warning-count ABI documentation, ext4 directory documentation,
  hardware-vulnerability documentation, perf tests, and selftest helpers.

## Odessa-specific change 1: PMD/PUD page-table moves

Commit: `98efff6a92e3af5294ce48ed4cd020691a14ce29`

Files changed:

- `arch/Kconfig`
- `arch/arm64/Kconfig`
- `arch/arm64/include/asm/pgtable.h`
- `mm/mremap.c`

Effective behavior:

- Adds `HAVE_MOVE_PMD` and `HAVE_MOVE_PUD` architecture capabilities.
- Enables both capabilities for arm64.
- Adds arm64 `set_pud_at()` support.
- Extends `mremap()` to move normal page tables at PMD and PUD granularity.
- Keeps separate handling for normal PMDs, transparent huge PMDs, and normal
  PUDs.
- Removes the previous `LATENCY_LIMIT` restriction from the page-table move
  loop.

Review status:

- No definite correctness defect was found by source inspection.
- This is a substantial memory-management backport and requires an arm64
  kernel build plus runtime testing of `mremap()`, memory pressure, and large
  mappings before it is considered validated on Odessa.
- The larger movement extents can change scheduling and latency behavior even
  though the operation remains functionally equivalent in the normal case.

## Odessa-specific change 2: FCM 6 defconfig

Commit: `b9df0469a7a2d7dbce8e6795d035088c4bbe6f85`

Files changed:

- `arch/arm64/configs/vendor/odessa_defconfig`
- `drivers/gpu/msm/Kconfig`

Configuration changes:

- Enables `CONFIG_UTS_NS`.
- Enables `CONFIG_BPF_JIT` and `CONFIG_BPF_JIT_ALWAYS_ON`.
- Enables `CONFIG_USERFAULTFD`.
- Enables `CONFIG_ARM64_SW_TTBR0_PAN`.
- Enables `CONFIG_XFRM_MIGRATE`.
- Enables `CONFIG_DM_SNAPSHOT` and `CONFIG_VETH`.
- Enables `CONFIG_SONY_FF`.
- Enables `CONFIG_ANDROID_BINDERFS`.
- Enables ext4 POSIX ACL support.
- Enables `CONFIG_FS_VERITY` and `CONFIG_FS_VERITY_BUILTIN_SIGNATURES`.
- Enables `CONFIG_DEBUG_LIST`.
- Enables static usermode helper support with an empty helper path.
- Enables `CONFIG_CRYPTO_CHACHA20POLY1305`.
- Disables `CONFIG_RT_GROUP_SCHED`.
- Disables `CONFIG_SPECULATIVE_PAGE_FAULT`.
- Makes the Qualcomm KGSL driver select `TRACE_GPU_MEM`.

Review status:

- The settings match the general pattern already present in sibling Qualcomm
  vendor defconfigs in this kernel tree.
- They still require full kernel configuration validation, target-files VINTF
  validation, SELinux validation, and hardware testing.
- Enabling an interface does not prove that the Android userspace integration
  or device behavior is complete.

## Odessa-specific change 3: early Qualcomm RNG scheduling

Commit: `41038075962c29364e02cbe5a548904b1f88e028`

Files changed:

- `drivers/char/hw_random/core.c`
- `drivers/char/random.c`
- `drivers/net/wireless/ath/ath9k/rng.c`
- `drivers/soc/qcom/early_random.c`
- `include/linux/random.h`

Effective behavior:

- Adds a `sleep_after` argument to
  `add_hwgenerator_randomness()`.
- Normal hardware-RNG and ath9k callers pass `true`, preserving throttling.
- Qualcomm `early_random` passes `false`, preventing scheduler sleep during
  early Qualcomm initialization.
- All callers in the tree were updated to the new function signature.

Review status:

- No caller/signature mismatch was found.
- The change is narrowly scoped and does not alter the entropy data supplied by
  the Qualcomm early-RNG path.
- Runtime validation should confirm early boot completion and later RNG
  readiness on the actual device.

## Findings and decision

No definite source-level correctness bug was identified in the three
Odessa-specific commits.

The following remain open validation risks:

- The PMD/PUD `mremap()` backport is not proven correct on the Snapdragon 730G
  workload until compiled and exercised on arm64 hardware.
- The new FCM configuration enables several security and runtime interfaces
  that require userspace, VINTF, SELinux, and hardware validation.
- The complete range combines 285 upstream stable commits with three
  Odessa-specific commits, making future regression diagnosis harder if they
  are treated as a single change.

## Verification performed

- Read-only Git history and range statistics were inspected.
- All changed paths were enumerated.
- The three Odessa-specific commit diffs were inspected file by file.
- All `add_hwgenerator_randomness()` callers were checked for the new argument.
- `git diff --check` passed for the reviewed range.

No kernel rebuild or device runtime test was performed as part of this review.
