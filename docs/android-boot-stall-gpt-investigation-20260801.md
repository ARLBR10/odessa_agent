# Android Boot Stall and GPT Investigation

Date: 2026-08-01

## Purpose

This report records the investigation after an Android 16 OTA containing the
Odessa BPF version declaration appeared to bootloop or hang at the Motorola
logo. It distinguishes measured facts from unresolved reports and documents
the temporary diagnostic changes now in the source tree.

No device identifiers, raw GPT captures, or raw logs are included. Raw GPT
captures and host USB traces remain only under `/tmp/opencode`.

## Starting symptom

After the user built and installed an OTA containing the corrected
`ro.bpf.kver_override=5.10.239` declaration, the phone did not reach Android.
The user reported two different symptoms at different times:

- an apparent partition-table/slot failure immediately after an OTA install,
  recoverable by restoring the partition table;
- after that restore, a long Motorola-logo hang. A manual power-off was made
  after about 19 minutes.

The initial report was not accompanied by a GPT capture made before the
restore. It must therefore not be described as proven GPT corruption.

## Verified Findings

### BPF declaration

- Recovery on slot A reported `ro.bpf.kver_override=5.10.239`.
- The property is correctly declared through `PRODUCT_SYSTEM_PROPERTIES`, not
  vendor properties. The previous vendor placement was rejected by init due to
  property ownership and caused `netbpfload` to see the literal 4.14 kernel.
- The generic `ro.boot.bootreason=reboot` observed after a forced power-off
  cannot identify the original Android hang.

### Current GPT health

- Read-only captures of every physical GPT copy passed both header and
  partition-entry-array CRC validation.
- The current complete A/B layout is enumerable from Recovery.
- After the partition-table restore, every boot-chain partition was consistently
  A active (`0x04`) and B inactive (`0x00`). `boot_a` carried a normal MBM
  attempt-counter state.
- In an explicitly approved reproduction, rebooting through the bootloader and
  selecting Recovery returned to Recovery normally. Comparing GPT captures
  before and after this transition showed only the expected `boot_a` attempt
  counter decrement. There was no layout change and no other A/B attribute
  change.

This proves the current table is healthy and the current Recovery transition
does not reproduce a persistent GPT mutation. It does not disprove an earlier
post-install failure that was repaired before capture.

### Android hang stage

- During one approved Android reboot, the device disconnected from Recovery and
  exposed Motorola's Android USB device about 41 seconds later.
- It then remained at the Motorola logo without ADB and without a fastboot
  fallback.

This establishes that the observed hang is later than the bootloader and USB
hardware initialization. It is not evidence of a current GPT failure.

### Recovery boot-control integration

- The source checkout uses bootctrl commit `6a85678` (`bootctrl: Match Motorola
  GPT slot attributes on odessa`).
- The generated build rules for both normal and Recovery boot-control components
  include `-DXBL_SLOT_BY_GPT_ATTRIBUTES`.
- The SM6150 common tree sets
  `QTI_GPT_UTILS,XBL_SLOT_BY_GPT_ATTRIBUTES,true`.
- The tested Recovery boot-control service was the intended QTI AIDL service,
  not the historical dead-code implementation.

### First diagnostic OTA

- The first temporary diagnostic build added fsynced markers at post-fs-data,
  BPF start/completion, and zygote start.
- The target-files `boot`, `dtbo`, and `recovery` images exactly match the
  installed B-slot partitions. A retains older images, including the Recovery
  currently being used after the test.
- All first diagnostic marker files were absent from shared metadata when
  Recovery A was reached.
- Current GPT state is normalized to A active and B inactive. That state alone
  cannot determine whether B was never selected or was selected, failed, and
  then fell back to A.

The missing markers do not prove a BPF or zygote failure. If the B-slot image
ran, they place its failure before `post-fs-data`; if it was not selected, the
markers were never under test.

## Source Changes Made

All changes below are temporary diagnostics. They are uncommitted and must be
removed after the blocker is identified.

