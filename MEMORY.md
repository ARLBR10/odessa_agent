# Project Memory

Extremely important durable facts, organized by date. This is context, not proof:
re-verify device state before any device-changing command.

- `journals/DD-MM-YYYY.md` — detailed per-day records (hashes, commands, dead ends).
- `docs/` — standalone reports, handoffs, and big-bug analyses.
- `OLD_MEMORY.md` — verbatim archive of the pre-2026-07-27 monolithic log. Do not update.

## Current state (as of 2026-07-29)

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
- **Corrected hardware boundary (user-verified 2026-07-28):** exact commit
  `df9da243d122` built and ran on the phone without the later backport commits.
  The aggregate containing `37e035f8c918`, `eb0458ea6a0f`, and the networking
  follow-ups bootloops; those groups have not yet been isolated on hardware.
- **Disproven candidate (2026-07-28):** retaining the later APIs while restoring
  Odessa's defconfig, ARM64 virtual-memory layout, and ARM64 BPF JIT byte-for-byte
  to `df9da243d122` still bootlooped. Those reversions were removed. Two valid
  RX-queue free fixes in `net/core/dev.c` remain; they were not the sole cause.
- **Kernel hardware oracle clarification (2026-07-28):** the user tests each
  kernel by building and flashing a recovery image. The reported failure is a
  pre-Recovery bootloop, before Android or `netbpfload`; do not diagnose these
  kernel candidates from the earlier full-Android bpfloader reboot path.
- **Disproven recovery candidate:** disabling the two boot-time initcalls newly
  added by `37e035f8` in `kernel/trace/bpf_trace.c` still bootlooped; they were
  restored.
- **Current unbuilt recovery candidate:** keep RX queues allocated but mark their
  XDP metadata unused instead of registering every queue during net-device
  creation. This isolates unconditional XDP setup added after `df9da243`; it is
  a recovery diagnostic, not the final XDP design.
- **BPF bootloop isolation resumed (2026-07-29):** the completed backport still
  bootloops before Recovery. A diagnostic with eBPF syscall/JIT/cgroup/classifier
  support disabled boots, and a second diagnostic with the full eBPF core/events
  restored but JIT disabled also boots. This isolates the failure to JIT execution,
  not the verifier, eBPF core, cgroup/classifier, or imported networking core.
  XDP RX-queue registration and `CONFIG_BPF_EVENTS` were separately disabled
  without curing the loop. The next checkpoint compiles the byte-identical Xiaomi
  ARM64 JIT but leaves it default-off (`BPF_JIT_ALWAYS_ON=n`). That checkpoint
  also boots, proving static JIT integration is safe. **Root cause hardware-confirmed:**
  the import omitted `BPF_JIT_DEFAULT_ON`, `ARCH_WANT_DEFAULT_BPF_JIT`, and ARM64's
  select, so `bpf_jit_enable` remained zero while `BPF_JIT_ALWAYS_ON` removed the
  interpreter. Restoring the exact 5.10 Kconfig pieces initializes
  `bpf_jit_enable=1`; the production-config Recovery then booted successfully.
  Published as kernel `56146fa51610`; the matching
  `ro.bpf.kver_override=5.10.239` is published as Odessa `fc7495d29f7a`. The
  manifest pins both immutable revisions, so Repo sync is safe again.
- **Full build verified (2026-07-30):** `m -j8 bacon recoveryimage` succeeds,
  VINTF is compatible, the property is packaged, and native offline application
  of the exact OTA payload reproduces every target partition byte-for-byte. OTA
  SHA-256 is `7fdc68d6e6503b7ca10a40fddbe55ff401b27cfaf84901eaa417e9b68db17a83`.
  Kernel and Odessa changes are published and immutable manifest pins restored.
- **BPF completion hardware-proven (2026-08-01):** a controlled slot-B Android
  boot with fsynced metadata markers reached `boot-scripts-loaded`,
  `post-fs-data`, `bpf-start`, **`bpf-done`**, and `zygote-start`. The complete
  BPF backport and version declaration now pass NetBpfLoad on the phone. The
  active boot stall is later than BPF. TRY12 further proved
  `odsign.verification.done=1` and that init issued starts for statsd, primary
  zygote, and secondary zygote. The next RC-only diagnostic records later init
  triggers and service running/restarting states.
- **Recovery marker-reading rule (2026-08-01):** Lineage Recovery does not mount
  `/metadata` automatically. An absent file under the ramdisk mount point is no
  evidence. Mount the metadata partition read-only with `ro,noload` before
  reading diagnostic files; never expose or copy metadata-encryption keys.
- **First full-Android BPF OTA failure proven (2026-07-30):** preserved ramoops
  reaches NetBpfLoad, then cleanly restarts with `bpfloader-failed`. Init rejected
  `ro.bpf.kver_override=5.10.239` from `/vendor/build.prop` because this is not a
  vendor-owned property, so NetBpfLoad saw 4.14 and enforced its kernel minimum.
  Odessa `properties.mk` now uses `PRODUCT_SYSTEM_PROPERTIES`; rebuild and verify
  the property moves to `SYSTEM/build.prop` before another sideload.
