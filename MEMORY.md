# Project Memory

Extremely important durable facts, organized by date. This is context, not proof:
re-verify device state before any device-changing command.

- `journals/DD-MM-YYYY.md` — detailed per-day records (hashes, commands, dead ends).
- `docs/` — standalone reports, handoffs, and big-bug analyses.
- `OLD_MEMORY.md` — verbatim archive of the pre-2026-07-27 monolithic log. Do not update.

## Current state (as of 2026-07-27)

- **Boot blocker, proven end to end:** Android dies at `exec_start bpfloader`;
  `/metadata/bootstat/persist.sys.boot.reason` = `reboot,bpfloader-failed`. Android 16's
  `netbpfload` hard-requires kernel ≥ 5.4 (25Q2); odessa has 4.14.336. Recovery boots
  fine; full Android has never reached zygote on the current kernel.
- **Chosen fix (user decision, 2026-07-27):** stay on 4.14.x — (1) bump to the
  current OpenELA stable level, then (2) apply the *full* BPF backport modelled on
  `LineageOS/android_kernel_xiaomi_sm6150` (same SM7150 silicon, officially
  supported on LineageOS 23.2). The current OpenELA release is **.357**, not .356,
  and .357 is what both reference trees use.
- **Step 1 DONE and build-verified.** `wip/openela-4.14.357` = **4.14.357-openela**
  (21 merges, one per stable release; 2042 commits / 1595 files / +33,089 / −12,307
  over `lineage-23.2`). Builds clean: `m bootimage` succeeded in 7m33s,
  `utsrelease.h` = `4.14.357-openela-perf+`. 13 files were hand-resolved.
- **Step 2 DONE and the kernel LINKS.** `wip/bpf-backport-4.14.357`
  (`295fa6418564`, 7 commits off the bump): the full 5.10 BPF subsystem plus the
  4.15→5.10 networking core the user approved (option A). **3913 objects,
  0 errors, `Image` produced.** 1839 files / +107,368 / −26,147 over
  `lineage-23.2`. `vmlinux` has `btf_new_fd`, `dev_map_alloc`,
  `ringbuf_map_alloc`, `bpf_trampoline_link_prog`; uapi has `BPF_BTF_LOAD`,
  `BPF_MAP_TYPE_DEVMAP_HASH`, `BPF_MAP_TYPE_RINGBUF` — exactly what netbpfload
  gates on. `devmap.c`, which stalled the old branch, builds.
  The older `wip/bpf-backport-4.14.336` is superseded but kept.
- `ro.bpf.kver_override=5.10.239` is now set in
  `device/motorola/odessa/properties.mk` (`7784600`), and
  `CONFIG_BPF_UNPRIV_DEFAULT_OFF` finally takes effect — the symbol was in
  odessa_defconfig but **missing from `init/Kconfig`, so it had silently been
  doing nothing**; the 5.10 entry was added.
- **Never set `ro.bpf.kver_override` on a kernel without the backport.** It is a
  claim about kernel features, not a workaround; alone it only moves the failure
  later (loader takes the BTF path and uses absent map types).
- **NOT yet built through the Android build system and NOT yet on hardware.**
  Next step is `m bootimage` + a boot test: does `exec_start bpfloader` now
  succeed instead of `reboot,bpfloader-failed`?
- **Fallback if the backport fails:** LineageOS 21 (Android 14), the newest branch an
  unmodified 4.14 kernel satisfies. A 5.10/6.x rebase is rejected (no SM6150/SM7150
  BSP exists at any 5.x; vendor blobs are built against 4.14 UAPI).
- **Temporary bring-up hacks that must NOT ship:** uncommitted TRY* bootloop
  diagnostics in `system/core` + `system/sepolicy` + `device/motorola/sm6150-common`;
  disabled `zygote.critical_window.minute`; `persist.logd.logpersistd`/`ro.logd.kernel`;
  AVB vbmeta `--flags 3` (verification/hashtree disabled; matches upstream sm6150-common
  but must be documented as a security limitation); test-key signing.

