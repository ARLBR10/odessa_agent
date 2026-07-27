# Handoff: bootloop is inside first-stage mounting; rebuild corrected TRY9

Date: 2026-07-26

Read `MEMORY.md` first. This handoff supersedes
`docs/handoff-20260726-bootloop-observability.md` as the next-action guide.
The XBL/GPT boot-control fix remains correct and is not under investigation.

## One-paragraph state

The phone still bootloops, but the failure is now localized before normal
Android init rc actions. TRY5 proved `zygote-start` was not reached. TRY6 and
TRY7 found no stage file, but their evidence was limited by durability and rc
execution. TRY8 put a direct, fsynced marker in first-stage init immediately
after `DoFirstStageMount()`; the exact payload contained that marker, yet it was
absent after all slot-A retries. Therefore normal first-stage mounting never
completes. Corrected TRY9 instruments device/logical setup, system-as-root, and
every remaining first-stage partition after metadata is mounted. The latest
target-files archive was built before one final correction that prevents a
generic outer marker from overwriting the exact failure. **Do not generate or
install TRY9 from that stale archive. Rebuild from the current source first.**

## Current phone state

- The phone is in slot-B Lineage Recovery with ADB enabled.
- Recovery reports `ro.boot.slot_suffix=_b` and battery capacity 100%.
- Slot A exhausted all retries during TRY8 and is unbootable.
- Slot B remains the recovery/fallback path.
- The bootloader partition view remained healthy throughout these tests.
- `/metadata` is not mounted now.
- Both slots contain LineageOS-family diagnostic builds; there is no stock slot.
- The accepted stock recovery route remains the exact-device RPAS31 package.
- Do not factory-reset, re-arm A manually, boot Android, or flash loose images.

The user has authorized routine `adb`, `fastboot`, and focused `getvar`
commands. Every new sideload still requires the normal destructive warning and
explicit authorization.

## Immediate next action

The current source has the corrected TRY9 instrumentation, but the package is
stale by one line. From `lineageos/`, the user should run:

```sh
m -j8 init_first_stage
m -j8 target-files-package
```

Do not use `mka otapackage` for this diagnostic. Generate the OTA only from the
exact newly inspected target-files archive so target-to-payload provenance is
explicit.

After the build:

1. Hash and ZIP-test
   `out/target/product/odessa/obj/PACKAGING/target_files_intermediates/lineage_odessa-target_files.zip`.
2. Confirm `BOOT/RAMDISK/init` contains these strings:
   `first-stage-device-creation-failed`, `first-stage-devices-created`,
   `first-stage-system-mount-start`, `first-stage-system-mount-failed`,
   `first-stage-system-mounted`, `first-stage-mount-start:`,
   `first-stage-mount-failed:`, and `first-stage-mounted:`.
3. Confirm `BOOT/RAMDISK/init` does **not** use a generic outer
   `first-stage-mount-failed` marker after `DoFirstStageMount()` returns false;
   that marker was removed because it overwrote the useful specific result.
4. Generate `lineage-23.2-20260726-BOOTLOOP-TRY9-UNOFFICIAL-odessa.zip` with
   `out/host/linux-x86/bin/ota_from_target_files` from that exact archive.
5. ZIP-test and hash the OTA and payload. Extract at least `boot` and prove its
   ramdisk init contains the exact markers above. Compare payload boot to the
   target-files boot byte-for-byte.
6. Only after explicit destructive authorization, sideload from recovery B to
   target A. Pull `/tmp/recovery.log` before reboot and require status 0.
7. Boot A, catch the reset/fallback in Motorola fastboot, then boot recovery B.
8. Enable ADB, mount metadata read-only, read only
   `/metadata/vold/bootloop-stage`, and unmount metadata immediately.

Interpret the stage literally:

- No file: failure occurred before metadata became usable in
  `DoCreateDevices()`, or metadata itself could not mount.
- `first-stage-device-creation-failed`: metadata may have mounted, but required
  device/logical-partition creation failed.
- `first-stage-devices-created`: device/logical setup completed; failure
  occurred before the first mount-specific marker.
- `first-stage-system-mount-failed`: `TrySwitchSystemAsRoot()` failed.
- `first-stage-mounted:/vendor` or `/product`: that partition mounted; the next
  operation failed or reset.
- `first-stage-mount-failed:/vendor` or another path: exact partition mount
  failure.
- `first-stage-mounts-complete`: all normal first-stage mounts completed; this
  would contradict TRY8 and move the investigation to SELinux setup.

Do not list `/metadata/vold`; query only the exact stage path.

## Why TRY9 is needed

`fstab_dynamic.qcom` orders first-stage entries as system, vendor, product, then
metadata. However, current AOSP `DoCreateDevices()` explicitly mounts metadata
before creating logical partitions because snapshot state may live there. This
means a marker can survive while system/vendor/product mounting is still in
progress.

TRY8 wrote only after `DoFirstStageMount()` returned success. Its absence proved
that the whole operation did not complete but could not identify the failed
substep. TRY9 records:

