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

## LineageOS 23.2 configuration baseline

- The Android source checkout is initialized on `lineage-23.2` / Android 16, with Lineage's active release configuration `bp4a`.
- `manifests/odessa.xml` pins the initial source baseline to immutable commits:
  - Odessa device tree `49f6257549cd2081e7a07d7efae4ba51f3139983` (the only published LineageOS branch is `lineage-19.1`);
  - SM6150 common tree `47c9e585cf78f2371a4d12766925a0e73b5a97fb` (newest published branch `lineage-20`);
  - SM6150 kernel `112b525abbc08298256abedbf984e0e8c20d0338` (newest published branch `lineage-20`);
  - branch-current shared Motorola hardware tree `ffd5182343fb63227308f0f8b268358e3bd2a3b6`.
- The pinned manifest is active through `lineageos/.repo/local_manifests/odessa.xml`, and all four projects synced successfully.
- The historical shell-based proprietary extraction scripts were ported locally to the current Python `extract-utils` interface. The old common proprietary list contained duplicate destinations that current tooling rejects; those duplicates were removed while retaining the pinned Wi-Fi Display variants.
- The common tree's obsolete `device/qcom/sepolicy_vndr-legacy-um/SEPolicy.mk` include was migrated to the branch-current `device/qcom/sepolicy_vndr/legacy-um/SEPolicy.mk` path.
- Baseline vendor makefiles were generated from the proprietary lists. No proprietary payload is currently considered complete.
- `source build/envsetup.sh && lunch lineage_odessa-bp4a-userdebug` now succeeds and reports LineageOS `23.2`, Android `16`, target `lineage_odessa`, and both ARM64/ARM architectures.
- Direct extraction from the running TequilaOS installation is incomplete: unprivileged ADB receives `Permission denied` on `/vendor`, and `adb shell su -c id` was denied. Do not weaken device permissions to work around this.
- The LineageOS manual ZIP extraction guide is applicable once a suitable exact ROM/OTA package is available: unpack the payload or dynamic partitions to a host directory, then run `extract-files.py` against that directory. The currently available Android 10 stock package is too old to be accepted as the target blob source.
- The exact installed TequilaOS payload has now been obtained and verified; the next build blocker is reconciling the historical proprietary lists against that payload and the newer public SM6150 trees.

## Community-source evaluation and exact TequilaOS payload

- The XDA TequilaOS download is still available as `tequila-uno-20240117-0816-UNOFFICIAL-odessa.zip`. It was downloaded to the ignored path `lineageos/.downloads/`.
- Pixeldrain reports SHA-256 `2eebc8ee17bcbc3a28d96b7b1dbf1b6769c6281d437194fbf582f0e2b365fdb6`; the downloaded file independently matched.
- The ZIP is payload-based and contains `boot`, `dtbo`, `product`, `recovery`, `system`, `vbmeta`, and `vendor`. `ota_extractor` successfully extracted every partition.
- The extracted build fingerprint is exactly the fingerprint observed on the connected phone: `motorola/tequila_odessa/odessa:14/UQ1A.240105.004.A1/24010712:user/release-keys`. This establishes the ZIP as the matching installed-ROM package, not merely a similar build.
- Package properties confirm Android 14, framework security patch `2024-01-05`, vendor security patch `2023-01-01`, shipping API 29, and board `sm6150`.
- The packaged boot image uses header version 2 and contains Linux `4.14.190-Amber`, built 2024-01-17 with Android clang 14. This matches the running-device kernel identity.
- Host-side extraction with the migrated proprietary lists now obtains almost all Odessa-specific blobs. The remaining failures are primarily obsolete or separately sourced common Wi-Fi Display entries, root-relative old-list paths, pinned hashes from another Motorola model, and the absent `vendor/bin/charge_only_mode`. Reconcile the lists against the newer public SM6150 trees rather than weakening extraction checks.
- The repository linked as `delawcharles/device_motorola_odessa` is not a LineageOS 20-era tree: its only branch is `staging/lineage-17.1`, head `431fd9cb9c395bd12ace3968de5384c0e6b07891`, last pushed in 2020. Keep it only as early-history evidence.
- The 2025 Project Infinity X Android 16 thread publishes more useful device sources:
  - Odessa device branch `infinityx`, head `423733e268d2e05056166a0d4413a710d261b56a`;
  - SM6150 common branch `infinity`, head `7bfd3cd1ab3f499082ca24c7243569ba4a83edbb`;
  - its thread links `Frost444/kernel_motorola_liber`; the newer `miguelbarretoo/android_kernel_motorola_sm6150` fork has an Android 16 QPR2 head `c31c33d81187844b94b546f50db73610e95ac479`.
