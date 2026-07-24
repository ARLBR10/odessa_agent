# First Install Checkpoint

Status: **firmware comparison complete; device-changing procedure not yet approved**.

This document records the intended installation architecture, the completed read-only firmware comparison, and the remaining review gate. It is not permission to flash, wipe, format, or sideload the phone.

## Intended installation architecture

- Odessa has separate 64 MiB A/B `recovery` partitions. Recovery is not embedded in `boot`.
- The standalone Lineage Recovery candidate is `lineageos/out/target/product/odessa/recovery.img`, 67,108,864 bytes, SHA-256 `dd4e3350ac92278b42a7db13bbc2f778898a923b09ab48b6d1368886272c2d26`.
- The installable ROM is an A/B payload OTA for `pre-device=odessa`: `lineageos/out/target/product/odessa/lineage-23.2-20260719-UNOFFICIAL-odessa.zip`, 1,028,374,656 bytes, SHA-256 `65d3a91433e470899f79c75386e771bd6d84b3d4cde28f0a06a7d0dd23280dee`.
- The OTA updates `boot`, `dtbo`, `product`, `recovery`, `system`, `vbmeta`, and `vendor`. It does not update bootloader, modem, DSP, Bluetooth, or other low-level firmware partitions.
- The intended mechanism is Lineage Recovery factory reset followed by `Apply update` / `Apply from ADB`. The A/B updater, not manual fastboot commands, owns logical-partition updates and slot switching.
- A clean first installation must format `data` and `metadata`, destroying all apps, settings, accounts, messages, and internal-storage files.

Do not use `fastboot boot recovery.img`: support for temporary boot has not been established for this exact Motorola bootloader. Do not use `fastboot update` with the OTA ZIP, and do not manually flash `system`, `vendor`, `product`, or `super`.

## Artifact checks

- OTA ZIP integrity passes.
- OTA metadata reports `ota-type=AB`, `pre-device=odessa`, SDK 36, and payload major version 2.
- The OTA and generated recovery use the same Android test-key certificate. This remains an unofficial `userdebug` development build, not a release-signed artifact.
- Target-files VINTF validation returns `COMPATIBLE` for Linux `4.14.336-perf+` and FCM 6.
- Target-files AVB verification covers boot, DTBO, recovery, product, system, and vendor with vbmeta flags 0.
- The official Motorola Software Fix stock Rescue route remains the destructive fallback documented in `docs/stock-restore-rpas31-4-3-9.md`.

## Firmware-slot consistency gate

Current LineageOS Motorola SM6150 sibling devices use a `copy-partitions` package before first installation because the OTA does not ship low-level firmware. Historical Odessa community instructions also mention this step, but neither source proves that copying is necessary on this phone now.

The official `copy-partitions-20220613-signed.zip` was downloaded from LineageOS for inspection only:

- SHA-256: `92f03b54dc029e9ca2d68858c14b649974838d73fdb006f9a07a503f2eddd2cd`
- ZIP integrity passes.
- Its certificate is the official LineageOS key, which is not trusted by this test-key recovery.
- Its script uses raw `dd` to copy almost every A/B partition except boot, DTBO, system, and vbmeta.
- That broad loop can include `fsg` and other partitions this project treats as identity/calibration-sensitive.

Therefore this generic package is **not approved for sideloading or re-signing**. Do not weaken recovery signature checks and do not run its script manually.

Before the first write, compare SHA-256 values for a reviewed whitelist of non-sensitive A/B firmware partitions from the currently installed recovery without saving partition contents. If each pair matches, omit the copy step. If a pair differs, stop and review its provenance and function; do not automatically copy it.

The whitelist and read-only commands must exclude at least `fsg`, `persist`, `modemst1`, `modemst2`, `cid`, `prov`, `utags`, `utagsBackup`, and all other identity, calibration, DRM, attestation, or user-data storage.

## Completed read-only preflight

The following **READ ONLY** checkpoint was completed on 2026-07-19:

1. Reconfirm `odessa`, `XT2087-1`, active slot, two-slot layout, `securestate: flashing_unlocked`, battery at least 60%, and stable bootloader USB detection.
2. Boot the already installed recovery and compare only the approved non-sensitive A/B firmware hashes.
3. Return to Android and confirm `sys.boot_completed=1`.
4. Record whether firmware copying can be omitted.
5. Recovery and OTA hashes must still be rechecked immediately before any later device-changing command.

Because most firmware pairs differed, a partition-specific provenance and consistency review is required before the destructive first-install procedure can be written. No image is approved for flashing before that review.

## Firmware comparison result

The read-only comparison was completed on 2026-07-19 and is recorded in `docs/firmware-slot-comparison-20260719.md`.

- Product, SKU, slot count, unlock state, battery, recovery ADB, and return to Android were reconfirmed.
- Of 19 reviewed non-sensitive A/B firmware pairs, only `dsp`, `multiimgoem`, and `multiimgqti` matched; the other 16 differed.
- No partition image was saved or copied, and no partition was written.
- The generic `copy-partitions` package remains prohibited. Hash differences do not identify which side is newer or safe to copy.
- First installation remains blocked on a HOST ONLY partition-specific provenance and consistency review followed by a minimal, explicit firmware synchronization decision.

## Live preflight recheck

Rechecked **READ ONLY** on 2026-07-19 after the firmware comparison:

- Android reported product `odessa`, SKU `XT2087-1`, model `motorola g(9) plus`, active slot `_a`, and `sys.boot_completed=1`.
- Battery was present, healthy, USB powered, and at 100%.
- Android ADB and bootloader fastboot both detected the phone over USB without `sudo`.
- Bootloader fastboot reported product `odessa`, current slot A, two slots, `is-userspace: no`, and `securestate: flashing_unlocked`.
- `recovery.img` remains exactly 67,108,864 bytes with SHA-256 `dd4e3350ac92278b42a7db13bbc2f778898a923b09ab48b6d1368886272c2d26`.
- The OTA remains exactly 1,028,374,656 bytes with SHA-256 `65d3a91433e470899f79c75386e771bd6d84b3d4cde28f0a06a7d0dd23280dee`.
- The phone returned to Android on slot A; ADB detection and `sys.boot_completed=1` were reconfirmed.

This recheck does not resolve the differing low-level firmware slots or approve a device-changing command.
