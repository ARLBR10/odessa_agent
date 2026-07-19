# Phase 0 Recovery Checkpoint

No LineageOS image is approved for flashing until every required item below is complete.

## Verified identity

- Device: Motorola Moto G9 Plus (`odessa`)
- SKU: `XT2087-1`
- Retail region: Brazil
- Bootloader: `MBM-3.0-odessa_retail-e69c40c38d6-220629`
- Baseband: `M7150_22.31.04.72R` / `ODESSA_BRLADSDS_CUST`
- Layout: A/B slots with dynamic partitions and `super`
- Bootloader state: unlocked, as reported directly by bootloader fastboot
- Host platform-tools: Google Platform Tools 37.0.0

Re-query these values before any future device-changing operation. Do not rely only on this record.

## Official stock recovery package

Status: **complete**. Motorola Software Fix automatically identified the connected phone and downloaded `RPAS31.Q2-59-17-4-3-9`. All payload hashes and AVB hashes/hashtrees verify; see `docs/firmware-validation-rpas31-4-3-9.md` and `docs/stock-restore-rpas31-4-3-9.md`.

Motorola's current official Software Fix application is Windows-only. It reads the phone identity in fastboot mode and selects the matching firmware using the device IMEI. The IMEI must remain private and must not be pasted into project logs, commits, chat, or screenshots.

Official references:

- <https://pt-br.support.motorola.com/app/softwarefix>
- <https://en-us.support.motorola.com/app/answers/detail/a_id/158726/>
- <https://en-us.support.motorola.com/app/answers/detail/a_id/167770/>

Acquisition checkpoint:

1. Use a trusted Windows 10 or Windows 11 installation.
2. Download Motorola Software Fix only from Motorola/Lenovo's official support page.
3. Connect this exact phone and let Software Fix identify it.
4. Confirm that it reports `XT2087-1`, `odessa`, and the expected Brazilian/RETLA channel before downloading.
5. Select **Download** only. Do not select **Rescue**, **Flash**, or any installation action.
6. Record the displayed package/build, channel, bootloader, and baseband without recording the IMEI or serial number.
7. Make the downloaded and unpacked package available under the ignored `.local/` area for host-side inspection and SHA-256 recording.

The accepted package was selected automatically by the official tool for this exact phone. Its bootloader is newer than the currently installed bootloader, its baseband matches exactly, and its physical/dynamic layout matches the device. The existing Android 10 `QPA30.19-Q3-32-50` package is too old and remains prohibited for flashing.

Motorola states that an actual Rescue operation factory-resets the phone and removes personal data. We are not performing Rescue during package acquisition.

## Android inventory

Status: **complete for currently accessible non-sensitive metadata**. See `docs/phase-0-inventory.md`.

Classification: **READ ONLY**. These commands query Android and do not intentionally modify phone storage.

Prerequisites:

- Android is fully booted.
- The user has accepted the USB-debugging authorization prompt for this host.
- Any raw output retained for later analysis is written only under ignored `.local/` storage.
- Serial numbers, IMEI/MEID, phone numbers, accounts, Wi-Fi credentials, Bluetooth addresses, and tokens are redacted before any summary is tracked.

Completed Phase 0 inventory scope:

- Build, vendor, firmware, slot, encryption, and dynamic-partition properties.
- Partition names, symlink targets, filesystem types, and sizes where permissions permit.
- `lpdump`, boot-mode identity, advertised hardware features, and USB transport behavior.
- No partition contents, raw block reads, calibration data, or identity data.

The broader VINTF, service, sensor, camera, audio, radio, and behavioral collection belongs to the Phase 1 working-device inventory. Permission denials are recorded rather than bypassed.

## Fastbootd checkpoint

Status: **complete** on 2026-07-18. Bootloader fastboot and fastbootd both identified `odessa`, slot `a`; fastbootd reported `is-userspace: yes`. The phone returned to Android afterward.

Classification: **READ ONLY**. This temporarily reboots the phone but does not intentionally flash, format, erase, or modify a partition.

Prerequisites:

- Android inventory is complete.
- Battery is at least 60%.
- USB connection is stable.
- Bootloader fastboot detection and the return-to-Android path are working.
- The user is present to operate hardware keys if necessary.

Procedure goals:

- Reconfirm exact product, SKU, unlock state, current slot, and slot count in bootloader fastboot.
- Enter fastbootd using the supported reboot path.
- Confirm `fastboot getvar is-userspace` reports `yes` in fastbootd.
- Record non-sensitive partition and logical-partition variables.
- Return directly to Android without flashing or erasing anything.

Stop if the host loses USB detection, identity differs from the verified baseline, the phone enters an unexpected mode, or returning to Android is uncertain.

## Recovery checkpoint

Status: **complete** on 2026-07-18. The installed custom recovery booted, exposed ADB after its Enable ADB menu action, and returned to Android using `adb reboot`. No install, sideload, wipe, format, mount change, or partition write was performed.

Classification: **READ ONLY**. This temporarily boots the currently installed recovery and does not intentionally install, wipe, format, or sideload anything.

Prerequisites are the same as for fastbootd.

Procedure goals:

- Identify the installed recovery and record its version/build if displayed.
- Confirm that recovery starts and that the host can detect the device where expected.
- Confirm that the menus for rebooting to Android and fastbootd exist, without selecting factory reset, format, install, sideload, or partition operations.
- Return directly to Android.

## Exit criteria

Phase 0 is complete only when:

- The official exact-device stock package is downloaded, inspected, checksummed, and accepted as current enough.
- Written stock restore steps have been derived from that exact package and reviewed without executing them.
- The non-sensitive partition inventory is complete.
- Fastbootd and recovery behavior are verified.
- The TequilaOS baseline matrix in `docs/tequilaos-hardware-baseline.md` is complete.

Until then, the generated LineageOS OTA remains a host-validated development artifact, not an installation candidate.
