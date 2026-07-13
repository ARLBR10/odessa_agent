# Moto G9 Plus (`odessa`) LineageOS Bring-up Guide

## Mission

This workspace is for bringing the Motorola Moto G9 Plus (`odessa`) up on the newest LineageOS release that the hardware can support reliably.

The current official LineageOS release is the **starting target, not a promise**. Before selecting a branch, verify the current release on the LineageOS website and verify that the available kernel, vendor blobs, firmware, and common Qualcomm platform code can support it. If the newest release is blocked, document the exact blocker and establish a working intermediate branch first. Do not call an older build the final result without the user's explicit agreement.

The user is new to Android ROM development and C/C++. Work in small, reversible, explained steps. A successful boot is not enough: calls, mobile data, Wi-Fi, Bluetooth, cameras, audio, sensors, encryption, charging, recovery, updates, and emergency-call behavior all matter.

## Known starting point

- Device: Motorola Moto G9 Plus
- Codename: `odessa`
- Common model seen publicly: XT2087 variants; **verify the exact model/SKU on this phone**
- Platform: Qualcomm Snapdragon 730G / SM7150-family platform, commonly grouped with Motorola `sm6150-common` trees
- Original software generation: Android 10, with an official Android 11 update available in some regions
- Current phone state: bootloader-unlocked/custom-ROM-capable and running TequilaOS
- TequilaOS source is unavailable. Treat it only as a running reference from which logs, properties, firmware versions, and required proprietary files may be collected.
- Historical LineageOS device/common trees exist. They are evidence and a migration baseline, not proof that a modern branch works unchanged.

Verify every fact on the physical phone before flashing. Regional variants can differ in NFC, radio configuration, camera modules, partition contents, and firmware.

## Non-negotiable safety rules

1. **Assume every unlock, format, partition operation, or flash can erase the phone.** Say so before giving the user a command.
2. Never flash until the exact product, SKU, bootloader state, active slot, partition layout, and current firmware are recorded.
3. Never use `fastboot erase`, `fastboot format`, `dd`, raw block writes, partition-table changes, EDL/QFIL, or bootloader relocking as an exploratory step.
4. Never relock the bootloader while custom images are installed. A mismatched or unsigned image can make the device unbootable.
5. Never flash images from another codename, model, region, or partition layout merely because the SoC is similar.
6. Preserve identity/calibration partitions. Do not modify, publish, or commit modem calibration, IMEI-bearing data, serial numbers, DRM keys, attestation keys, or user data. Examples may include `persist`, `modemst1`, `modemst2`, `fsg`, `frp`, and device-specific equivalents; first confirm the actual partition map.
7. Proprietary Motorola/Qualcomm binaries may be kept in this repository when that is the practical way to make reproducible builds. Record the source firmware/build and extraction method when known. Never commit device-unique or personal material such as IMEI data, calibration partitions, DRM/attestation keys, serial numbers, accounts, or user data.
8. Keep a known recovery path before each flash: charged battery, working USB cable/port, host-side platform tools, bootloader access, correct stock firmware package, checksums, and written restore steps.
9. Do not make Play Integrity, banking apps, DRM, or root-hiding claims without testing on this exact build. Never weaken platform security merely to silence a test.
10. Do not bundle Magisk, Play Integrity bypasses, spoofed fingerprints, leaked keys, or root into the base ROM. First produce and validate an unrooted build.

## Communication rules for agents

- Explain unfamiliar terms on first use. Give the purpose, expected output, risk, and rollback for every device-changing command.
- Provide one small command group at a time. Stop at checkpoints and inspect actual output rather than predicting it.
- Mark commands as one of:
  - **HOST ONLY** — cannot alter the phone.
  - **READ ONLY** — queries the phone without intentionally changing it.
  - **DESTRUCTIVE** — can alter or erase the phone.
- For a destructive step, explicitly state:
  - what will change;
  - what data may be lost;
  - the prerequisite backup/checkpoint;
  - the expected success output;
  - how to return to the last known-good state.
- Never ask the user to paste secrets or complete unredacted logs. Show how to redact serial numbers, IMEI/MEID, phone numbers, accounts, Wi-Fi credentials, Bluetooth addresses, and tokens.
- Preserve raw command output in ignored local artifacts where useful; summarize verified facts in tracked notes or commit messages.
- When a step fails, diagnose it. Do not repeat flashing commands with random flags or substitute an image from a vaguely similar device.
- At the start of every session, read `MEMORY.md` for durable facts and decisions from past sessions. Update it when a verified project fact, decision, blocker, or completed milestone will matter in a future session. Treat it as context, not proof: re-verify device state and other safety-critical facts before any device-changing command.