- **Superseded reboot concern (2026-07-30):** the first full OTA sideload to slot A
  completed status 0; update_engine and safe partition hashes all passed. A fast
  reboot cycle initially raised concern about GPT attributes, but later ramoops
  proved Android booted through userspace and deliberately restarted for the
  rejected BPF property above. GPT corruption is not indicated. Report:
  `docs/bpf-backport-jit-root-cause-20260730.md`.
- **OTA slot-attribute correction (2026-08-01, supersedes the claimed complete
  2026-07-29 fix):** the boot chain uses hybrid encoding. XBL and all non-boot
  A/B partitions require Motorola's simple `0x04`/`0x00`, but the target
  `boot_<slot>` requires `0x3f`. Two status-0 OTAs wrote target boot as `0x04`;
  both entered fastboot until the user restored stock GPT and ran
  `fastboot set_active`. Fresh byte-level diffs show MBM changed only target boot
  `0x04→0x3f`. TRY13 proved preserving the old slot's successful bit as `0x72`
  still fails; Motorola's working `fastboot set_active b` changes that sole
  remaining byte to fixed inactive `0x3a`. TRY14 hardware-verified the corrected
  `0x3f`/`0x3a` boot plus `0x04`/`0x00` non-boot implementation with a direct
  automatic target-slot Recovery boot; the fix remains uncommitted and published
  `6a85678788e1` remains incomplete.
- **TRY14 GPU blocker (2026-08-02):** the bounded persistent log
  proves SurfaceFlinger aborts only because Adreno cannot open `/dev/kgsl-3d0`:
  `kgsl_open()` returns `EAGAIN`, then EGL reports `EGL_BAD_ALLOC`. The initiating
  kernel failure is secure GPU firmware loading: `a615_zap.mdt` is not found,
  followed by GMU/GX stop timeouts during `adreno_start()` cleanup. All four
  `a615_zap` PIL files exist in the installed read-only `modem_a` firmware image,
  but are unavailable to ueventd at request time. TRY15 packages them in
  `/vendor/firmware`; ZIP integrity, all seven payload partitions, file hashes,
  SELinux labels, and the hardware result are verified. This fix is uncommitted.
  Exact artifact and firmware hashes are in `journals/01-08-2026.md`.
- **TRY15 hardware result (2026-08-02):** the packaged `a615_zap` firmware fixes
  GPU initialization: no ZAP/KGSL/EGL failure recurs and the Lineage boot
  animation runs. The new blocker is SystemServer waiting for obsolete HIDL
  memtrack; `android.hardware.memtrack@1.0-impl` cannot find a legacy
  `memtrack.<hardware>.so`, then watchdog kills SystemServer after 66 seconds.
  Motorola common now mirrors upstream Xiaomi SM6150 fix `5f487d934999`: remove
  the HIDL manifest/service and package QTI's AIDL
  `vendor.qti.hardware.memtrack-service`. TRY16 hardware-verifies memtrack and
  reaches `bootAnimationComplete`.
- **TRY16 blocker (2026-08-02):** SystemServer reaches final screen enable, then
  LiveDisplay blocks 60 seconds waiting for declared `IDisplayModes/default` and
  watchdog restarts it. The generic AIDL SDM service never registers display
  modes, consistent with this panel exposing no QDCM modes. Motorola common now
  sets `livedisplay_sdm.enable_dm=false` (as current Motorola common trees do),
  retaining Picture Adjustment while removing the unsupported declaration.
  TRY17 is artifact-verified: VINTF is compatible, its exact payload vendor has
  only `IPictureAdjustment/default`, and all seven payload partitions reproduce
  target-files. Hardware testing proves Display Modes was removed, but the same
  watchdog then blocks on `IPictureAdjustment/default`; the SDM daemon registers
  neither interface on this device. The generic SDM package is now removed
  entirely. TRY18 is artifact-verified: VINTF passes, exact payload vendor has no
  SDM binary/RC/device manifest, and all seven payload partitions reproduce
  target-files. **TRY18 reaches the LineageOS setup wizard**, resolving the
  SystemServer/LiveDisplay boot blocker. Touchscreen input does not work in
  either Lineage Recovery or Android, so the active blocker is now the shared
  kernel touch-driver/module/firmware path. Recovery proves the exact panel is
  Novatek `NVT-ts-spi`, but `/proc/modules` is empty and init reports no
  `/lib/modules`; touch modules/firmware were vendor-only while Recovery leaves
  `/vendor` empty. The TRY19 candidate packages both Odessa touch variants,
  dependency, and firmware in Recovery. TRY19 is artifact-verified: exact payload
  recovery has the correct module load/dependency metadata and firmware, all
  seven payload partitions reproduce target-files, and VINTF passes. It is
  installed on slot B but its Recovery returns to bootloader before ADB, including
  when RAM-booted, isolating an early touch-module load crash. The next diagnostic
  packaged all modules/firmware but auto-loaded only `sensors_class`; exact TRY20
  also returns to bootloader when RAM-booted. Thus the touch drivers themselves
  are not yet isolated. Next test: package modules/firmware with an empty
  `modules.load`, then RAM-boot before any further OTA. Exact analysis:
  `docs/try19-recovery-pre-adb-regression-20260803.md`.