## Durable operational rules (hard-won, do not relearn)

- Never trust loose `out/target/product/odessa/*.img`. Always use images extracted
  from the exact OTA payload or target-files archive, and confirm extraction finished.
- The boot-control HAL that writes GPT attributes during a sideload is the one in the
  **running recovery**. Flash the new recovery and boot it before testing a bootctrl
  change. Identify the running recovery by hashing the on-device
  `android.hardware.boot-service.qti.recovery` binary — never by build timestamps.
- Before trusting a source change is under test, confirm the file appears in
  `out/soong/build.lineage_odessa.incremental.ninja` (the dead-code bootctrl lesson).
- MBM quirks: unsuffixed `fastboot flash` writes to `_a` regardless of active slot —
  always use explicit suffixes. From the degraded one-slot state, unsuffixed
  `fastboot flash bootloader bootloader.img` (RPAS31 package) restores the partition
  view; a full Software Fix Rescue is not required.
- Persisted properties survive image flashes in userdata (`persist.sys.usb.config`
  trap). When a removed property still misbehaves, factory reset before concluding.
- Ramoops/pstore is not a usable evidence channel on this device: it did not retain
  even a deliberate SysRq panic. Never force power-off with the Power key when any
  boot evidence is wanted — hold Volume Down into the bootloader instead.
- Host stability is suspect (Clang SIGSEGV, Rust LLVM SIGSEGV, single-bit Btrfs
  dirent corruption, all with clean disk counters). Do not trust long unattended
  builds until a memtest86+ run passes.
- **This `repo` checkout is a shallow clone** (269 boundary commits in
  `$(git rev-parse --git-common-dir)/shallow`). A fetched upstream will look
  re-rooted and share no merge base, and `git replace --graft` will silently do
  nothing (it cannot cross a shallow boundary — `git cat-file` honours the graft
  but `git log`/`rev-list` do not). Deepen instead:
  `git fetch --shallow-exclude=<older-tag> <remote> <branch>` then
  `git fetch --deepen=1 ...` to attach the boundary commit. Do not conclude an
  upstream "publishes truncated history" before checking `shallow`.
- **When a merge prints `Resolved '<file>' using previous resolution`, read the
  result.** rerere replays a resolution recorded in a different context and never
  re-justifies it. (At 4.14.346 it produced a `net/core/filter.c` that looked like
  a dropped hunk; it was correct, but only inspection established that.)
- **Never reuse an old branch's work with `git cherry-pick -X theirs`.** Against a
  moved baseline it discards hunks silently, with no conflict reported (it dropped
  the documented `set_vm_flush_reset_perms()` no-op). Instead classify each file by
  whether the baseline moved: identical baseline → take the old result verbatim;
  moved → real 3-way `git merge-file --diff3` against the common base.
- **Kernel-only iteration:** `$SCRATCH/kbuild.sh` builds with `O=` in a scratch dir,
  leaving the Android `out/` untouched — minutes instead of a full `m bootimage`.
  Needs `CLANG_TRIPLE` (not just `LLVM=1`) or the stack-protector check fails, and
  needs `ROCM_PATH`/`HIP_PATH` set to nonexistent paths: this host has `/opt/rocm`,
  and `clang -v` prints a `Found HIP installation:` line that `mkcompile_h` splices
  into `LINUX_COMPILER`, producing an unparsable `compile.h`. That failure looks
  exactly like a source error in `init/version.c` and `include/linux/types.h`.
- **A file missing from a build's error list has not necessarily been built.**
  Make stops in a directory at the first failing object, so later files are never
  reached. Confirm by checking the `.o` exists, not by its absence from errors.
  (Cost a wrong "net/core/filter.c compiles" claim on 2026-07-27.)