### `system/core`

- `init/util.h`, `init/util.cpp`
  - Added `WriteFileSync()`, which fsyncs the marker file and its parent
    directory.
  - Added `RecordBootStage()`. It first verifies that `/metadata` is a
    separately mounted filesystem, then writes the short non-sensitive stage
    value to `/metadata/vold/odessa-bootdiag-first-stage`.
  - Marker write failures only log an error and never change boot behavior.
- `init/builtins.cpp`
  - Added temporary `write_sync` for init rc actions.
- `rootdir/init.rc`
  - Records post-fs-data, BPF start, BPF completion, and zygote-start in
    separate marker files.
- `init/first_stage_mount.cpp`
  - Records metadata mount, logical-device creation, system mount start/failure/
    completion, and individual first-stage partition mount transitions.
- `init/selinux.cpp`
  - Records successful SELinux setup before the second-stage exec.
- `init/init.cpp`
  - Records second-stage init entry and completed boot-script loading.

### `system/sepolicy`

- `private/init.te`
  - Grants init only `create_file_perms` for the existing
    `vold_metadata_file` type, replacing its prior `getattr`-only rule.
  - No permissive mode, global denial suppression, or broad metadata access was
    added.

### Project documentation

- `journals/30-07-2026.md` records the verified GPT, USB, slot-image, and
  diagnostic findings.
- This report was added as a standalone handoff.

`git diff --check` passed for the changed outer project, `system/core`, and
`system/sepolicy` worktrees. The extended direct-marker diagnostic has not yet
been compiled or installed.

## Device Actions Taken

No partition image, partition table, or user data was written by this
investigation.

Actions were limited to:

- read-only fastboot slot queries;
- read-only hashes of installed boot, recovery, and DTBO partitions;
- read-only GPT metadata capture in Recovery;
- temporary transfer and execution of `tools/capture-gpt.sh` under `/tmp` in
  Recovery. The script reads only GPT headers and partition-entry arrays;
- approved `adb reboot` and `adb reboot bootloader` observations, with the user
  selecting Recovery Mode.

The user independently flashed a partition-table image to recover from the
reported post-install failure. Its source and exact command were not captured
in this session.

## Open Questions

1. What exactly occurs to GPT attributes immediately after an OTA install and
   before any reboot or restore? A read-only before/after capture around a
   future install is required.
2. Did the first diagnostic OTA select slot B and fail, or did the boot chain
   continue selecting A? The normalized post-fallback state cannot answer this.
3. If the extended first-stage diagnostic runs on the selected target slot,
   which exact `odessa-bootdiag-first-stage` value is retained?
4. If it reaches `boot-scripts-loaded` but not `post-fs-data`, which init action
   blocks before the post-fs-data trigger?
5. If the first-stage marker is absent, did metadata itself fail to mount, or
   does the device reset before the marker can be emitted?

## Next Steps

1. Build the extended diagnostic with:

   ```bash
   source build/envsetup.sh
   lunch lineage_odessa-bp4a-userdebug
   m -j8 init init_first_stage host_init_verifier
   m -j8 bacon recoveryimage
   ```

2. Verify the exact target-files and OTA contain the direct marker strings and
   the intended `write_sync` implementation.
3. Before any installation, capture GPT metadata from the running Recovery.
4. Request explicit user permission before every flash or sideload operation.
5. After installation, capture GPT metadata again before rebooting.
6. If boot fails, return to Recovery without restoring GPT first when possible,
   mount metadata read-only, and read only the exact marker paths.
7. Compare attributes, image hashes, recovery logs, and marker value before
   proposing a correction.

## Follow-up Recovery Inspection

Later on 2026-08-01, a read-only inspection confirmed that the phone was in
slot-A Lineage Recovery 23.2 on `4.14.357-openela-perf+` and that
`ro.bpf.kver_override=5.10.239` was visible there.