- failure/success of `DoCreateDevices()`;
- start/failure/success of `TrySwitchSystemAsRoot()`;
- start/failure/success of each remaining first-stage partition mount;
- later SELinux, second-stage, boot-script, post-fs-data, BPF, and zygote stages
  if first-stage mounting succeeds unexpectedly.

All stage writes use `WriteFileSync()`, which fsyncs both the marker and its
parent directory. Fast warm resets can no longer explain an absent marker.

## What this session proved

### TRY4 and TRY5

- TRY4's zygote `onrestart` log copy produced no metadata log.
- TRY5 added `zygote-start` and restart markers. All were absent.
- Therefore the active failure was before `zygote-start`, not a zygote linker
  or restart failure.

### TRY6 and TRY7

- TRY6 added one stage file across post-fs-data/BPF/zygote checkpoints, but the
  ordinary init `write` builtin does not fsync regular files.
- TRY7 added `write_sync`, and exact payload verification proved system init and
  rc files contained it.
- TRY7 still produced no stage file. Bootstrap review confirmed first-stage
  ramdisk init execs `/system/bin/init` for SELinux and second stage, so the
  system binary with `write_sync` was the correct parser.

### TRY8

- TRY8 added direct fsynced markers in first-stage init, SELinux setup,
  second-stage entry, and after boot-script parsing.
- Exact payload boot and raw system were byte-identical to target-files.
- Exact payload ramdisk init contained `first-stage-mounts-complete`.
- TRY8 installed with status 0, exhausted slot A, and left no stage file.
- Therefore `DoFirstStageMount()` did not complete.

## Last verified artifacts

These are historical evidence, not the next install package.

TRY8 target-files:

```text
size: 2,614,937,918 bytes
SHA-256: 4363aa046e000f7d07d865d2a173a198498314977e3901218d130840269fc513
```

TRY8 OTA:

```text
size: 1,028,478,895 bytes
SHA-256: 2bc9ffae66dedc07108da7307081ef6e394b273bd997d4378ec04cd7bb15a7ee
payload SHA-256: 7f0b0c6158400759eed62b3fb02f8cfe2e9f58c7a308d2acf7d9ea21b289d3ef
```

TRY8 recovery log:

```text
lineageos/.downloads/recovery-slotb-try8-20260726.log
SHA-256: ffca11679ddf7f9685939091b20cf58e0a6b51f291b3327419d16ac0784bce66
```

The recovery log is sensitive and must remain ignored and unquoted.

The most recent pre-correction TRY9 target-files checkpoint is also historical
only:

```text
size: 2,614,941,963 bytes
SHA-256: 2ce942af970158f9693d8fea9a2cb8d24843bd8bf8f716220d31c9a52d982ca2
```

It is superseded because the source now omits the generic overwrite marker.
Do not generate an OTA from it.

## Temporary source state

Uncommitted diagnostic changes exist in:

- `system/core/init/builtins.cpp`
- `system/core/init/first_stage_init.cpp`
- `system/core/init/first_stage_mount.cpp`
- `system/core/init/init.cpp`
- `system/core/init/selinux.cpp`
- `system/core/init/util.cpp`
- `system/core/init/util.h`
- `system/core/rootdir/init.rc`
- `system/core/rootdir/init.zygote64.rc`
- `system/sepolicy/private/init.te`
- `device/motorola/sm6150-common/properties.mk`
- `device/motorola/sm6150-common/rootdir/etc/init.target.rc`

`git diff --check` passes in all three repositories after the generic-marker
correction. Do not commit these diagnostics. Remove them after the boot blocker
is identified and fixed. Restore the production zygote critical-window property
before any release build.

The outer project has unrelated pre-existing tracked and untracked files. Do
not clean, revert, or commit them wholesale.

## Closed paths

Do not reopen these without new evidence:

- XBL/GPT attribute handling: fixed and hardware-verified.
- GPT corruption: never occurred; CRCs and ranges remained valid.
- UFS boot-LUN theory: disproven.
- Slot firmware asymmetry: disproven by same-build tests on both slots.
- AVB flags and signing-key format: disproven.
- Dynamic-partition sizing: fastbootd metadata and OTA verification are healthy.
- USB gadget debugging: separate persisted-property regression, not the original
  failure.
- Ramoops/pstore: deliberately panicked recovery still retained nothing.
- Recovery userdata decryption: unavailable and not a small fix.
- Zygote linker/restart: current failure happens earlier.

## Operational rules

- Never flash loose boot, DTBO, vbmeta, or dynamic images for this diagnosis.
- Never use mutable `out/*.img` as provenance; inspect target-files and exact OTA
  payload images.
- Always pull recovery logs before rebooting after sideload.
- Never use `adb wait-for-device`; use bounded direct queries.
- Do not force-power-off when evidence may be in RAM, though current markers are
  fsynced to metadata.
- Do not expose raw recovery logs, `/proc/cmdline`, serials, MAC addresses,
  metadata keys, or other identifiers.
- Do not build as the agent. Give the user constrained build commands; their
  shell has the configured sccache environment.