- The correct lunch combo is **`lineage_odessa-bp4a-userdebug`**.
- **Backport method that made a 1839-file change tractable:** for each file,
  (1) `git diff v4.14.357-openela HEAD -- <file>` to see what vendor content we
  have, (2) confirm the reference carries it (same Android msm-4.14 lineage, so
  it usually does), (3) import wholesale if yes, else 3-way merge with the
  **upstream tag as base** so conflicts are reported. Helper: `$SCRATCH/merge3.sh`.
  Always re-grep the vendor markers afterwards — don't assume.
- **This tree has `CONFIG_SPECULATIVE_PAGE_FAULT`; the reference reverted SPF.**
  Never import `include/linux/mm_types.h` from it. Likewise never import its
  `time*.h` (y2038 rework cascades into timekeeping), `lib/idr.c` (needs xarray),
  or `kernel/cgroup/cgroup.c` (core PSI/vendor divergence).
- **Resolving stable-merge conflicts: the LineageOS xiaomi sm6125/sm6150 trees are
  the oracle.** They merged the same OpenELA releases into an msm-4.14 vendor tree
  with the same divergences, so `git show reference/sm6125-lineage-23.2:<path>`
  shows how the same conflict was resolved on hardware-validated code.
- Tools in `tools/`: `capture-gpt.sh` + `decode-gpt.py` (GPT attribute diffing),
  `watch-usb.sh` (raw USB enumeration watcher). `/proc/cmdline` contains serial/MACs —
  redact before sharing.

## Verified device and restore facts

- Moto G9 Plus, codename `odessa`, SKU `XT2087-1`, Brazil. A/B slots + dynamic
  partitions, `super` = 9,730,785,280 B. Bootloader `securestate: flashing_unlocked`.
  Partition/LUN map and firmware details: `docs/phase-0-inventory.md`.
- Stock restore: official Motorola Software Fix package `ODESSA_RETAIL
  RPAS31.Q2-59-17-4-3-9` (Android 11), auto-selected by Software Fix for this exact
  device, fully hash/AVB-validated. Procedure: `docs/stock-restore-rpas31-4-3-9.md`.
- Proprietary blobs come solely from the exact installed TequilaOS payload ZIP
  (SHA-256 `2eebc8ee17bcbc3a28d96b7b1dbf1b6769c6281d437194fbf582f0e2b365fdb6`);
  lists revalidated with zero missing/mismatched files.
- Repos live on `lineage-23.2` branches; forks under `ARLBR10` (kernel, bootctrl).
  `manifests/odessa.xml` pins the bootctrl fork; the five device/kernel/vendor repos
  still pin public historical commits — update only after private remotes carry the
  new commits. Never commit logs or captures containing identifiers.

## Per-day key facts

- **2026-07-12** — Device identity/layout verified (odessa, XT2087-1, TequilaOS A14,
  4.14.190-Amber, slot A, A/B + dynamic partitions, unlocked). Host adb/fastboot OK.
  Android 10 stock package judged too old and untrusted — inspection only.
- **2026-07-13** — lineage-23.2 (Android 16) source synced; blobs extracted from the
  exact TequilaOS payload; `lunch` and `m bootimage` succeed.
- **2026-07-14** — First full target-files attempt OOM-killed; GPS/sched/fingerprint/
  gpt-utils fixes; rerun constrained (`m -j8`), preserve `out/`.
- **2026-07-15** — Soong JSON fix (unquoted `TARGET_RECOVERY_PIXEL_FORMAT`);
  legacy `PRODUCT_BUILD_PROP_OVERRIDES` migrated to `DeviceProduct`/`BuildDesc`/
  `BuildFingerprint`.
- **2026-07-16** — Pre-build review fixes committed (lights HAL, FPC SELinux, GNSS
  battery listener, stale services, vbmeta flags-3 removal). Power HAL ported to
  Android 16 libperfmgr APIs.
- **2026-07-17** — sccache via wrapper `/home/arthu/bin/sccache-android` (never point
  `CCACHE_EXEC` at sccache directly). First transient Clang SIGSEGV with USB UAS reset.