- **TRY21 recovery diagnostic artifact-verified (2026-08-03):** Odessa keeps all
  three touch-related modules in Recovery but sets an explicitly empty
  `BOARD_RECOVERY_KERNEL_MODULES_LOAD`. Exact payload Recovery SHA-256 is
  `ff352b4f294a8c902c118a954365ffd32ff0767455bd54f24b7abbd824402aac`;
  its `modules.load` is zero bytes and module/dependency metadata is intact. This
  distinguishes `sensors_class` insertion from merely packaging `/lib/modules`.
  Hardware RAM-boot succeeds and reaches ADB, proving module packaging and image
  size are safe. Manual `insmod sensors_class.ko` fails with
  `Required key not available`; dmesg says its PKCS#7 signature is not trusted.
  This explains TRY19/20: first-stage init treats the rejected listed module as
  fatal. Root cause is stale sccache output for `certs/system_certificates.S`:
  its `.incbin` certificate bytes were absent from the cache key, so the kernel
  embedded an old generated certificate while modules used the current key.
  Kernel `certs/Makefile` now adds the signing-certificate SHA-256 to that
  assembly command; `CONFIG_MODULE_SIG_FORCE=y` remains enabled. TRY22 hardware
  confirms the fix: the runtime key matches the current certificate, both
  `sensors_class.ko` and `nova_0flash_mmi.ko` insert successfully, and Novatek
  registers input `event2` plus IRQ 249. The prior claim that the Novatek blobs
  were aria2 control files was a `file(1)` false positive: the driver parses and
  downloads `novatek_ts_fw.bin` successfully in 84 ms, then reads firmware
  version 3 / PID `601F`. Both extracted files remain byte-identical 139,264-byte
  blobs (SHA-256
  `d9d1f5e88dc0fa90fdd64437e39adac7bf72ad70a8335e339cdb325cec2dab38`),
  The runtime firmware path and Recovery UI touch are hardware-proven working.
  Odessa now restores dependency-ordered automatic Recovery loading for
  `sensors_class`, Novatek, and Focaltech. TRY23 hardware-verifies the no-command
  path both when RAM-booted and after the user installed the update; touch works.
- **Artifact preservation hazard (2026-08-02):** TRY16 through TRY19 filenames
  were hardlinks to the same mutable `lineage_odessa-ota.zip` inode and now all
  contain TRY19 bytes. Recorded historical hashes remain valid evidence, but the
  old files are not preserved artifacts. Future named artifacts must be real
  copies/reflinks with distinct inodes and rechecked hashes.
- **TRY24 radio/audio result (2026-08-04):** neither radio driver was directly
  changed by OpenELA/BPF. Packaging the branch-current vendor mountpoints mounts
  `modem`, `bluetooth`, `dsp`, and `fsg`; Bluetooth is hardware-verified working
  and the user reports audio now works. Wi-Fi remains failed: firmware and board
  data mount and `wlan.ko` registers, but ICNSS has `SERVER_ARRIVE=0` and no
  `wlan0`. Root cause is commit `31eea31c` removing legacy integration while the
  product never inherited `hardware/qcom-caf/common/common.mk`; consequently all
  `/vendor/rfs` links are absent. **TRY25 hardware-verifies the inheritance fix:**
  Wi-Fi works, `wlan0` and `p2p0` exist, and the MSM WPSS/MPSS RFS trees are
  installed. Exact OTA SHA-256 is
  `abbc875d67411b2b197b24392ec8ee939f4bf07c67d058c780090d3d8ce9b1ca`.
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
- Repos live on `lineage-23.2` branches. `manifests/odessa.xml` pins the published
  `ARLBR10` Odessa (`fc7495d`), SM6150 common (`e4b352ff`), BPF-backported kernel
  (`56146fa`), and bootctrl (`6a85678`) commits. The two vendor
  repositories remain local/private and are not manifest projects. Never commit
  logs or captures containing identifiers.
- A 2026-07-29 sync recreated Odessa/common at the old public historical manifest
  pins and caused `lunch` to fail on the obsolete `sepolicy_vndr-legacy-um` path.
  The commits were recovered from their `ARLBR10` branches and the manifest pins
  corrected. Do not restore the historical LineageOS project names/revisions.

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