## Repository rules

The Android source checkout will be large. Keep this small project repository focused on manifests, device bring-up changes, extraction tooling, reproducible instructions, and test records.

- Do not commit a full Android source checkout, build output, `ccache`, extracted personal partitions, signing keys, unrelated firmware archives, or host-specific configuration.
- Pin manifests and dependencies to immutable commits when reproducibility matters. Record upstream URLs and revisions.
- Keep device-specific code in the device tree, shared SM6150-family code in the common tree, kernel work in the kernel tree, and proprietary-file declarations/extraction in the vendor tree.
- Reuse the current LineageOS conventions for the selected branch. Do not copy obsolete configuration forward without understanding it.
- Keep patches small and single-purpose. Record what was tested on hardware.
- Do not suppress SELinux denials globally, switch production builds to permissive, disable verified boot/encryption, or grant broad permissions as a “fix.” Find the correct policy or integration issue.
- Do not use prebuilt objects to conceal source/build failures. If a proprietary component is required, identify its source build/firmware and extraction method.
- Proprietary blobs may be tracked for reproducible builds; user-specific data and complete personal partition dumps must remain ignored.

## Work plan

Advance only when the exit criteria for the current phase are met. A later phase must not be used to conceal a failure in an earlier one.

### Phase 0 — Protect the recovery path

Before modifying the phone:

1. Confirm that the user accepts a complete data wipe.
2. Back up ordinary user data independently of Android ROM tooling: photos, files, authenticator recovery codes, contacts, messages where possible, and anything app-specific.
3. Record the exact retail model/SKU, region/channel, bootloader version, baseband, current slot, unlock state, and current build fingerprint.
4. Obtain the correct stock Motorola firmware/restore route for that exact variant. Record its source and checksums. Do not assume a similarly named package is compatible.
5. Confirm that bootloader/fastboot mode is reachable and that the host consistently detects the phone.
6. Record whether the device uses A/B slots, dynamic partitions, `super`, and `fastbootd` from actual command output.
7. Save a redacted baseline report. Keep sensitive raw output local and untracked.

**Exit criteria:** the exact variant is known, the user backup is complete, bootloader communication is reliable, and a credible stock restore procedure exists.

### Phase 1 — Inventory the working device

Use TequilaOS as a behavioral reference, not as an unexplained source tree.

Collect read-only information where available:

- `adb shell getprop` with sensitive values redacted;
- kernel version and command line;
- Android version, vendor security patch level, VNDK level, and build fingerprint;
- `adb shell lshal`, manifest/matrix information, and service lists;
- partition names, sizes, slot suffixes, filesystem types, and dynamic-partition metadata;
- mounted filesystems and encryption state;
- camera IDs/providers, audio devices, sensors, GNSS, NFC, fingerprint, USB modes, and radio/SIM behavior;
- boot/recovery DTB/DTBO information where it can be inspected safely;
- firmware versions and vendor blob provenance.

Capture a baseline hardware test matrix while TequilaOS works. Include both working features and known failures.

**Exit criteria:** there is enough verified information to compare a future build against the current working state without relying on memory.

### Phase 2 — Research and select the baseline

Before cloning hundreds of gigabytes:

1. Check whether `odessa` is currently official on the LineageOS device list.
2. Inspect all historical `odessa`, `sm6150-common`, kernel, and proprietary vendor repositories, including their branches and commit history.
3. Identify the last known booting LineageOS branch and its required Motorola firmware.
4. Inspect sibling devices on the same common platform that already support the desired modern branch.
5. Read the current LineageOS device-support charter and port-submission requirements.
6. Identify Android-version migration gaps: kernel requirements, VINTF, FCM level, vendor interface, AIDL/HIDL transitions, dynamic partitions, recovery, sepolicy, encryption, and camera/audio/radio compatibility.
7. Select:
   - a **known-good baseline branch** for recovery and comparison; and
   - the **target branch** for the actual port.

Do not select a Generic System Image (GSI) boot as the final architecture. It may be useful as a diagnostic only.

**Exit criteria:** a short, evidence-based compatibility plan names the source trees, exact revisions, firmware prerequisite, known-good baseline, target branch, and expected blockers.

### Phase 3 — Prepare the build host

Follow the build-host requirements for the selected LineageOS branch, not an old tutorial.

