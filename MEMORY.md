# Project Memory

This file preserves durable facts and decisions from prior sessions. It is context, not proof: re-verify safety-critical facts against the physical phone and current source before flashing or making compatibility claims.

## Current state

- The user has already prepared the LineageOS build environment.
- Use the current LineageOS build guide as the workflow baseline, starting from the `tucana` build guide's “Preparing the build environment” flow: <https://wiki.lineageos.org/devices/tucana/build/variant1/#preparing-the-build-environment>.
- Do not assume `tucana` device-specific commands, repositories, firmware, partition layout, or images apply to `odessa`; adapt the workflow using verified `odessa` data.
- The agent is expected to create and maintain the required device-specific configuration, kernel integration, manifests, proprietary-file integration, and related bring-up code rather than asking the user to author C/C++ or Android device-tree code.

## Known source leads

- Historical/incomplete LineageOS `odessa` device repository: <https://github.com/LineageOS/android_device_motorola_odessa>. Treat it as evidence and a migration baseline, not as a complete or currently compatible device tree.
- The `sm7150-mainline` organization contains postmarketOS/Linux-mainline work: <https://github.com/sm7150-mainline>. It may provide hardware, SoC, device-tree, and driver clues, but it is not automatically suitable for the Android/LineageOS kernel and userspace architecture.
- Existing Motorola `sm6150-common`, sibling-device, kernel, vendor, and firmware sources still need to be researched and pinned before selecting the implementation baseline.

## Working decisions

- Follow branch-current LineageOS conventions rather than copying a tutorial device's configuration.
- Reuse verified upstream code where compatible; write the missing `odessa`-specific pieces in this project.
- Keep postmarketOS/mainline Linux information as a research input only unless a component is shown to fit the selected Android kernel and vendor interfaces.
- No flashing occurs during initial discovery and source research.

## Verified physical-device baseline

The following was queried read-only from the connected phone on 2026-07-12. Sensitive identifiers such as the USB serial were deliberately not recorded.

- Retail region: Brazil.
- Device/product codename: `odessa`.
- Retail model: Motorola g(9) plus.
- Hardware SKU: `XT2087-1`.
- Current ROM: TequilaOS-derived Android 14 build.
- Current build fingerprint: `motorola/tequila_odessa/odessa:14/UQ1A.240105.004.A1/24010712:user/release-keys`.
- Current kernel: Linux `4.14.190-Amber`, AArch64, built 2024-01-17.
- Current bootloader: `MBM-3.0-odessa_retail-e69c40c38d6-220629`.
- Current baseband: `M7150_22.31.04.72R` / `ODESSA_BRLADSDS_CUST`.
- Vendor security patch: `2023-01-01`.
- Vendor API level: `29`, reflecting an Android 10-generation vendor interface under the Android 14 framework.
- Framework VNDK version: `34`.
- Encryption reports `encrypted` with file-based encryption.
- Current slot was `_a`; bootloader reports two slots and Android reports A/B updates enabled.
- Dynamic partitions are enabled. A raw `super` partition is present with size `0x244000000` (9,730,801,664 bytes, about 9.06 GiB).
- Bootloader `fastboot getvar is-userspace` returned `no`; that session tested bootloader fastboot, not fastbootd.
- Motorola bootloader `securestate` is `flashing_unlocked`; `iswarrantyvoid` is `yes`; `secure` is `yes`.
- Android's `ro.boot.flash.locked=1` conflicts superficially with the direct bootloader result. Treat `securestate: flashing_unlocked` as the stronger evidence, but re-query the bootloader immediately before any future flash.
- The mounted filesystems exposed Magisk overlays. Treat TequilaOS as a rooted behavioral reference; reproduce future ROM bugs without Magisk before attributing them to LineageOS.
- `adb` and bootloader `fastboot` were both tested successfully. The phone was returned to Android with `fastboot reboot`, and `sys.boot_completed=1` confirmed a complete boot.

## Verified host tools

- Platform Tools came from Google's official download.
- `adb`: protocol version `1.0.41`, Platform Tools `37.0.0-14910828`.
- `fastboot`: Platform Tools `37.0.0-14910828`.
- Tools are installed under `/home/arthu/bin/platform-tools`.
- Current host USB permissions support both `adb` and `fastboot`; no `sudo` was required.

## Phase 0 recovery status

- The user accepts a complete wipe and states that existing phone data does not need to be preserved.
- Exact SKU, codename, Brazilian region, current bootloader, current baseband, active slot, unlock state, A/B layout, dynamic partitions, `super`, Android USB communication, bootloader USB communication, and the return-to-Android path have been verified.
- Still required before any flash: identify the exact software channel beyond Brazil/RETAIL/LATAM where possible; acquire a trusted stock package at least as new as the installed low-level firmware; record its checksums; establish a verified stock restore procedure; collect a complete non-sensitive partition inventory; verify fastbootd and recovery behavior; and record the TequilaOS hardware baseline matrix.
- Unprivileged Android denied access to `/proc/partitions`. A later inventory may use existing root only to read non-sensitive partition names, sizes, types, and slot metadata. Do not dump identity/calibration partitions or use raw writes.

## Untrusted Android 10 stock-package candidate

