# Official Stock Restore Procedure

Package: Motorola `ODESSA_RETAIL_RPAS31.Q2-59-17-4-3-9`, automatically selected for this connected phone by Motorola Software Fix.

This procedure is a recovery fallback. Do not run it merely to test the package.

## Risk classification

**DESTRUCTIVE**

An official Rescue operation replaces the GPT, bootloader, vbmeta, radio, Bluetooth firmware, DSP firmware, logo, boot, DTBO, recovery, and the complete dynamic `super` contents. Motorola's full-flash manifest also erases `carrier`, `userdata`, `metadata`, and `ddr`.

All apps, settings, photos, messages, and files stored only on the phone may be lost. Factory Reset Protection may require the Google account previously associated with the phone during setup.

The manifest does not flash or erase `persist`, `modemst1`, `modemst2`, or the device's identity/calibration partitions. Never add commands for those partitions.

## Prerequisites

- Restoration is actually required because the phone cannot return to the last known-good ROM through a less invasive supported path.
- Ordinary user data and authentication recovery codes are backed up independently.
- Battery is at least 60%.
- A stable known-good USB cable and direct USB port are available.
- The trusted Windows 10/11 host has Motorola Software Fix from Motorola's official support site.
- Software Fix automatically identifies this exact phone; no other model, codename, or manually selected package is accepted.
- The package identity, file count, MD5 manifest, and SHA-256 values match `docs/firmware-validation-rpas31-4-3-9.md`.
- Bootloader fastboot is reachable and reports product `odessa` before starting.
- Google account credentials needed after a factory reset are available.
- The bootloader remains unlocked. Do not relock it as part of recovery.

## Preferred procedure

Use Motorola Software Fix's **Rescue** workflow. Do not translate `flashfile.xml` into an improvised manual fastboot script. The official client controls mode transitions, ordering, sparse transfer limits, and Motorola-specific `fb_mode_set`/`fb_mode_clear` handling.

1. Start Motorola Software Fix on the trusted Windows host.
2. Select Rescue and connect the phone as instructed in bootloader fastboot mode.
3. Confirm Software Fix automatically identifies the phone and selects `ODESSA_RETAIL_RPAS31.Q2-59-17-4-3-9`.
4. Stop if the product, channel, package, or firmware identity differs.
5. Confirm backups, battery, cable, and Google account prerequisites again.
6. Start Rescue only after accepting that the phone will be factory-reset and stock partitions replaced.
7. Keep the cable connected and do not interrupt the host or phone while progress is active.
8. Wait for Software Fix to report **Rescue completed**.
9. Allow the first stock boot to finish; it may take longer than a normal boot.
10. Confirm the stock setup screen, bootloader accessibility, baseband, active slot, and basic radio/Wi-Fi/touch behavior.

## Expected result

- Motorola Software Fix reports **Rescue completed**.
- The phone boots official Android 11 build `RPAS31.Q2-59-17-4-3-9` or the exact build Motorola explicitly substitutes during a newly downloaded Rescue session.
- Stock boot, recovery, vbmeta, firmware, and dynamic partitions are restored.
- Userdata is factory-reset.
- The bootloader is not intentionally relocked.

## Failure handling

If Software Fix fails, record its exact non-sensitive error and stop. Do not retry with random fastboot flags, omit GPT/firmware steps, use the older Android 10 package, erase additional partitions, use EDL/QFIL, or relock the bootloader.

If bootloader fastboot remains reachable, keep the phone in that known recovery mode and diagnose the official client/package failure before another attempt. If Software Fix itself offers a documented retry for the same automatically identified package, use only that official retry path after checking the cable, port, battery, and package hashes.

There is no honest instant rollback once Rescue has rewritten GPT, firmware, and `super`; the accepted stock package is itself the rollback destination. This is why Rescue remains a last-resort recovery operation.