- Use a supported 64-bit Linux environment.
- Check available disk, RAM, swap, CPU, filesystem, and network before syncing.
- Install only branch-required packages.
- Configure Git identity, `repo`, `ccache`, and a workspace path without fragile permissions.
- Create a pinned local manifest for device, common, kernel, and vendor dependencies.
- Sync with retry/resume rather than deleting a partially valid checkout.
- Verify repository revisions after sync.

Estimate storage from current official documentation and leave substantial headroom for source, object files, multiple builds, and cache.

**Exit criteria:** source sync is complete and reproducible, dependencies resolve, and a generic branch build command can initialize the environment.

### Phase 4 — Reproduce the last known-good build

Where feasible, build the historical known-good `odessa` branch before forward-porting.

- Extract proprietary files from an explicitly recorded source build or from the connected device when technically valid.
- Verify extraction completeness; do not silently accept missing blobs.
- Build without root or integrity modifications.
- Resolve host/build errors before changing device behavior.
- Record artifact hashes and the complete source revision set.

**Exit criteria:** either the historical build completes reproducibly, or the exact irrecoverable dependency/blocker is documented with evidence.

### Phase 5 — Forward-port in reviewable steps

Move to the target branch incrementally. Prefer adapting proven current LineageOS patterns from the same platform over carrying obsolete flags.

Suggested order:

1. manifests, product definitions, and dependency graph;
2. kernel/toolchain and boot image format;
3. partition layout, dynamic partitions, recovery, and fastbootd;
4. vendor blobs, VINTF manifests/matrices, and service declarations;
5. SELinux in enforcing mode;
6. encryption and userdata mounting;
7. radio, audio, Wi-Fi/Bluetooth, camera, sensors, GNSS, NFC, fingerprint, USB, and power/thermal integration;
8. updater and clean-install/upgrade paths.

Build after each coherent change. Treat warnings about VINTF, SELinux, neverallows, missing dependencies, ELF checks, or partition size as defects to understand—not obstacles to bypass.

**Exit criteria:** signed development artifacts build cleanly enough for a controlled first boot, with partition sizes and image layout verified against the physical device.

### Phase 6 — First boot, minimal-risk flashing

Use the least invasive supported boot/test method first. Some devices can temporarily boot an image; others cannot. Verify support rather than assuming it.

Before flashing:

- confirm exact device identity again;
- confirm battery charge and stable USB;
- record current slot and bootloader output;
- verify every artifact hash and size;
- map every image to the correct partition and flashing mode (`bootloader fastboot` versus `fastbootd`);
- ensure the restore package and instructions are locally available.

During first boot, capture host-side logs and, when available, `adb`, recovery, kernel, and ramoops/pstore data. If it fails, return to the known-good slot/image before making another hypothesis.

**Exit criteria:** the phone boots the target build repeatedly, recovery works, encryption state is understood, and logs contain no ignored critical boot failures.

### Phase 7 — Hardware and regression validation

Test from a clean, unrooted installation. At minimum:

- cold boot, warm reboot, shutdown, charging while off;
- lockscreen, PIN/password, file-based encryption, and recovery behavior;
- both slots and update installation, if A/B applies;
- SIM detection, PIN, calls in/out, SMS in/out, mobile data, airplane mode, preferred network types, IMS/VoLTE/VoWiFi where supported by stock firmware/carrier, and emergency-call UI behavior;
- Wi-Fi 2.4/5 GHz, hotspot, Bluetooth pairing/audio/calls, NFC if present, USB data/charging/tethering/ADB;
- earpiece, speaker, microphones, wired/USB audio, volume controls, vibration;
- every rear/front camera, photo/video, flash, focus, rotation, and third-party camera API behavior;
- GPS/GNSS cold and warm fixes;
- fingerprint, proximity, light, accelerometer, gyroscope, compass, and rotation;
- display brightness, adaptive brightness, refresh behavior, touch, and gestures;
- suspend/resume, idle drain, active thermals, charging rate, and battery reporting;
- DRM/security level as an observation, not a promise;
- recovery factory reset, sideload, clean install, and update/rollback procedure.

Keep a table with build hash, firmware version, test steps, result, logs, and unresolved severity. “Seems fine” is not a result.

**Exit criteria:** no blocker remains for boot, encryption, radio, calls, data, Wi-Fi, audio, camera, sensors, recovery, or updates; remaining limitations are explicit and reproducible.

### Phase 8 — Security, signing, and distribution

Only after hardware validation:

