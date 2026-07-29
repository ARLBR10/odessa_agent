# Moto G9 Plus (`odessa`) LineageOS Bring-up Guide

## Mission

This workspace is for bringing the Motorola Moto G9 Plus (`odessa`) up on the newest LineageOS release that the hardware can support reliably.

The current official LineageOS release is the **starting target, not a promise**. Before selecting a branch, verify the current release on the LineageOS website and verify that the available kernel, vendor blobs, firmware, and common Qualcomm platform code can support it. If the newest release is blocked, document the exact blocker and establish a working intermediate branch first. Do not call an older build the final result without the user's explicit agreement.

The user is new to Android ROM development and C/C++. Work in small, reversible, explained steps. A successful boot is not enough: calls, mobile data, Wi-Fi, Bluetooth, cameras, audio, sensors, encryption, charging, recovery, updates, and emergency-call behavior all matter.

## Project documentation layout

- `MEMORY.md` — durable, extremely important facts and decisions, organized by date. **Read it completely at the start of every session.** Update it only when a verified project fact, decision, blocker, or completed milestone will matter in a future session. Keep it short; it is an index of what matters, not a log.
- `journals/DD-MM-YYYY.md` — detailed per-day records: session work, discoveries, artifact hashes, command results, dead ends. Write specific information here, not in `MEMORY.md`.
- `docs/` — standalone reports, handoffs, and big-bug analyses (e.g., root-cause investigations meant to be read on their own).

Treat all of the above as context, not proof: re-verify device state and other safety-critical facts before any device-changing command.

## Known starting point

- Device: Motorola Moto G9 Plus
- Codename: `odessa`
- Verified model/SKU: `XT2087-1`, Brazil (see `MEMORY.md` for the current verified baseline)
- Platform: Qualcomm Snapdragon 730G / SM7150-family platform, commonly grouped with Motorola `sm6150-common` trees
- Original software generation: Android 10, with an official Android 11 update (`RPAS31.Q2-59-17-4-3-9` is the validated stock restore package)
- Current phone state: bootloader-unlocked, running TequilaOS (Android 14) as the working reference
- TequilaOS source is unavailable. Treat it only as a running reference from which logs, properties, firmware versions, and required proprietary files may be collected.
- Historical LineageOS device/common trees exist. They are evidence and a migration baseline, not proof that a modern branch works unchanged.

Regional variants can differ in NFC, radio configuration, camera modules, partition contents, and firmware. Verify facts on the physical phone before flashing.

## Non-negotiable safety rules

1. The user has accepted full device rewrites and existing data is already gone, so wipe warnings are not required — but every flash can still leave the phone unbootable. Keep a known recovery path before each flash: charged battery, working USB cable/port, host-side platform tools, bootloader access, the correct stock firmware package, checksums, and the written restore procedure (`docs/stock-restore-rpas31-4-3-9.md`).
2. **Ask the user for explicit permission before every `fastboot flash`, `fastboot erase`, or `fastboot format` command**, no matter how routine it seems. State exactly which partition(s) and image(s) are involved, and wait for approval. This also covers equivalent writes issued through recovery or other tools.
3. Never use `dd`, raw block writes, partition-table changes, EDL/QFIL, or bootloader relocking as an exploratory step.
4. Never relock the bootloader while custom images are installed. A mismatched or unsigned image can make the device unbootable.
5. Never flash images from another codename, model, region, or partition layout merely because the SoC is similar.
6. Preserve identity/calibration partitions. Do not modify, publish, or commit modem calibration, IMEI-bearing data, serial numbers, DRM keys, attestation keys, or user data. Examples may include `persist`, `modemst1`, `modemst2`, `fsg`, `frp`, and device-specific equivalents; the actual partition map is in `docs/phase-0-inventory.md`.
7. Proprietary Motorola/Qualcomm binaries may be kept in this repository when that is the practical way to make reproducible builds. Record the source firmware/build and extraction method when known. Never commit device-unique or personal material such as IMEI data, calibration partitions, DRM/attestation keys, serial numbers, accounts, or user data.
8. Do not make Play Integrity, banking apps, DRM, or root-hiding claims without testing on this exact build. Never weaken platform security merely to silence a test.
9. Do not bundle Magisk, Play Integrity bypasses, spoofed fingerprints, leaked keys, or root into the base ROM. First produce and validate an unrooted build.
10. Do not suppress SELinux denials globally, switch production builds to permissive, disable verified boot/encryption, or grant broad permissions as a "fix." Find the correct policy or integration issue.