- **2026-07-18** — Kernel genuinely updated to Android-common 4.14.336 (FCM 6 minimum);
  VINTF COMPATIBLE; first full target-files + A/B OTA built (test keys, not flashable).
  Phase-0 inventory done (fastbootd, recovery, partition map).
- **2026-07-19** — Official Android 11 RPAS31 package validated → accepted restore
  route. User's first sideload (with GApps+Magisk, wrong procedure) looped and fell
  back. Kernel bisection begins: recovery-only slot-B tests are the oracle;
  4.14.190 boots, 4.14.336/4.14.317 loop. 16 of 19 A/B firmware partitions differ
  (later eliminated as a cause).
- **2026-07-20** — Bisection: 4.14.254 boots; 4.14.282 and 4.14.286 loop.
  WIP debug branches published to `ARLBR10`.
- **2026-07-21** — 4.14.283 reproducible FAIL; the .282→.283 source delta alone is not
  the cause (header-propagated object changes matter).
- **2026-07-22** — Recovery-USB root cause: the generic DWC3 gadget import replaced
  the Motorola/Qualcomm integration. Restoring `core.c`+`gadget.c` from 4.14.254 fixes
  Recovery ADB on 4.14.282 (commit `0625428fb4ec`).
- **2026-07-23** — Bootloop root cause: stable `6e721f3a` (extcon registration order)
  + Motorola's `devm_kzalloc` `bnh` before registration; fixed by explicit `kcalloc`
  (commit `f22e2c86`). 4.14.310 and 4.14.336 recovery PASS; merged to `lineage-23.2`.
  Separate 4.14.310→336 Recovery-ADB regression: DWC3 suspended-event path dropped
  (`5be9b397181c`). AIDL BootControl migration done (`496a793c`).
- **2026-07-24** — OTA installs status 0 but slot won't boot. After three disproven
  theories, proven: **odessa selects the XBL chain by GPT attributes, not the UFS boot
  LUN** — QTI bootctrl must not skip xbl/xbl_config/multiimgoem/multiimgqti. First fix
  landed in dead code (`boot_control.cpp`); real target is
  `1.1/libboot_control_qti/`. Btrfs ghost dirent blocked a build (host RAM suspect).
- **2026-07-25** — XBL-by-GPT-attributes fix (`XBL_SLOT_BY_GPT_ATTRIBUTES`, bootctrl
  `6024c10`, common `f64cb3e5`) pushed and manifest-pinned: bootloader accepts the
  slot, graceful fallback, near-brick eliminated. New problem: Android bootloops.
  Bisected: `persist.sys.usb.config=adb` (composes the gadget in full Android) breaks
  boot; stale persisted value in userdata misled one retest. Firmware/slot
  differences eliminated.
- **2026-07-26** — TRY1–TRY9 metadata-marker diagnostics (ramoops proven useless).
  **Breakthrough: boot dies at `exec_start bpfloader`**; everything through
  post-fs-data (FBE, keystore, apexd, odsign) completes.
- **2026-07-27** — Root cause proven: `reboot,bpfloader-failed`; netbpfload requires
  4.19 (V) / 5.4 (25Q2), kernel is 4.14.336. `ro.bpf.kver_override` alone is NOT a fix
  (BTF/DEVMAP_HASH missing). BPF backport scoped and started
  (`wip/bpf-backport-4.14.336`); 26/32 objects compile; `devmap.c` XDP infra is the
  next port. Reference: `reference/sm6125-lineage-23.2` in the kernel repo.
  Strategy then fixed by the user: OpenELA bump first, then the full BPF backport
  from xiaomi sm6150. Bump completed on `wip/openela-4.14.357` (4.14.336 →
  4.14.357-openela, 21 merges, 13 files hand-resolved). Remotes added to the kernel
  repo: `openela` (github.com/openela/kernel-lts) and `xiaomi6150`. Full conflict
  table and the shallow-clone diagnosis are in `journals/27-07-2026.md`.