- No temporary boot-stage marker or queried `/metadata/bootstat` record exists.
  Because the extended diagnostic has not been built or installed, this absence
  does not constrain the Android failure stage.
- The current Recovery log contains no retained prior-Android, slot-fallback,
  update-engine, AVB, or BPF failure. Its generic boot reason is only `reboot`.
- Recovery's inability to find plaintext F2FS magic on raw `userdata` is the
  expected result of metadata encryption, already established in
  `docs/handoff-20260726-bootloop-observability.md`; it is not evidence that
  userdata is corrupt.
- The backported kernel still boots Recovery. No new evidence justifies changing
  the BPF backport before running the prepared first-stage diagnostic.

No device write or reboot was performed during this follow-up. The raw Recovery
log remains untracked under `/tmp/opencode` because it contains identifiers.

## Extended Diagnostic Artifact Verification

The user then completed both requested build commands successfully. The exact
installable artifact is:

```text
lineage-23.2-20260801-UNOFFICIAL-odessa.zip
size: 1,028,096,263 bytes
SHA-256: 53b76f045cf4c5b0ff73722655a796e5f7ad2473856d75ac6ed618e3b145a674
```

The target-files boot and system init binaries contain all extended stage
strings. The packaged system init RC contains the fsynced post-fs-data, BPF, and
zygote markers; compiled platform policy contains the temporary init access to
`vold_metadata_file`; and `ro.bpf.kver_override=5.10.239` is present only in the
system build property.

Native payload extraction completed for all seven partitions. Extracted boot,
DTBO, product, recovery, system, vbmeta, and vendor images match the target-files
images byte-for-byte, converting sparse product/system images to raw first.

A new read-only pre-install GPT capture has valid primary and backup CRCs on all
captured disks. Slot A is consistently active with Motorola value `0x04`, slot B
is inactive with `0x00`, and `boot_a=0x37` has the normal attempt-counter state.
The raw capture remains untracked under `/tmp/opencode` because GPT metadata
contains device-specific GUIDs.

## Extended Diagnostic Installation Result

With explicit user approval, the exact verified OTA was sideloaded from slot-A
Recovery. Update engine selected slot B, verified all seven target partition
hashes, completed postinstall, and Recovery finished with status 0.

The immediate post-install GPT capture proves that the updater made exactly the
intended complete slot transition: all A boot-chain attributes changed to
`0x00`, while all B attributes, including XBL and XBL config, changed to
Motorola's active value `0x04`. Primary and backup header and entry-array CRCs
remain valid on every captured disk. No unexpected GPT byte-level change was
reported by the decoder.

Installed B boot, Recovery, DTBO, and the 8,192-byte vbmeta payload match the
exact OTA target hashes. This reproduction therefore does not require a
partition-table restore; GPT corruption and incomplete slot switching are ruled
out before the diagnostic Android boot.

## Controlled Slot-B Boot Result

The first reboot was not a valid diagnostic boot because the user restored the
stock partition table after entering fastboot. A post-restore capture is
byte-for-byte identical to the pre-install A-active GPT, so the subsequent stall
ran old slot A.

Motorola MBM's own `fastboot set_active b` was then run with explicit approval.
The exact installed slot-B diagnostic Recovery booted successfully. A controlled
Android B boot exposed Motorola Android USB after 48 seconds but no ADB during a
three-minute observation, and the user returned directly to Recovery B without
another GPT restore.

The initial Recovery marker check was invalid because Recovery does not mount
`/metadata` automatically; it examined the empty ramdisk mount point. After
mounting the metadata partition strictly read-only with `ro,noload`, the retained
markers reported:

```text
odessa-bootdiag-first-stage=boot-scripts-loaded
odessa-bootdiag-post-fs-data=post-fs-data
odessa-bootdiag-bpf-start=bpf-start
odessa-bootdiag-bpf-done=bpf-done
odessa-bootdiag-zygote-start=zygote-start
```