- The newer kernel remains Linux 4.14.190, contains `vendor/odessa_defconfig`, and that defconfig generated successfully for ARM64. The generated local version is `-FlopX-Kernel`, showing inherited branding that must be cleaned before adoption.
- The candidate kernel has no merge base with the current LineageOS kernel history and differs in 319 files (5,791 insertions, 7,256 deletions). Its recent history added and removed several root/SUSFS implementations; the selected QPR2 tip is explicitly `sm6150: remove all ksu support`, and no KSU/SUSFS configuration remained in the generated Odessa config.
- Adoption decision: use the exact TequilaOS payload as the immediate proprietary-blob and working-behavior reference; use the Infinity X device/common/kernel repositories as migration and patch evidence. Do not replace the pinned LineageOS baseline wholesale until individual changes are reviewed, the kernel builds under LineageOS 23.2, and boot/security behavior is validated.

## 2026-07-13 proprietary reconciliation and focused Android 16 build

### Revisions and blob provenance

- The source baseline remained pinned; no community tree or kernel replaced it:
  - `device/motorola/odessa`: `49f6257549cd2081e7a07d7efae4ba51f3139983`;
  - `device/motorola/sm6150-common`: `47c9e585cf78f2371a4d12766925a0e73b5a97fb`;
  - `kernel/motorola/sm6150`: `112b525abbc08298256abedbf984e0e8c20d0338`;
  - `hardware/motorola`: `ffd5182343fb63227308f0f8b268358e3bd2a3b6`.
- The sole accepted proprietary source is `.downloads/tequila-uno-20240117-0816-UNOFFICIAL-odessa.zip`, SHA-256 `2eebc8ee17bcbc3a28d96b7b1dbf1b6769c6281d437194fbf582f0e2b365fdb6`. Its extracted filesystem is `.downloads/tequila-uno-20240117/images`.
- The final lists identify this ZIP and hash in their headers. They contain 208 Odessa entries and 871 common entries. A host-side revalidation found zero missing sources, zero pinned-hash mismatches, and zero duplicate destinations in both lists.
- `system_ext/priv-app/ims/ims.apk` is the only retained hash-pinned blob. Its old Lineage-list hash `2fbaabee440315379ad284c38ebe2a006db50216` was replaced with the exact Tequila file's SHA-1 `2d54a5285aac0e97b70d20dd26bdcb281ffa9607`; it is not a separately sourced blob.
- No Edge S, other Motorola firmware, community-ROM, or other separately sourced blob remains in the generated vendor trees.

### Reconciliation decisions

- Removed Odessa `vendor/bin/charge_only_mode`: it is absent from the exact Tequila payload and the modern comparison trees. Removed common `vendor/etc/init/hw/init.mmi.charge_only.rc` with it because retaining an init service for a nonexistent executable is invalid. Charge-only mode is not claimed supported; implementing and validating it is future device-behavior work.
- Removed proprietary `vendor/lib64/com.motorola.hardware.biometric.fingerprint@1.0.so` and common `vendor/lib64/libqsap_sdk.so`: both interfaces are built from the pinned `hardware/motorola` source tree. The generated vendor namespaces import `hardware/motorola`.
- Removed the 87-entry Motorola Edge S Wi-Fi Display set. This means all 71 old entries whose list text contains `Wfd`, `wfd`, or `wifidisplay`, plus these 16 companion entries:
  - `system_ext/lib/{libmmosal,libmmparser_lite,libmmrtpdecoder,libmmrtpencoder}.so`;
  - `system_ext/lib64/{libmmosal,libmmparser_lite,libmmrtpdecoder,libmmrtpencoder}.so`;
  - `vendor/lib/{libFileMux_proprietary,libhdcp1prov,libhdcp2p2prov,libhdcpsrm,libmm-hdcpmgr,libmmosal,libmmrtpdecoder_proprietary,libmmrtpencoder_proprietary}.so`.
  Every file in this set was hash-pinned from a different device/firmware, absent from the matching Tequila package, and absent from the reviewed modern Odessa common tree. `WfdCommon` was also removed from `PRODUCT_BOOT_JARS`; `libnl` and `libwfdaac_vendor` were removed from the obsolete Wi-Fi Display product block. Wi-Fi Display is not claimed supported.