- return SELinux to enforcing if development ever required a temporary diagnostic permissive build;
- remove debug-only properties and insecure ADB settings;
- use private release signing keys stored outside the repository, with backups and access controls;
- verify AVB/update behavior appropriate to the device;
- document exact supported firmware, installation, upgrade, recovery, known issues, and artifact hashes;
- before public distribution, identify any proprietary-file licensing or redistribution concerns so the user can make an informed decision;
- compare the result against the current LineageOS device-support charter before considering an official submission.

Never publish personal test builds as “official LineageOS.” Only the LineageOS project can grant official status.

## Play Integrity, Google apps, and root

These are separate concerns and must stay out of initial bring-up.

### Google apps

LineageOS does not generally bundle Google apps. If the user chooses a Google apps package, it must match the Android version and architecture and be installed using the current LineageOS/device instructions. Test the ROM first without optional packages so failures can be attributed correctly.

### Play Integrity

An unlocked bootloader and custom OS can cause one or more Play Integrity verdicts to fail. Results also depend on Google services, device certification, signing, hardware-backed attestation, server-side policy, and changes outside this project. Therefore:

- do not guarantee Play Integrity, Google Wallet, banking apps, or DRM playback;
- record which verdicts are observed on an unrooted release-signed build;
- do not ship fingerprint spoofing, leaked attestation material, keybox replacement, or bypass modules;
- do not trade away SELinux, encryption, verified boot, or update safety for an integrity verdict.

If Play Integrity is mandatory, treat it as an explicit acceptance test after the base ROM is stable. The safe fallback may be stock firmware or a locked, manufacturer-signed OS—not a bypass.

### Magisk/root

Root is optional and unsupported by the base bring-up. After an unrooted build passes the hardware matrix, the user may test the current Magisk release using Magisk's official installation documentation for the actual boot/init_boot layout.

- Back up the exact matching stock/custom boot image first.
- Patch an image from the exact installed build; never reuse a patched image from another build.
- Expect OTA/update behavior and security properties to change.
- Reproduce ROM bugs without Magisk or modules before filing/fixing them.
- Never require root for normal ROM hardware functionality.

## Definition of done

The project is done only when all of the following are true:

- the target is the newest feasible LineageOS branch, and any gap from the current release has a proven technical blocker;
- source manifests and revisions reproduce the build;
- required proprietary files have documented provenance and extraction;
- clean install, boot, encryption, recovery, and update paths work;
- the complete hardware/regression matrix has been run on the exact device variant;
- SELinux is enforcing and no debug security bypass remains;
- stock recovery instructions are verified and available;
- installation documentation is safe for a beginner and includes prerequisites, warnings, expected output, and rollback;
- optional Google apps, Play Integrity observations, and Magisk results are clearly separated from base-ROM support;
- release artifacts are signed appropriately, checksummed, and never labeled official without LineageOS approval.

## First session checklist

The first session should stop after safe discovery. Do **not** flash anything.

1. Explain bootloader, recovery, fastboot/fastbootd, A/B slots, firmware, device tree, kernel, vendor blobs, and ROM in plain language.
2. Confirm the user-data backup.
3. Install/verify `adb` and `fastboot` on the host from a trustworthy source.
4. Record tool versions.
5. With Android booted, collect redacted read-only identity, build, firmware, slot, and partition information.
6. Reboot to the bootloader only after confirming the user understands how to return to Android.
7. Confirm bootloader detection and collect read-only bootloader variables, redacting identifiers.
8. Return to Android.
9. Produce the Phase 0 gap list. The next action is whichever missing recovery prerequisite is safest—not source sync or flashing.

## Authoritative references

Prefer primary, branch-current documentation over forum recipes:

- LineageOS home and announcements: <https://lineageos.org/>
- LineageOS Wiki: <https://wiki.lineageos.org/>
- LineageOS device-support charter: <https://github.com/LineageOS/charter/blob/main/device-support-requirements.md>
- Submitting a device: <https://wiki.lineageos.org/submitting_device>
- Historical Odessa device tree: <https://github.com/LineageOS/android_device_motorola_odessa>
- Motorola SM6150 common tree: <https://github.com/LineageOS/android_device_motorola_sm6150-common>
- LineageOS source and review: <https://github.com/LineageOS> and <https://review.lineageos.org/>
- Motorola kernel sources: <https://github.com/MotorolaMobilityLLC>
- Android platform tools: <https://developer.android.com/tools/releases/platform-tools>
- AOSP build documentation: <https://source.android.com/docs/setup/start>
- Magisk official documentation: <https://topjohnwu.github.io/Magisk/>

Community posts may provide clues, logs, and historical builds, but verify their claims against source and this exact hardware. Never flash an unverified community attachment solely because a post says it supports `odessa`.