This is the first end-to-end hardware proof that NetBpfLoad completes on the
backported 4.14 kernel. The current blocker is later than BPF and is narrowed to
the `zygote-start` action. Its first blocking command after the marker is
`wait_for_prop odsign.verification.done 1`.

The next minimal diagnostic adds fsynced markers after that property wait and
after the statsd, primary zygote, and secondary zygote start commands. It changes
only `system/core/rootdir/init.rc`; the kernel, BPF backport, and SELinux policy
are unchanged.

## TRY12 Follow-up

TRY12 packaged the follow-up markers and reproduced all seven target-files
partitions exactly from its payload. It installed from B to A with status 0,
successful partition verification, and successful postinstall.

The updater's GPT was CRC-valid and consistently selected A, but the direct
Recovery-A reboot entered fastboot. After the user restored stock GPT and ran
Motorola `fastboot set_active a`, exact TRY12 Recovery A booted. Comparing the
two captures shows only:

```text
boot_a: 0x04 -> 0x3f
boot_b: 0x00 -> 0x02
```

All non-boot slot attributes are identical. This proves the published
`0x04`/`0x00` bootctrl correction generalized too far: Motorola uses those
simple values for XBL and the rest of the chain, but `boot_<slot>` retains the
priority/attempt encoding. A new Odessa-gated source fix implements that hybrid
behavior and is not yet built or hardware-tested.

The controlled TRY12 Android boot stalled again. Read-only metadata markers
showed `odsign-verified`, `statsd-started`, `zygote-primary-started`, and
`zygote-secondary-started`. The blocker is therefore after odsign verification
and after init dispatches both zygote services. The next diagnostic records
later init triggers and service running/restarting transitions.

## TRY13 Follow-up

TRY13's artifact and payload checks passed, and its exact Recovery boot-control
service was bootstrapped on slot A before installation. The A-to-B update
completed with status 0 and wrote target `boot_b=0x3f`, while all non-boot B
partitions received `0x04`.

Automatic Recovery B was not stable. After the user restored stock GPT and ran
Motorola `fastboot set_active b`, the working table differed from the rejected
post-OTA table at exactly one byte:

```text
boot_a: 0x72 -> 0x3a
```

Target `boot_b=0x3f` and every non-boot attribute were already exact. The hybrid
bootctrl fix therefore needs fixed boot values `0x3f` active and `0x3a` inactive;
preserving the old successful bit was wrong. Source now reflects this but is not
yet rebuilt or hardware-tested.

The TRY13 Android diagnostic reached `early-boot` and `boot`. Boot animation ran,
while primary zygote, secondary zygote, and SurfaceFlinger each entered running
and then restarting states. Boot completion never occurred. The remaining
blocker is a userspace crash/restart loop.

The next temporary diagnostic uses Android's stock bounded `logcatd` destination
under encrypted `/data/misc/logd`, then copies only that log to one metadata path
from zygote's existing restart hook. This is intended to capture the actual crash
message without adding insecure USB defaults or broad SELinux bypasses.

## TRY14 Follow-up

TRY14 hardware-verified both sides of the investigation. The corrected bootctrl
values (`boot` active/inactive `0x3f`/`0x3a`, all other A/B partitions
`0x04`/`0x00`) produced a direct automatic target-slot Recovery boot after a
status-0 OTA. The bounded persistent log then exposed the Android blocker.

SurfaceFlinger is not failing because its requested EGLConfig is inherently
unsupported. Its render thread loads the expected Qualcomm userspace driver, but
the driver's first `/dev/kgsl-3d0` open returns `EAGAIN`. The kernel trace shows
`kgsl_open()` calling `adreno_start()`, followed by failed GPU/GMU cleanup. The
earlier initiating message is:

```text
firmware a615_zap.mdt: _request_firmware_load: firmware state wait timeout: rc = -2
subsys-pil-tz soc: qcom,kgsl-hyp: a615_zap: Failed to locate a615_zap.mdt(rc:-11)
```