- Removed root-relative `lib64/libaptX_encoder.so` and `lib64/libaptXHD_encoder.so`: these historical extraction paths do not exist in the exact package or the reviewed modern Odessa list. The Tequila payload still supplies the DSP-side `vendor/lib/rfsa/adsp/capi_v2_aptX_Classic.so` and `capi_v2_aptX_HD.so`; Bluetooth aptX behavior remains a hardware test item, not an assumption.
- Moved old root-relative `etc/permissions/privapp-permissions-qti.xml` to its actual Tequila location, `system_ext/etc/permissions/privapp-permissions-qti.xml`. Likewise, `moto-telephony.xml` and `moto-telephony.jar` now use their actual `system_ext` paths instead of legacy source-to-destination remaps.
- Odessa camera permission files now extract directly from `vendor/etc/permissions`; Tequila already places them there, so the old product-to-vendor copy syntax was removed.
- Added the 32-bit and 64-bit Tequila OMX audio encoder blobs `libOmxAacEnc`, `libOmxAmrEnc`, `libOmxEvrcEnc`, `libOmxG711Enc`, and `libOmxQcelp13Enc`; they were present in the exact payload and required by the retained media graph.
- Current extract-utils package syntax replaced obsolete leading `-` package markers. `MODULE_SUFFIX=_system_ext` disambiguates same-basename `system_ext` and vendor IMS/data/display libraries. Narrow `DISABLE_DEPS` markers were added only where the legacy blob's ELF graph names an unavailable architecture/partition variant; they were not used to hide missing source files.

### Generated vendor and build integration

- Current LineageOS Python extract-utils scripts now drive the Odessa/common pair. Final extraction from `.downloads/tequila-uno-20240117/images` exited successfully, restored the exact pinned IMS file, and regenerated `vendor/motorola/odessa` and `vendor/motorola/sm6150-common` makefiles without a partial result.
- The generated integrations parse successfully through Soong and Kati. Product namespaces now cover the branch-current Qualcomm display, WLAN, data-services, boot-control, and Motorola source modules needed by the blob dependency graph.
- Historical duplicate local boot-control modules were removed in favor of `hardware/qcom-caf/bootctrl`. Historical local LiveDisplay Soong definitions were removed in favor of branch-current `vendor.lineage.livedisplay-service.sdm`. Other migrated product modules include `gralloc.qcom`, `hwcomposer.qcom`, `libstdc++_vendor`, `android.hardware.thermal-service.qti`, and `android.hardware.wifi-service`.
- Both duplicate kernel `audio_kernel_headers` Android make definitions were removed; the branch-current `hardware/qcom-caf/common` header module is the single owner.
- Four strict-prototype fixes were required for the pinned 4.14 kernel under the Android 16 clang toolchain: `tty_diag_channel_abandon_request(void)`, `tty_diag_get_dbg_ftm_flag_value(void)`, `ce_services_legacy(void)`, and `target_if_get_ctx(void)`. These match their existing header declarations and do not change runtime behavior.

### Verified result

- `source build/envsetup.sh && lunch lineage_odessa-bp4a-userdebug` succeeded with `PLATFORM_VERSION=16`, `TARGET_PRODUCT=lineage_odessa`, `TARGET_BUILD_VARIANT=userdebug`, `TARGET_ARCH=arm64`, release config `bp4a`, and LineageOS `23.2`.
- `m bootimage` completed successfully on focused attempt 27. Full log: `lineageos/.downloads/build-logs/m-bootimage-20260713-attempt27.log`.
- Output: `lineageos/out/target/product/odessa/boot.img`, exactly 67,108,864 bytes, SHA-256 `c29246952c100b5116682a1875ab5c08c3c56638653e24bef4fa8c240a4ce93e`.
- No focused-build source blocker remains. The next untested build gate is a complete product/target-files build, which may expose vendor, VINTF, SELinux, partition-size, or packaging defects not exercised by `bootimage`.
- Known focused-build warnings remain and must not be mistaken for hardware readiness: malformed non-string touchscreen-overlay `status` properties, duplicate fingerprint notifier exports because both ETS and FPC modules build, old common-tree firmware-mount mkdir overrides, and depmod metadata warnings. Resolve or validate these before any image is considered flashable.
- This was HOST ONLY. Nothing was flashed, booted, sideloaded, or changed on the phone.