- Local path: `Motorola_Moto_G9_Plus_XT2087-1_ODESSA_RETAIL_QPA30.19-Q3-32-50_LATAM/Firmware`.
- Source: a public, untrusted firmware website. The local files are useful research inputs but are not an approved restore package.
- Package identity: `odessa_retail`, `XT2087-1`, `LATAM`, Android 10 build `QPA30.19-Q3-32-50`, build date 2020-11-06.
- Package fingerprint: `motorola/odessa_retail/odessa:10/QPA30.19-Q3-32-50/4f9fc:user/release-keys`.
- Package bootloader: `MBM-3.0-odessa_retail-8b64315a8-201106`.
- Package baseband: `M7150_19.24.04.63R`; FSG version: `FSG-6150-07.57`.
- Package AVB metadata reports Android 10 and security patch `2020-11-01`.
- Payload includes `gpt.bin`, `bootloader.img`, `radio.img`, `BTFM.bin`, `dspso.bin`, `logo.bin`, `boot.img`, `dtbo.img`, `recovery.img`, `vbmeta.img`, and nine `super.img_sparsechunk.*` files.
- The package does not contain or require publishing device-unique identity/calibration partitions. Continue to protect `persist`, `modemst1`, `modemst2`, `fsg`, IMEI-bearing data, DRM/attestation material, serial numbers, and user data.
- All 19 payload MD5 values independently matched the included `flashfile.xml` manifest.
- `vbmeta.img` has a SHA256/RSA-2048 AVB signature. Its embedded signature verified, and it successfully verified the included `boot.img`, `dtbo.img`, and `recovery.img`.
- The AVB public-key SHA-1 identifier is `fd29248b78aa9d6427e8f569eda90be62b9fa0ee`. Compare this with a known-official later `odessa` package; an embedded-key verification alone does not prove Motorola provenance.
- Full AVB hashtree verification of `system`, `product`, and `vendor` was not completed because they are packaged as sparse `super` chunks rather than separate images. The sparse chunks did match the manifest hashes.

### Candidate payload SHA-256 values

```text
adbaefb1a3d96186ee7d8895fd82c563dbf7f71a1484d1b2702e179037603fe7  BTFM.bin
ac7ba3ae3432c007fe026f8402d194fd2e3e767378b0ad60b679fba21a837f39  boot.img
f78b4269311e910e141cd3c44e8c643bd73ec98fdc1c4b211641fbd90e792f79  bootloader.img
1a35e5c003642b341fa4cc55c76051a43308c721234a5c620ad2316b5cd2b480  dspso.bin
c8c27eca0e412df7ccf409467309677a90611145cae8906d66ad8257d65da629  dtbo.img
62a8ff2956728ba6bbd88393efce725114e9ab47c71676d72995012a3082d8ef  gpt.bin
4a08b9816f6b7104a8b0820ed0dbe33d48ce57de1a36477d4ceb469c7f672301  logo.bin
fc86280acb9debf5f3e6cbc8288439e403a4be3749df5bb9bc23595ea6fd9c7c  radio.img
9e1b91924f745d8022c249a05a1b65dcd1ceaca20aebc28a3fc6f81b8922b8f8  recovery.img
b768463a91c28a5830c83fa501da855546b2555129e137e4be6916642fa4e74c  super.img_sparsechunk.0
2b834710c0d2d4c494bd071042811da6ee739e3a27df8027d5532070371ff876  super.img_sparsechunk.1
4a813f43c0e231fe5c6616af0c6514a90569eeb1c9a8172a54c61807c31e52db  super.img_sparsechunk.2
54ab3e9efb2158e553e95307dd391c83f2df7da0504dec5586aad0892116d561  super.img_sparsechunk.3
8dc4edb7934d4cc0ae7ccf1b46d6d5b1381b193faa906d5823f833961b1dad34  super.img_sparsechunk.4
8d02bd33bb02b3be0762930eebeb0124393f1885702fbf10473fd97ca66a0876  super.img_sparsechunk.5
990f2591e9f2766c7cf1b9eaa2522f84db5612b46043eb8c27d5afc7e0bb8090  super.img_sparsechunk.6
053731cd33a5a78a0208f854062f682149780c47f663c4996d32fcd2eb22be5d  super.img_sparsechunk.7
90e5a8134ee881481738566bae720294048f33f46f64d4c47ba942d63d1c171c  super.img_sparsechunk.8
c9a0cf842bd4e4a90626f57413e14ce82f795c12461e4828253457b1468a2202  vbmeta.img
```

## Stock-package safety decision

- Never run the package's bundled Windows executables, DLLs, drivers, website shortcuts, RSD links, or `flashfile.bat`; they came from an untrusted distributor and are unnecessary on this Linux host.
- Do not flash this package. It is substantially older than the installed bootloader, modem, and vendor generation and could trigger rollback protection or leave incompatible low-level firmware.
- The included full-flash sequence rewrites the GPT and bootloader, replaces radio/Bluetooth/DSP firmware, replaces boot/recovery/AVB/`super`, and erases `carrier`, `userdata`, `metadata`, and `ddr`. The batch file also flashes `BTFM.bin` twice.
- The package is acceptable only for offline inspection, historical Android 10 comparison, original partition-layout research, and proprietary-blob comparison.
- Obtain the newest exact `XT2087-1` Brazilian/RETLA package through Motorola's official Software Fix/Rescue route. Download and inspect it without initiating Rescue. Prefer an exact or newer compatible package relative to bootloader `...-220629` and baseband `M7150_22.31.04.72R`.
- Official Motorola references: <https://en-us.support.motorola.com/app/softwarefix>, <https://en-us.support.motorola.com/app/answers/detail/a_id/143893>, <https://en-us.support.motorola.com/app/answers/detail/a_id/158726/>, and <https://en-us.support.motorola.com/app/answers/detail/a_id/167770/>.