EGL consequently reports `EGL_BAD_ALLOC`, SurfaceFlinger cannot initialize an
EGLConfig, and its configured restart relationship restarts zygote. The GMU
lowest-idle and GX GBIF halt timeouts are cleanup symptoms, not evidence that
Skia's EGL attribute query is the root cause.

A read-only inspection proved `a615_zap.b00`, `.b01`, `.b02`, and `.mdt` are all
present in the installed slot-A modem firmware image. They were nevertheless not
available to ueventd when KGSL requested them. The next source candidate packages
only those four signed generic firmware files in `/vendor/firmware`, which is
first-stage-mounted and already part of Android's standard ueventd firmware
search path. Exact provenance hashes are recorded in `journals/01-08-2026.md`.

TRY15 builds that candidate. ZIP integrity passes, native payload extraction
reproduces all seven target-files partitions exactly (after sparse-to-raw
conversion for product and system), and the payload vendor filesystem contains
all four files with exact source hashes and `vendor_firmware_file` labels. The
artifact installed with status 0 and exact partition-hash verification.

TRY15 then reached the animated Lineage boot animation without any recurrence of
the ZAP, KGSL, EGL, GMU, or GX errors. The GPU firmware correction is therefore
hardware-verified. Boot still did not complete because SystemServer blocked for
66 seconds in `startMemtrackProxyService()` and watchdog killed it. The declared
HIDL memtrack service repeatedly failed `hw_get_module("memtrack")` with
`ENOENT`; its wrapper was packaged but its legacy implementation was not.

The next source candidate follows upstream LineageOS Xiaomi SM6150 commit
`5f487d934999372a73cab757714e5c1212358a5c`: remove the obsolete HIDL memtrack
packages and device-manifest declaration, then package QTI's AIDL
`vendor.qti.hardware.memtrack-service`, whose module provides the matching init
RC and VINTF fragment.

TRY16 packages that migration correctly. All seven payload partitions reproduce
target-files exactly, the payload vendor filesystem contains the QTI AIDL
binary/RC/VINTF fragment, the obsolete HIDL executable/declaration is absent,
and the previously verified ZAP firmware remains present. Installation completed
with status 0 and exact installed-partition verification. Automatic TRY16
Recovery A booted directly, proving the OTA slot transition without repair.

TRY16 Android no longer blocks in memtrack and reaches `bootAnimationComplete`.
The next blocker occurs during final screen enable: Lineage LiveDisplay queries
declared `IDisplayModes/default`, but the generic SDM service does not register
that interface. The display thread remains in `waitForDeclaredService()` for 60
seconds until SystemServer watchdog kills it. The next source candidate sets
`livedisplay_sdm.enable_dm=false`, matching current Motorola common practice for
panels without QDCM display modes while retaining the SDM Picture Adjustment
interface.

TRY17 packages that capability correction correctly. Its exact payload vendor
declares only `IPictureAdjustment/default`; the unsupported
`IDisplayModes/default` fragment is absent. VINTF returns `COMPATIBLE`, ZIP
integrity passes, and native extraction proves all seven payload partitions
reproduce target-files.

Hardware testing showed that TRY17 advances from Display Modes but blocks on the
remaining `IPictureAdjustment/default` declaration at final screen enable. The
SDM daemon cannot register either interface on this device, and SystemServer is
again watchdog-killed after 60 seconds. The next candidate removes the generic
SDM LiveDisplay package entirely rather than running a daemon with no supported
interfaces.

TRY18 packages that removal correctly: its exact payload vendor has no SDM
LiveDisplay executable, init RC, or device VINTF fragment. VINTF passes, ZIP and
payload properties verify, and all seven extracted payload partitions reproduce
target-files. Hardware testing reaches the LineageOS setup wizard, proving the
LiveDisplay watchdog blocker resolved. The next bring-up issue is independent:
touch input fails in both Recovery and Android, placing it in the shared kernel
touchscreen path rather than framework UI startup.