## Communication rules for agents

- Explain unfamiliar terms on first use. Give the purpose and expected output for device-affecting commands.
- Provide one small command group at a time. Stop at checkpoints and inspect actual output rather than predicting it.
- Never ask the user to paste secrets or complete unredacted logs. Show how to redact serial numbers, IMEI/MEID, phone numbers, accounts, Wi-Fi credentials, Bluetooth addresses, and tokens.
- Preserve raw command output in ignored local artifacts where useful; summarize verified facts in tracked notes or commit messages.
- When a step fails, diagnose it. Do not repeat flashing commands with random flags or substitute an image from a vaguely similar device.
- For Android build commands, give the user the command to ran it. His terminal caching is better than your native tool, plus you have less things to pay attention.
- Inform the user of every change in files in this repo, he has to be able to backtrack your changes. Don't use bash commands to write/add text to files when your native tool (update, write, apply_patch, edit) can do the same.

## Repository rules

The Android source checkout is large. Keep this small project repository focused on manifests, device bring-up changes, extraction tooling, reproducible instructions, and test records.

- Do not commit a full Android source checkout, build output, `ccache`, extracted personal partitions, signing keys, unrelated firmware archives, or host-specific configuration.
- Pin manifests and dependencies to immutable commits when reproducibility matters. Record upstream URLs and revisions.
- Keep device-specific code in the device tree, shared SM6150-family code in the common tree, kernel work in the kernel tree, and proprietary-file declarations/extraction in the vendor tree.
- Reuse the current LineageOS conventions for the selected branch. Do not copy obsolete configuration forward without understanding it.
- Keep patches small and single-purpose. Record what was tested on hardware.
- Do not use prebuilt objects to conceal source/build failures. If a proprietary component is required, identify its source build/firmware and extraction method.
- Proprietary blobs may be tracked for reproducible builds; user-specific data and complete personal partition dumps must remain ignored.
- Don't make changes that might be lost, or untracked, every change in LineageOS repos (outside tracked repos such as Device Tree, Kernel and Vendor) should be able to tracked. In the test instances warn the user about your changes.

### Android project repositories

The Odessa bring-up is maintained as five standalone Git repositories inside the ignored `lineageos/` checkout, plus forks for upstream LineageOS repos that need device fixes (currently `hardware/qcom-caf/bootctrl` via `ARLBR10/android_hardware_qcom_bootctrl`). Keep work on their local `lineage-23.2` branches and commit changes in the repository that owns the affected path:

- `lineageos/device/motorola/odessa`: Odessa-specific product configuration, overlays, and SELinux policy.
- `lineageos/device/motorola/sm6150-common`: configuration and source shared by Motorola SM6150-family devices.
- `lineageos/kernel/motorola/sm6150`: the shared Linux kernel source.
- `lineageos/vendor/motorola/odessa`: generated Odessa-specific proprietary files and vendor makefiles.
- `lineageos/vendor/motorola/sm6150-common`: generated shared proprietary files and vendor makefiles.

The outer project repository does not track these nested repositories because `lineageos/` is ignored. Record their immutable commit IDs in `manifests/odessa.xml` after private remotes are configured. Keep the two vendor repositories private unless redistribution has been reviewed. Their current payload must remain reproducible from the source and SHA-256 recorded in the device trees' `proprietary-files.txt`; never replace generic package files with personal partition dumps.

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
