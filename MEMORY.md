# Project Memory

This file preserves durable facts and decisions from prior sessions. It is context, not proof: re-verify safety-critical facts against the physical phone and current source before flashing or making compatibility claims.

## Current state

- The user has already prepared the LineageOS build environment.
- Use the current LineageOS build guide as the workflow baseline, starting from the `tucana` build guide's “Preparing the build environment” flow: <https://wiki.lineageos.org/devices/tucana/build/variant1/#preparing-the-build-environment>.
- Do not assume `tucana` device-specific commands, repositories, firmware, partition layout, or images apply to `odessa`; adapt the workflow using verified `odessa` data.
- The agent is expected to create and maintain the required device-specific configuration, kernel integration, manifests, proprietary-file integration, and related bring-up code rather than asking the user to author C/C++ or Android device-tree code.
- For long Android build commands, give the user a command that redirects routine output to a log and ask for the concise result. Do not run long builds in the main agent context; if autonomous execution is necessary, use a subagent.

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

## 2026-07-14 interrupted full target-files build

- A HOST ONLY `m target-files-package` run was attempted seven times for `lineage_odessa-bp4a-userdebug`; no phone command was issued and no target-files archive was produced.
- Attempt 1 reached 74,490/198,469 actions (37%) and exposed the first device blocker: removed `cutils/threads.h` in the legacy GPS utility. Attempt 2 was interrupted during build parsing. Logs: `lineageos/.downloads/build-logs/target-files-package-20260713-215237-attempt1.log` and `...-222707-attempt2.log`.
- Subsequent incremental fixes, all still uncommitted, were:
  - remove unused `cutils/threads.h` from `device/motorola/sm6150-common/gps/pla/android/loc_pla.h`;
  - qualify `move` as `std::move` in `gps/utils/LocIpc.cpp`;
  - move the kernel's private `struct sched_param` from exported `include/uapi/linux/sched/types.h` to internal `include/linux/sched.h`, avoiding collision with Bionic's definition;
  - delete obsolete Odessa `vendor_hal_fingerprint_fpc` policy and label `fpc_ident` with `hal_fingerprint_default_exec`;
  - define `PTN_MULTIIMGOEM` and `PTN_MULTIIMGQTI` in common `gpt-utils/gpt-utils.h` for the current QTI boot-control implementation.
- Attempts 3-6 verified those blockers in sequence. Logs: `...-223134-attempt3.log`, `...-223410-attempt4.log`, `...-225524-attempt5.log`, and `...-232149-attempt6.log`.
- Attempt 7 passed the previous GPS, scheduler-UAPI, SELinux, and boot-control failures and continued compiling/installing C/C++, Rust, Java, Wi-Fi supplicant interfaces, recovery libraries, GNSS, radio, and system applications. Its log ends abruptly at 10,296/64,927 remaining actions (15%) without `BUILD_EXIT_STATUS`; the user reports the Linux kernel killed the process for excessive RAM use. Log: `lineageos/.downloads/build-logs/target-files-package-20260713-232635-attempt7.log`.
- Therefore the full product did **not** finish. The next session should preserve `out/` for incremental reuse, inspect host RAM/swap and the OOM record, then rerun with constrained Ninja parallelism rather than restarting an unconstrained build. Do not treat the Clang/Rust/Java output as proof of completion; success requires an exit-zero log and a target-files ZIP with size and SHA-256.

## 2026-07-15 product-config JSON fix

- A constrained `m -j8 target-files-package` retry reached 1,086/54,681 actions, then failed while merging `out/soong/soong.lineage_odessa.extra.variables`: `RecoveryPixelFormat` was emitted as invalid JSON `""RGBX_8888""`.
- The source was the historical `TARGET_RECOVERY_PIXEL_FORMAT := "RGBX_8888"` assignment in `device/motorola/sm6150-common/BoardConfigCommon.mk`. Current Soong adds JSON quoting itself, so the assignment was corrected to the unquoted make value `RGBX_8888`.
- Focused verification with `m -j8 product-config` completed successfully. The preceding AppFunctions missing-class diagnostic and Rust `tagged-globals` Clippy message were non-fatal warnings for this failure.
- The full target-files build remains incomplete and should be resumed with `m -j8 target-files-package`, preserving `out/`.
- The next full-build blocker was the legacy Motorola `libdisppower` module failing to compile because current `perfmgr/FlagProvider.h` includes generated `powerhal_flags.h`. The module now mirrors the current Pixel display-power dependency pattern by adding static dependencies on `powerhal_flags-aconfig-cc` and `libaconfig_storage_read_api_cc`.
- Focused `m -j8 libdisppower` verification completed successfully for both arm64 and arm static/shared variants. The full target-files build still needs to resume.

## 2026-07-15 build-property override migration

- The resumed build failed generating the ODM `build.prop` because the historical Odessa product used legacy `PRODUCT_BUILD_PROP_OVERRIDES` keys `PRODUCT_NAME` and `PRIVATE_BUILD_DESC`, which Android 16's `gen_build_prop` rejects.
- `device/motorola/odessa/lineage_odessa.mk` now uses the current schema keys `DeviceProduct`, `BuildDesc`, and `BuildFingerprint`, preserving the Android 11 Motorola identity values.
- Focused generation of `out/soong/.intermediates/build/soong/odm-build.prop/android_common/build.prop` completed successfully. The generated ODM properties contain `ro.product.odm.name=odessa_retail`, `ro.product.odm.device=odessa`, and the intended stock fingerprint.
- The full target-files build remains incomplete and should resume with `m -j8 target-files-package`, preserving `out/`.

## 2026-07-16 pre-full-build review

- A read-only review covered the Odessa device tree, SM6150 common tree, their cross-tree integration, and the selected kernel configuration/source. No device was contacted or flashed, and no Android project source was changed by the review.
- Keep `device/motorola/sm6150-common` separate from `device/motorola/odessa`. It contains genuinely shared platform integration and explicit sibling-device behavior. Correct the current ownership leaks, especially the common vendor namespace's Odessa dependency, rather than merging the trees.
- Immediate runtime blockers found: the selected AIDL lights HAL advertises a backlight with an empty callback and leaves every advertised light's type unset; the FPC fingerprint HAL executable has no SELinux executable label; fingerprint selector policy cannot create/update its persist selector files; and both fingerprint kernel nodes/drivers are enabled on the same GPIOs with duplicate exported notifier symbols.
- The common configuration still advertises or starts removed/nonexistent functionality, including Wi-Fi Display, charge-only mode, old HIDL LiveDisplay, duplicate `time_daemon`, and several unowned init services. Its VINTF manifest must be reconciled against the actually shipped services before a full build can be considered valid.
- The current vbmeta configuration uses AVB flags `3`, explicitly disabling verification and hashtrees. Treat this as temporary bring-up configuration pending bootloader-specific validation, not a release-ready security configuration.
- The touchscreen DT overlays intentionally use Motorola-specific multi-string `status` properties and emit DTC warnings. Touch depends on stock bootloader DT mutation unless proven otherwise; do not enable both competing touch nodes blindly.
- The uncommitted brace fix in `gps/android/utils/battery_listener.cpp` prevents `mHealth` from being dereferenced when null during unregister. The destructor still writes `mDone` outside its mutex, does not notify `mCond` before joining, and can call `join()` through a null `mThread` if Health HAL initialization failed.
- HOST ONLY focused validation succeeded for `android.hardware.lights-service.odessa` and `android.hardware.gnss@2.1-service-qti` under the normal `lineage_odessa-bp4a-userdebug` lunch environment. All tracked XML in both device trees parsed with `xmllint`, and `git diff --check` passed for device, common, and kernel trees. No target-files ZIP exists; full VINTF, partition sizing, image packaging, AVB, and OTA checks remain unproven.

## 2026-07-16 pre-full-build fixes

- The review fixes were committed on the local `lineage-23.2` branches:
  - Odessa device: `55aa52999c71c2ace5976768a33512d26e8fa73a`;
  - SM6150 common device: `31eea31c91705d042af7d74b460e872aebbf4067`;
  - SM6150 kernel: `92a96be148a072185131f60977af463c918b58cd`;
  - SM6150 common vendor integration: `b20e28ee4cc1d7a54dc3f69689e72756fc8880e1`.
- Keep the Odessa and SM6150 common device repositories separate. The common tree remains the owner of shared audio, radio, GNSS, display, boot-control, partition, init, and SELinux integration. Its extraction and generated vendor namespace no longer depend on `vendor/motorola/odessa`.
- The AIDL lights HAL now reports correct type/ordinal metadata, implements backlight writes, scales framework brightness to the kernel's sysfs maximum, gives the service access to the backlight node, declares AIDL version 2, and preserves battery/notification LED handling.
- The FPC HAL has the standard fingerprint executable label. The fingerprint selector can create and update only its labeled persist files, including truncating existing IDs. Egis and FPC now use one notifier implementation built into the kernel, eliminating duplicate exported symbols while retaining userspace selection of either sensor module.
- The GNSS battery listener no longer uses a detached initializer. Health-HAL failure, callback unregister, condition-variable shutdown, service death, global teardown, and later reinitialization are synchronized and null-safe.
- Removed unsupported or stale Wi-Fi Display declarations, WFD hidden-API entries/fixups, charge-only service/policy, old HIDL LiveDisplay source/manifest/policy, duplicate `time_daemon`, obsolete display post-processing triggers, missing automatically started services, and the missing Motorola autotest service. AOD is no longer exposed on the LCD, unverified sensor/CDMA/device-ID features are no longer declared, and NFC release logging is reduced.
- Removed the global duplicate-rule and ELF-copy build escape hatches and the old firmware-mount make rules they concealed. Product configuration and policy generation pass without them.
- AVB remains enabled, but vbmeta flags `3` were removed so new vbmeta output will no longer request disabled verification and hashtrees. Final AVB metadata still requires inspection from a completed product build before flashing.
- Kernel fixes include the parallel-charger Kconfig ownership correction, FPC GPIO error handling, removal of the fingerprint notifier lifetime hazard, a narrower Android-only `sched_param` UAPI exclusion, and Odessa hardening for refcounts, dmesg restriction, forced module unloading, LoadPin availability, and Yama.
- HOST ONLY verification passed for `product-config`, `android.hardware.lights-service.odessa`, `liblocbatterylistener` in both architectures, `android.hardware.gnss@2.1-service-qti`, and the complete `selinux_policy` target including neverallow/context tests. `bootimage` and `dtboimage` also completed after the kernel changes.
- Resulting focused artifacts: `boot.img`, 67,108,864 bytes, SHA-256 `c904313b4ca4dbecea8ec50455913fdd485650eb9879d37a33101c0f5baa7406`; `dtbo.img`, 25,165,824 bytes, SHA-256 `7b76a363a0ff5ad8e1516fb05c3fde710be2962b51ff7fb6090d5e74edc9`.
- A direct `check-vintf-all` request expanded to roughly 89,000 product actions and was stopped by the 10-minute tool timeout at about 5%; the displayed failures were cancelled actions after SIGTERM, not source diagnostics. Full VINTF, final vbmeta, partition sizing, target-files, and OTA checks therefore remain gated on the constrained full build.
- Remaining hardware-dependent risks were deliberately not guessed away: Motorola's bootloader-specific touchscreen `status` tuples still emit DTC warnings and require DTBO/bootloader validation; actual Egis/FPC selection requires physical-device testing; Linux 4.14.190 remains legacy/EOL; charge-only behavior is not claimed; and no image is approved for flashing yet.
- `manifests/odessa.xml` still pins the public historical baselines. Do not replace those revisions with unpublished local commit IDs under the public GitHub remotes; update the manifest after private/published remotes can fetch the new commits.

## 2026-07-16 power HAL Android 16 migration

- The resumed full build reached 73% and failed because the SM6150 power-service sources include current `libperfmgr` headers, whose generated `powerhal_flags.h` was not exposed through the shared-library dependency.
- `android.hardware.power-service.sm6150-libperfmgr` now directly links `powerhal_flags-aconfig-cc` and `libaconfig_storage_read_api_cc`, matching current Lineage/Pixel power-service consumers.
- Compiling past that header exposed three additional API removals. The service now treats `HintManager::GetInstance()` as the non-owning singleton pointer returned by the current API; legacy hint-driven profile switching uses `GetAdpfProfileFromDoHint()` / `SetAdpfProfileFromDoHint()`; and the old early-boost timer was removed because current `AdpfConfig` has no early-boost fields and the device configuration supplied no corresponding settings. PID/uclamp control and stale-session handling remain.
- HOST ONLY focused verification with `m -j8 android.hardware.power-service.sm6150-libperfmgr` completed successfully and installed the vendor power-service executable. The constrained full `target-files-package` build still needs to resume from the preserved output tree.

## 2026-07-17 sccache build configuration

- The host has `/usr/bin/sccache` version `0.16.0`.
- For future LineageOS builds, use `sccache` instead of `ccache` while retaining `USE_CCACHE=1`, because the Android and Lineage build integrations use that variable to enable compiler wrappers.
- Do not point `CCACHE_EXEC` directly at `sccache`: this branch's Soong sandbox invokes `CCACHE_EXEC -k cache_dir`, a `ccache` query that `sccache` 0.16.0 rejects.
- Use an executable compatibility wrapper at `/home/arthu/bin/sccache-android`. It must print `${SCCACHE_DIR:-$HOME/.cache/sccache}` when invoked as `-k cache_dir` and otherwise run `exec /usr/bin/sccache "$@"`.
- Build environment:
  - `export USE_CCACHE=1`
  - `export CCACHE_EXEC=/home/arthu/bin/sccache-android`
  - `export SCCACHE_DIR="$HOME/.cache/sccache"`
  - `export SCCACHE_CACHE_SIZE=50G`
- Before a build, restart the server after setting those variables with `sccache --stop-server` and `sccache --start-server`. Use `sccache --zero-stats` before measurement and `sccache --show-stats` afterward.
- `SCCACHE_CACHE_SIZE=50G` replaces `ccache -M 50G`. No equivalent of `ccache -o compression=true` is required because sccache handles cache compression internally.
- Preserve the existing incremental `out/` tree and continue the constrained build with `lunch lineage_odessa-bp4a-userdebug` followed by `m -j8 target-files-package`.
- The first sccache-enabled build failed immediately because `/home/arthu/.cache/sccache` had accidentally been created as an empty regular file. It was replaced with a directory and the server was restarted. A two-compile C smoke test then reported one miss followed by one hit, no cache errors, and a 50 GiB maximum, confirming the local cache works. The failed Android actions produced no source defect; rerun the same incremental build without cleaning `out/`.

## 2026-07-17 transient Clang crash and USB storage reset

- A constrained full build reported a Clang 21 optimizer segmentation fault while compiling the generated HIDL source `android.hardware.audio@7.0` `PrimaryDeviceAll.cpp`. This was not a C++ diagnostic or a reproducible source failure.
- The host kernel log showed simultaneous USB UAS failures on workspace drive `/dev/sdb`: multiple read/write command aborts and xHCI bad-transfer events began at 18:09:18, followed by a successful USB device reset at 18:09:39. The build reported the Clang failure at 18:10:09. Treat the compiler crash as secondary to this storage transport incident unless it recurs without USB errors.
- `/dev/sdb1` is the Btrfs workspace filesystem. After the reset, Btrfs device counters reported zero read, write, flush, corruption, and generation errors. No new USB, Btrfs, OOM, machine-check, or memory errors appeared during focused verification.
- HOST ONLY verification with `m -j1 android.hardware.audio@7.0` rebuilt the exact failing `PrimaryDeviceAll.cpp` arm64 target and completed all 1,992 module actions successfully in 7:07. No source workaround or Clang bug report is warranted from this incident.
- Before another long build, stabilize the external SSD connection (direct port and known-good cable/enclosure where possible). Preserve `out/`; after the physical connection is reliable, resume the incremental `m -j8 target-files-package` build rather than cleaning or patching the audio interface.

## 2026-07-18 obsolete Qualcomm wifilearner removal

- The constrained full build reached the vendor init-copy stage and rejected `vendor.qti.hardware.wifi.wifilearner@1.0-service.rc`: its lazy-service `IWifiStats` interface was unknown because the proprietary interface library is only a prebuilt and no source `hidl_interface` target exists.
- Current LineageOS Qualcomm common trees remove this obsolete extension rather than weakening `host_init_verifier` or deleting only the lazy-start declaration. The SM6150 common proprietary list now omits `wifilearner`, its init script, and `vendor.qti.hardware.wifi.wifilearner@1.0.so`; the matching VINTF HAL declaration was also removed.
- Regeneration from the verified TequilaOS payload removed all three files and their generated `Android.bp`/vendor-make entries. No `wifilearner` reference remains in `vendor/motorola/sm6150-common`; XML validation and `git diff --check` pass.
- The resumed `m -j8 target-files-package` run recognized the deleted init glob and no longer reported the original verifier error. During mandatory Soong graph regeneration it exposed an independent platform failure: the arm64 `libzygote` rlib reports multiple outputs from its shared dependency `libseccomp_policy` at `system/zygote/zygote/Android.bp:95`. Do not reintroduce wifilearner to investigate this next blocker.

## 2026-07-18 Widevine crypto compatibility fix

- The Android 14 TequilaOS `vendor/lib64/libwvhidl.so` imports `CBS_init` from its original `libcrypto.so`, but Android 16's BoringSSL no longer exports that symbol. This caused Soong's strict ELF check to fail even though `libcrypto` was declared.
- The common extraction script now reproducibly adds `libcrypto_shim.so` to the blob's ELF `DT_NEEDED` list. LineageOS's existing vendor-capable `hardware/lineage/compat:libcrypto_shim` implements the required `CBS_init` ABI; the original `libcrypto.so` dependency remains intact.
- Regeneration from the verified TequilaOS payload patched the proprietary blob and generated `libcrypto_shim` as a Soong shared dependency. No `allow_undefined_symbols` escape hatch was added.
- HOST ONLY focused verification with `m -j8 libwvhidl` completed successfully, including the exact `libwvhidl check elf file` action, and installed both vendor libraries. The constrained full `target-files-package` build still needs to resume from the preserved output tree.

## 2026-07-18 completed target-files and validation

- The full HOST ONLY `m -j8 target-files-package` build completed and produced `lineageos/out/target/product/odessa/obj/PACKAGING/target_files_intermediates/lineage_odessa-target_files.zip`.
- Initial post-build VINTF validation found `android.hardware.boot@1.1::IBootControl/default` declared both in the common device manifest and the branch-current boot service's own VINTF fragment. The obsolete declaration was removed from `device/motorola/sm6150-common/manifest.xml`, and the user completed a new target-files build.
- Corrected archive: 2,614,118,513 bytes, SHA-256 `df57ff2dd125159a34bcf27a345306a993ba738621ebc50144fe40d7d2f34527`, modified 2026-07-18 14:02:54 -0300. `unzip -tq` reported no compressed-data errors.
- A standalone non-verbose `check_target_files_vintf` invocation appeared to exit zero after the duplicate boot HAL was fixed, but this was not sufficient proof of compatibility. The OTA generator's verbose internal check, which passes the fully populated target `BuildInfo`, definitively returned `INCOMPATIBLE`: kernel FCM level was unspecified and numerous proprietary/device HALs were absent from the assembled framework compatibility matrices. The duplicate boot HAL error itself is gone.
- `avbtool verify_image` successfully verified the RSA-4096 vbmeta signature plus boot, DTBO, recovery, product, system, and vendor descriptors/hashtrees. Vbmeta flags are `0`; this remains a test-key `userdebug` artifact, not a release-signed image.
- The dynamic partition group is 4,864,868,352 bytes per slot. Product, system, and vendor consume 4,589,371,392 bytes including AVB metadata, leaving 275,496,960 bytes (about 263 MiB), or 5.67% headroom. This fits but should be monitored.
- The user subsequently completed the HOST ONLY `m -j8 ota_from_target_files` host-tool build. Direct OTA generation stopped before payload creation at the mandatory VINTF gate; no installable OTA ZIP was generated and compatibility checks were not bypassed.
- The pending source fix adds `<kernel target-level="4"/>` to the common device manifest and includes LineageOS's existing Motorola, Qualcomm, and legacy Qualcomm device-framework matrices through `DEVICE_FRAMEWORK_COMPATIBILITY_MATRIX_FILE`. XML validation and `git diff --check` pass. A new target-files archive must be generated and its OTA VINTF gate rerun to prove that these standard matrices cover every declared HAL.
- No image is approved for flashing yet. Phase 0 still lacks a trusted current exact-variant stock restore package/procedure, complete non-sensitive partition inventory, verified fastbootd/recovery behavior, and the TequilaOS hardware baseline matrix.

## 2026-07-18 transient Rust LLVM crash

- After the VINTF source fixes, the user's incremental target-files rebuild reached 95% and Rust 1.88's LLVM 20.1 optimizer crashed with SIGSEGV/general-protection fault while producing `libandroid_runtime`'s generated Rust static library. This was an internal ThinLTO optimizer crash, not a Rust source diagnostic.
- Host kernel logs at 15:04:16 contain the matching `libLLVM.so.20.1` general-protection fault but no USB/UAS, Btrfs, OOM, or machine-check event. Btrfs `/dev/sdb1` read/write/flush/corruption/generation counters remain zero. The host currently has ample RAM and zram swap.
- Treat this as transient unless the exact action reproduces. First retry only `m -j1 libandroid_runtime` without cleaning or changing Rust stack/LTO settings; if that succeeds, resume `m -j8 target-files-package`. If it reproduces, preserve the crash and investigate compiler/hardware stability before adding a workaround.

## 2026-07-18 FCM 6 follow-up

- The focused `m -j1 libandroid_runtime` retry succeeded, confirming the Rust LLVM crash was transient. The user's subsequent incremental `m -j8 target-files-package` build also completed.
- Regenerated target-files archive: 2,614,132,019 bytes, SHA-256 `08095785266b97b4fbf3349a92a0ae495140ab2316941cd89f386a2884db735f`, modified 2026-07-18 17:24:59 -0300; ZIP integrity passed.
- OTA generation again stopped at mandatory VINTF validation. Including the standard Motorola/Qualcomm matrices reduced the missing-HAL list from dozens to only `android.hardware.configstore@1.1::ISurfaceFlingerConfigs/default`, `android.hardware.memtrack@1.0::IMemtrack/default`, and `motorola.hardware.health@1.0::IMotHealth/default`.
- Current Android 16 VINTF rejects kernel FCM 4 with Linux 4.14: the first allowed FCM for 4.14 is 6. A branch-current LineageOS 23.2 Xiaomi SM6150 reference also uses device manifest target level 6.
- Pending source fixes set both Odessa/common device manifest fragments and the kernel declaration to target FCM 6. A new common `framework_compatibility_matrix.xml` contains only the three remaining optional HAL instances and is included alongside the standard Motorola, Qualcomm, and legacy Qualcomm matrices. All changed XML parses and `git diff --check` passes.
- No OTA ZIP was produced and no compatibility check was bypassed. Regenerate target-files once more, then rerun OTA generation to prove FCM compatibility.

## 2026-07-18 Android 16 kernel minimum blocker

- The user regenerated target-files after the FCM 6 and supplemental-matrix changes. Archive: 2,614,137,705 bytes, SHA-256 `d67ea5d5f2e5712f569d0cd4c56d5aa279da4421597ad9cda8d110eea441842a`, modified 2026-07-18 17:38:15 -0300; ZIP integrity passed.
- OTA VINTF validation now accepts all device/framework HAL declarations. The sole remaining incompatibility is the kernel patch level: FCM 6 requires Linux 4.14.336 or newer, while the selected kernel is 4.14.190. No OTA ZIP was generated.
- Do not fake `SUBLEVEL`, remove kernel metadata, downgrade FCM, or skip compatibility checks. Android 16 requires a real stable-kernel update with the corresponding fixes.
- The public `motorola-sm6150-devs/kernel_motorola_sm6150` `lineage-20` branch reaches 4.14.326 and shares historical merge bases with this kernel, but its current tree differs by roughly 9,030 files; it is not safe to merge or replace wholesale without review. It is still ten stable releases below the minimum.
- The next engineering phase is a reviewed Motorola kernel stable update to at least 4.14.336, preferably the final maintained 4.14 LTS level if compatible, followed by kernel build, boot/DTBO rebuild, VINTF, and full hardware regression testing. This is a real target-branch blocker, not another packaging-only fix.

## 2026-07-18 Linux 4.14.336 and FCM 6 completion

- Kernel repository `kernel/motorola/sm6150` was genuinely updated from Linux 4.14.190 to final upstream Android-common 4.14.336. Merge commit `70f404ff7c1fb97460cef91e1f89d594a2959358` has parents local Motorola head `92a96be148a072185131f60977af463c918b58cd` and Android-common `014241ad77dda0eafbdf671d5b8e86917d8ec97e` (merge base `d2d05bcf4b4edf8d028fa420dee3c6644aa5b4ac`).
- The merge preserved Odessa/Motorola behavior while fixing reviewed semantic conflicts in USB gadget/networking, FFS, Qualcomm early-random/event-timer code, ARM64 CPU errata, and LPFC. The resulting kernel identifies as `4.14.336-perf+`; no KernelSU/SUSFS integration is present.
- FCM 6 configuration requirements were enabled in `vendor/odessa_defconfig`. Hidden `CONFIG_TRACE_GPU_MEM` is legitimately selected by the enabled Qualcomm KGSL driver rather than forced as a dummy setting.
- `CONFIG_HAVE_MOVE_PMD` and `CONFIG_HAVE_MOVE_PUD` are backed by the reviewed LineageOS 4.14 fast-`mremap` implementation and its extent/rmap correctness fixes, not fake capability flags. Provenance is the sequence used by `LineageOS/android_kernel_xiaomi_sm6125`: `c03090c08306`, `55aa9440e322`, `9c675f67ada9`, `7e84645f282f`, `994df5b67cca`, `52fe5a2c9c5c`, and `f54ef1f06039`.
- Motorola's experimental `CONFIG_SPECULATIVE_PAGE_FAULT` was disabled because fast PMD/PUD subtree moves otherwise retain a known use-after-free race. Other final FCM settings include binderfs, always-on BPF JIT, userfaultfd, software TTBR0 PAN, fs-verity signatures, static usermodehelper disablement, ext4 POSIX ACLs, and `CONFIG_RT_GROUP_SCHED=n`.
- The post-merge FCM/mremap/config delta is currently uncommitted in six kernel files: `arch/Kconfig`, `arch/arm64/Kconfig`, `arch/arm64/configs/vendor/odessa_defconfig`, `arch/arm64/include/asm/pgtable.h`, `drivers/gpu/msm/Kconfig`, and `mm/mremap.c`. `git diff --check` passes.
- Final HOST ONLY target-files archive: `lineageos/out/target/product/odessa/obj/PACKAGING/target_files_intermediates/lineage_odessa-target_files.zip`, 2,615,265,928 bytes, SHA-256 `6f80655466ccbd7cf9193bce23fb0b253b665760be3be304be27033c4b6f0f72`; ZIP integrity passes.
- Standalone verbose `check_target_files_vintf` definitively returns `COMPATIBLE` for kernel FCM 6 with Linux `4.14.336-perf+`. No compatibility check was bypassed.
- Final test-key A/B OTA: `lineageos/out/target/product/odessa/lineage-23.2-20260719-UNOFFICIAL-odessa.zip`, 1,028,374,656 bytes, SHA-256 `65d3a91433e470899f79c75386e771bd6d84b3d4cde28f0a06a7d0dd23280dee`; ZIP integrity and payload metadata checks pass. It is an unofficial `userdebug` development artifact signed with Android test keys, not a release artifact.
- Final boot artifact SHA-256 is `b3778bfeaa72aced813a9b04bda1878ab1c31c1e7447752e468a993432667737`; final DTBO SHA-256 is `be2e144cc4578577d1ae73ce28b924c302652b2ba7bd2d2e4d0495cbf9ff98e6`.
- No phone was contacted, booted, sideloaded, or flashed. The OTA is not approved for flashing: Phase 0 recovery gaps remain, and the new kernel/mremap/config behavior still requires physical-device validation across boot, storage/encryption, suspend, charging, USB, radio, Wi-Fi/Bluetooth, display/touch, audio, camera, fingerprint, sensors, recovery, and both A/B update slots.

## 2026-07-18 source checkpoint and Phase 0 inventory

- The previously uncommitted Android 16 compatibility work is now committed on local `lineage-23.2` branches: Odessa device `23809aa`; SM6150 common device `101bf343` and `ade40c34`; SM6150 kernel `98efff6a92e3` and `b9df0469a7a2` after merge `70f404ff7c1f`; SM6150 common vendor `73b5933`.
- No rebuild was performed because the validated artifacts were built from the exact source bytes that were subsequently committed. Existing hashes and ZIP integrity were rechecked, and verbose `check_target_files_vintf` again returned `COMPATIBLE` for Linux `4.14.336-perf+` and FCM 6.
- Read-only Android inventory reconfirmed `odessa`, `XT2087-1`, slot `_a`, A/B layout, dynamic partitions, file-based encryption, current bootloader/baseband, and the TequilaOS build. `/dev/block/by-name` and unprivileged `lpdump` provided the physical-name map and complete logical `super` layout without reading partition contents.
- Bootloader fastboot reconfirmed product `odessa`, slot `a`, two slots, `super` size 9,730,785,280 bytes, `is-userspace: no`, and `securestate: flashing_unlocked`. Motorola does not implement generic `getvar unlocked` on this bootloader.
- Fastbootd was verified with `is-userspace: yes`; logical `system_a`, `vendor_a`, and `product_a` were visible with sizes matching `lpdump`.
- The installed custom recovery booted and exposed ADB after its Enable ADB menu action. It reports the Android 11 Motorola vendor fingerprint `RPAS31.Q2-59-17-4-5-5`, display ID `TQ3A.230901.001`, and kernel `4.14.190-perf+`, but no Lineage Recovery/TWRP/OrangeFox version property. It returned successfully to TequilaOS and `sys.boot_completed=1`.
- No flash, erase, format, wipe, install, sideload, raw block read/write, or LineageOS boot occurred. The phone remained on TequilaOS.
- Phase 0 still requires the user-operated official Motorola Software Fix **Download-only** checkpoint on trusted Windows and completion of the physical TequilaOS hardware baseline. Software Fix must not run Rescue during package acquisition; Rescue is destructive and factory-resets the phone.
- Tracked details are in `docs/build-checkpoint-20260718.md`, `docs/phase-0-checkpoint.md`, `docs/phase-0-inventory.md`, and `docs/tequilaos-hardware-baseline.md`.

## 2026-07-19 official Android 11 firmware AVB validation

- HOST ONLY validation completed for `downloads/ODESSA_RETAIL_RPAS31.Q2_59_17_4_3_9_subsidy_DEFAULT_regulatory_DEFAULT_CFC.xml`; no phone command or source change was made. All 19 package payload MD5 values match `flashfile.xml`.
- Focused host `lpunpack` and `lpdump` targets built successfully. The nine sparse chunks reconstructed to a 9,730,785,280-byte raw `super`, SHA-256 `3701414cd149639d6e66089cee83ce20f5245797b63c71b3fd6e25513f82609e`.
- Both A/B metadata views are identical: liblp metadata 10.0, three metadata copies, no flags, 4,861,198,336-byte groups, populated `_a` product/system/vendor, a small `_b` system, and empty `_b` product/vendor.
- `avbtool verify_image --image vbmeta.img` verified the embedded SHA256/RSA-2048 signature, SHA-256 hashes for boot/DTBO/recovery, and SHA-256 hashtrees for extracted product/system/vendor. Flags are 0; rollback index is 16; public-key SHA-1 is `fd29248b78aa9d6427e8f569eda90be62b9fa0ee`.
- The package `super` size exactly matches the phone. Its populated `_a` logical sizes exactly match the phone's current `_b` sizes; current slot A and group-A sizing differ after later updates/custom ROM use. The package bootloader is dated 2022-08-18 and baseband matches the phone, but installed recovery identifies later Motorola build `...-4-5-5` and the running vendor patch is newer.
- Large generated reconstruction/extraction files were removed after verification; the downloaded package and host tool build outputs remain. Full commands, metadata, hashes, AVB descriptors, comparison, and cleanup are recorded in `docs/firmware-validation-rpas31-4-3-9.md`.
- Motorola Software Fix automatically identified the connected phone and selected this exact package; the user did not select a model/package manually, and no IMEI or serial was recorded. This establishes exact-device official provenance.
- The package is accepted as the stock recovery route: bootloader `...-220818` is newer than the phone's `...-220629`, baseband matches exactly, physical `super` size and A/B/liblp structure match, all manifest hashes pass, and complete AVB verification passes. Use only Motorola Software Fix Rescue if restoration becomes necessary; do not improvise a manual fastboot script or preemptively flash it.
- The destructive fallback procedure, prerequisites, expected result, and failure handling are documented in `docs/stock-restore-rpas31-4-3-9.md`. Phase 0's stock-package/restore-path blocker is resolved; remaining Phase 0 work is completion of the TequilaOS hardware baseline.

## 2026-07-19 Phase 0 completion with baseline limitations

- The user recalls that incoming/outgoing calls, incoming/outgoing SMS, airplane-mode service recovery, Bluetooth call audio/microphone, and proximity behavior previously worked on TequilaOS, but cannot repeat those tests now. They are recorded as `LIKELY`, not validated `PASS` results.
- Other unavailable hardware checks remain explicitly `UNTESTED`, and the known failure where only one rear camera worked remains `FAIL`. These limitations must be preserved in later LineageOS regression comparisons.
- Phase 0 is complete: exact identity/layout, official stock recovery package and procedure, non-sensitive partition inventory, bootloader fastboot, fastbootd, recovery, and the available TequilaOS behavioral baseline are documented.
- Completion of Phase 0 does not itself approve flashing. The next checkpoint is HOST ONLY review of the first-install artifacts, exact partition/install path, rollback readiness, and pre-flash checklist before proposing any device-changing command.

## 2026-07-19 first-install architecture review

- HOST ONLY review confirms Odessa uses separate 64 MiB A/B recovery partitions. The intended installation path is a standalone Lineage Recovery followed by recovery factory reset and ADB sideload of the A/B payload OTA. Do not assume `fastboot boot` support, use `fastboot update` with the OTA, or manually flash dynamic partitions.
- Standalone recovery candidate: `lineageos/out/target/product/odessa/recovery.img`, 67,108,864 bytes, SHA-256 `dd4e3350ac92278b42a7db13bbc2f778898a923b09ab48b6d1368886272c2d26`.
- The official LineageOS `copy-partitions-20220613-signed.zip`, SHA-256 `92f03b54dc029e9ca2d68858c14b649974838d73fdb006f9a07a503f2eddd2cd`, was downloaded and audited only. Its broad raw-`dd` loop can copy `fsg` and other protected partitions, and its official Lineage certificate is not trusted by this test-key recovery. It is not approved for sideloading, re-signing, or manual execution.
- Before any write, use the installed recovery only for a read-only SHA-256 comparison of a reviewed whitelist of non-sensitive A/B firmware partitions. If pairs match, omit firmware copying; if any differ, stop for partition-specific review rather than copying automatically.
- Full rationale, artifacts, prohibited paths, and the immediate preflight are in `docs/first-install-checkpoint.md`. No phone was contacted and no image was flashed, booted, wiped, formatted, installed, or sideloaded.

## 2026-07-19 read-only A/B firmware comparison

- The connected phone was reconfirmed as `odessa`, SKU `XT2087-1`, active slot A, two slots, bootloader fastboot, and `securestate: flashing_unlocked`; battery was 100%.
- The already installed recovery exposed root ADB. It streamed 19 reviewed non-sensitive A/B low-level firmware partition pairs through `sha256sum` without saving partition contents.
- `dsp`, `multiimgoem`, and `multiimgqti` matched across slots. The other 16 reviewed pairs differed: `abl`, `aop`, `bluetooth`, `cmnlib`, `cmnlib64`, `devcfg`, `hyp`, `keymaster`, `logo`, `modem`, `qupfw`, `storsec`, `tz`, `uefisecapp`, `xbl`, and `xbl_config`.
- Sensitive or shared storage including `fsg`, `prov`, `persist`, `modemst1`, `modemst2`, `cid`, `utags`, and `utagsBackup` was excluded and not read. Boot/recovery/DTBO/vbmeta and dynamic partitions were outside this low-level comparison.
- No partition was copied or written. The phone returned to TequilaOS on slot A and `sys.boot_completed=1` was confirmed.
- The mismatch means firmware copying cannot be omitted merely because the slots are assumed identical, but hashes alone do not establish which slot is newer or safe to copy. The generic `copy-partitions` package remains prohibited pending HOST ONLY partition-specific provenance review. Full hashes and scope are in `docs/firmware-slot-comparison-20260719.md`.

## 2026-07-19 live first-install preflight recheck

- Read-only live checks reconfirmed `odessa`, SKU `XT2087-1`, model Motorola g(9) plus, active slot A, two slots, battery 100%, and stable Android ADB plus bootloader-fastboot USB detection.
- Direct bootloader fastboot reported `is-userspace: no` and `securestate: flashing_unlocked`.
- The recovery candidate remains 67,108,864 bytes, SHA-256 `dd4e3350ac92278b42a7db13bbc2f778898a923b09ab48b6d1368886272c2d26`.
- The A/B OTA remains 1,028,374,656 bytes, SHA-256 `65d3a91433e470899f79c75386e771bd6d84b3d4cde28f0a06a7d0dd23280dee`.
- The phone was returned to TequilaOS on slot A and `sys.boot_completed=1` was confirmed. No partition access, flash, erase, format, wipe, install, or sideload occurred.
- This recheck does not resolve or authorize synchronization of the differing A/B low-level firmware partitions.

## 2026-07-19 failed first-install attempt and automatic fallback

- The user independently sideloaded the LineageOS 23.2 OTA from the previously installed Tequila/Pixys-derived recovery without first installing Lineage Recovery. Without rebooting recovery after the A/B OTA, they then sideloaded MindTheGapps 16 and Magisk 30.7. The attempted LineageOS boot looped and the bootloader automatically returned to TequilaOS Android 14 on slot A.
- The user confirms that recovery Factory reset / Format data was performed before the sideload, so retained TequilaOS userdata is not a plausible explanation for this failed boot.
- Read-only bootloader inspection confirmed slot A remains successful and bootable. Slot B is not successful, is marked unbootable, and has zero retries remaining. The bootloader remains `flashing_unlocked`; no slot flags were manually changed.
- The exact images extracted from the OTA payload match the complete installed slot-B `boot`, `recovery`, and `dtbo` partitions byte-for-byte. The first 8,192 bytes of `vbmeta_b` also match the OTA's complete vbmeta image. This proves the base OTA wrote those four slot-B artifacts and that Magisk did not patch `boot_b`.
- No kernel panic record survived in pstore. The old recovery has no persistent `/cache/recovery` or `/data/misc/recovery` install log; its current `/tmp/recovery.log` only covers the later diagnostic recovery boot. A raw copy is retained only in the ignored build-log directory and contains sensitive device properties, so it must never be committed or shared unredacted.
- The loose current `out/target/product/odessa/{boot,recovery,dtbo}.img` files do not match the OTA payload images, despite prior notes treating their hashes as final. Future install verification must use images extracted from the exact signed OTA or its exact target-files input, not mutable loose `out/` artifacts.
- The phone was returned to TequilaOS on slot A. Do not repeat the three-ZIP sequence. Before another attempt, establish whether userdata was factory-reset, review the old recovery's A/B add-on behavior, resolve or explicitly control the known low-level firmware mismatch between slots, and test the unmodified base LineageOS OTA before GApps or Magisk.

## 2026-07-19 failed Lineage Recovery tests

- The user first used bootloader fastboot's unsuffixed aliases while slot B was selected to flash the mutable loose `out/target/product/odessa/dtbo.img` and `recovery.img`. Their hashes were `be2e144c...f98e6` and `dd4e3350...2d26`; they did not match slot B's existing target-files vbmeta descriptors. Because B was already marked unbootable, the initial Recovery selection fell back to Pixys recovery A and was not a valid Lineage Recovery test.
- A controlled `set_active b` plus `fastboot reboot recovery` with those loose images genuinely looped before ADB. Slot A was restored immediately. No pstore record survived.
- The exact target-files images were extracted to the ignored `lineageos/.downloads/install-images-20260719/`: DTBO `8d807087...7293`, recovery `3c43c91f...7606`, and vbmeta `3495eda8...751e`. The exact vbmeta was already unchanged on B. Explicit `dtbo_b` and `recovery_b` writes restored an internally AVB-matched target-files set.
- A second controlled slot-B Recovery boot with the exact matched set also looped before ADB and eventually returned to bootloader. This rules out the loose-image/vbmeta mismatch as the sole cause. Slot A was restored and TequilaOS setup remains reachable through the booting Pixys recovery A.
- Host artifact review found Lineage and Tequila external DTBO table payloads byte-identical; generic boot header layout also matches. Both failed Lineage Android and recovery images share the same untested Linux 4.14.336 kernel and embedded base DTB, while working Tequila/Pixys use 4.14.190. However, every failed test has also used slot B, whose 16 reviewed low-level firmware/boot-chain pairs differ from A.
- The safest next discriminator is to read the exact booting Pixys `recovery_a`, `dtbo_a`, and `vbmeta_a` to ignored host files, verify them, then place only that known-working stack on failed slot B for one recovery test. If Pixys also fails on B, prioritize slot-B firmware provenance; if it boots, prioritize a pre-merge 4.14.190 hybrid Lineage Recovery and kernel bisection. Do not synchronize low-level firmware speculatively.
- That discriminator was completed successfully. The exact live Pixys A-slot stack was saved only under ignored `lineageos/.downloads/pixys-live-slot-a-20260719/`: recovery `e33b3392...d402`, DTBO `8e22e62e...13ad`, and full padded vbmeta partition `5a91c30b...471c`. Host copies matched direct device hashes.
- The live Pixys vbmeta uses the same test-key public key as Tequila/Lineage but flags `3` and rollback index `0`; fastboot warned `vbmeta_b anti rollback downgrade, 0 vs 16` but accepted it on the unlocked bootloader. These settings are diagnostic only and are not acceptable for Lineage release configuration.
- After copying only the known-working Pixys recovery/DTBO/vbmeta stack to B and marking B active, Pixys recovery booted fully on slot B with ADB and Linux `4.14.190-perf+`. This proves slot B's differing low-level firmware is sufficient to enter Linux and recovery userspace. The Lineage 4.14.336 kernel/embedded base DTB path is now the primary cause of both failed Lineage recovery and Android boots.
- Slot A was restored active immediately. The next device test must use a host-built one-variable Lineage Recovery diagnostic with the pre-merge `92a96be148a0` Linux 4.14.190 kernel while preserving the exact failed Lineage recovery ramdisk, embedded DTB, DTBO, header, and command line where possible. Do not perform more full-ROM, GApps, Magisk, or firmware-copy tests first.
- That one-variable diagnostic was built and tested successfully. Artifact directory: ignored `lineageos/.downloads/diagnostic-recovery-4.14.190-20260719/`. Recovery SHA-256 `283c31e3...0ca3`, DTBO `8d807087...7293`, and matching flags-0 vbmeta `51abd928...7d13`; complete AVB descriptor/hashtree verification passed.
- The diagnostic replaced only the exact failed Lineage Recovery's kernel payload with a genuine `4.14.190-perf+` kernel built from pre-merge commit `92a96be148a0`. Its Lineage ramdisk, embedded base DTB, embedded recovery DTBO, separate DTBO, header v2 metadata, command line, and OS metadata remained byte-identical. Kernel repository branch/HEAD were restored cleanly to `lineage-23.2` / `b9df0469a7a2` after the host build.
- On slot B the diagnostic reached the purple Lineage Recovery UI and, after manually enabling ADB, exposed root ADB with `ro.boot.slot_suffix=_b` and `uname -r=4.14.190-perf+`. Installed recovery/DTBO/vbmeta hashes matched the diagnostic artifacts exactly. This conclusively localizes the original pre-ADB loop to the current 4.14.336 kernel code/config transition, not the Lineage recovery ramdisk, embedded base DTB, external DTBO, AVB composition, slot-B firmware, or recovery image header/layout.
- A successful-recovery dmesg and pmsg were saved only under the ignored build-log directory and may contain device identifiers; never commit or share them unredacted. Slot A was restored and TequilaOS remains the known-good boot.
- The next narrowing test should build the same one-variable recovery with merge commit `70f404ff7c1f` (4.14.336 before the later mremap/FCM-config commits). If it fails, bisect the stable merge; if it boots, isolate `98efff6a92e3` versus `b9df0469a7a2` and the small final config delta.
- The merge-state diagnostic was built from the actual merge commit `70f404ff7c1fd64f2a3c84bc6ae617cdd9922312` with genuine `4.14.336-perf+`, preserving the same exact Lineage recovery components. Ignored artifacts: recovery `90f6aacf...93c51`, DTBO `8d807087...7293`, and flags-0 matching vbmeta `e6e9fe20...72d6e`; full AVB verification passed and the kernel repository was restored cleanly afterward.
- The merge-state recovery bootlooped and automatically returned to bootloader before reaching the Lineage Recovery UI. Slot A was restored. Therefore the regression is already present in the large `92a96be148a0` to `70f404ff7c1f` Android-common 4.14.336 merge; post-merge commits `98efff6a92e3` and `b9df0469a7a2` are not required to trigger it.
- Stop further ROM/add-on/device tests until this kernel merge is narrowed and fixed. Continue with HOST ONLY audit/bisection of the stable merge, prioritizing early ARM64/core initialization and reviewed merge-conflict resolutions. Recovery-only slot-B tests remain the minimal hardware oracle after each verified candidate; always restore slot A immediately.
- A source audit found a genuine semantic incompatibility in the merge: Qualcomm `init_random_pool()` calls `add_hwgenerator_randomness()` during `setup_arch()`, before scheduler initialization, while the imported RNG implementation may throttle with `schedule_timeout_interruptible()` immediately after the 4096-bit SCM result makes the CRNG ready. The kernel now has an uncommitted upstream-style `sleep_after` argument: normal hwrng/ath9k callers pass `true`, Qualcomm early random passes `false`, preserving all entropy mixing/credit while avoiding illegal pre-scheduler sleep.
- HOST ONLY build/AVB verification passed for this final-4.14.336 RNG-fixed diagnostic. Ignored artifacts: recovery `a7c682b7...e7747`, DTBO `8d807087...7293`, and flags-0 vbmeta `df34d249...227cd`. The five-file source diff is clean and remains uncommitted.
- The RNG-fixed diagnostic still bootlooped before recovery UI. Therefore the fix is correct but not sufficient; at least one additional stable-merge regression remains. Slot A was restored. The next useful synthesized boundary candidate is Android-common 4.14.317 plus the RNG fix, using the same recovery-only hardware oracle.
- HOST ONLY synthesis/build of the 4.14.317 boundary candidate completed in a disposable full-history repository. Full ancestry and `git fsck` passed; replay of the final 4.14.336 merge reproduced `70f404ff` byte-for-byte before rerere was used. Candidate source commit `0ce77b2bbc703c0c3ff576713acd14fe777c2b07`, tree `15410d994bae278569cf4fa39bcbe737f2c119e6`, combines Motorola base `92a96be148a0`, authoritative Android-common 4.14.317 `89ea220374c2`, reviewed conflict resolutions, and the RNG fix. Kernel release is genuine `4.14.317-perf+`.
- Ignored candidate directory: `lineageos/.downloads/diagnostic-recovery-4.14.317-rng-fix-20260719/`. Recovery is 67,108,864 bytes, SHA-256 `f48fb65a957096cda9dd836e70dbf992e5d752853aedde349e574ee0c54392b9`; exact DTBO SHA-256 `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; matching flags-0 vbmeta SHA-256 `5c70fd617b3c15a9f3b6285d858932bbcda604013de98f55b7da66b0c483ffc8`; kernel Image SHA-256 `3673a08b31256f70c6ca53a6328609d061f9c2cf5cc07a6c4568531317f9955c`.
- Candidate recovery structure is one-variable verified against the exact failed Lineage template: ramdisk, embedded DTB, embedded recovery DTBO, external DTBO, header, cmdline, and OS metadata are unchanged; complete AVB descriptors/hashtrees pass. Provenance and conflict notes are in that directory's `SOURCE-PROVENANCE.md`; build/repack logs are in ignored `lineageos/.downloads/build-logs/`.
- Immediate next step is a controlled recovery-only slot-B test of this 4.14.317 candidate after re-verifying that slot A/TequilaOS is active and bootable. If 4.14.317 boots, narrow the remaining regression to Android-common 4.14.318–4.14.336. If it fails, narrow it to 4.14.191–4.14.317. Always restore slot A immediately; do not install ROM/GApps/Magisk or copy firmware during kernel bisection.

## 2026-07-19 Android-common 4.14.317 boundary candidate

- HOST ONLY synthesis completed in a full-history disposable repository at `/tmp/opencode/sm6150-boot-bisect`; no phone command was issued and the working kernel repository was not changed.
- Authoritative Android-common `refs/heads/deprecated/android-4.14-stable` verified milestone `89ea220374c204a275482c85b75a2ad968b46ea7` as `Merge 4.14.317 into android-4.14-stable`, with full ancestry to final `014241ad77dda0eafbdf671d5b8e86917d8ec97e`. The Motorola merge base is `d2d05bcf4b4edf8d028fa420dee3c6644aa5b4ac`.
- Rerere was trained only after an `ort` replay of the final 4.14.336 merge produced the exact known tree `9d47db854c8095b0fa4e5b8658504fe4bac21b29`. The 4.14.317 merge retained reviewed Motorola behavior; DWC3 was manually adapted using only fixes present by 4.14.317, and Qualcomm `event_timer.c` was updated for the cached-rbtree timerqueue API exposed by a clean semantic conflict.
- Final disposable source commit is `0ce77b2bbc703c0c3ff576713acd14fe777c2b07`, tree `15410d994bae278569cf4fa39bcbe737f2c119e6`. Its merge commit is `cb1621aef94e2e698a23d3758e22277b48e25e9f`; RNG fix commit is `799e4328e2ccc0c686b3a75c35792fb87c002046`.
- Fresh Android clang `r563880c`, `LLVM=1 LLVM_IAS=1 -j8` build succeeded with `vendor/odessa_defconfig` and kernel release `4.14.317-perf+`. Image: 33,183,768 bytes, SHA-256 `3673a08b31256f70c6ca53a6328609d061f9c2cf5cc07a6c4568531317f9955c`.
- Ignored artifact directory: `lineageos/.downloads/diagnostic-recovery-4.14.317-rng-fix-20260719/`. Recovery SHA-256 is `f48fb65a957096cda9dd836e70dbf992e5d752853aedde349e574ee0c54392b9`; exact target-files DTBO remains `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; flags-0 test-key vbmeta is `5c70fd617b3c15a9f3b6285d858932bbcda604013de98f55b7da66b0c483ffc8`. Full AVB hash/hashtree verification and recovery component byte comparisons passed.
- A prerequisite-aware source bundle and complete resolution notes are stored with the artifacts. The working kernel remains `lineage-23.2` at `b9df0469a7a2d7dbce8e6795d035088c4bbe6f85` with only the intended five RNG files modified, diff SHA-256 `c23d55729a2576494285f6412849669ba2243c8a16ef4305bbc1e811a276b286`.

## 2026-07-19 early-kernel debugging research

- Odessa already enables ramoops console/panic/pmsg persistence (`CONFIG_PSTORE`, `CONFIG_PSTORE_CONSOLE`, `CONFIG_PSTORE_PMSG`, and `CONFIG_PSTORE_RAM`) in a reserved `0xbf800`-byte region at physical address `0xaf000000`. Lineage Recovery mounts pstore at `/sys/fs/pstore`.
- A successful 4.14.190 recovery log shows ramoops registering at about 0.149 seconds. Repeated failed 4.14.336 tests left no pstore record, so the regression likely hangs or resets before ramoops registration, or without a panic path that can dump the kernel log. Recovery userspace and ADB cannot observe that interval.
- The kernel has a real SM6150 GENI debug UART at `0x880000`, alias `serial0`, on GPIO16/GPIO17, and the Motorola overlay enables its DT node. However, Odessa disables `CONFIG_SERIAL_MSM_GENI_CONSOLE`, supplies no Linux `console=`/`earlycon` argument, and disables `CONFIG_KGDB`; ordinary USB ADB is therefore not a live early-kernel console or debugger.
- True live KGDB/KDB debugging would require a dedicated debug build plus a verified voltage-compatible UART connection to the phone's actual board pads. Source establishes the SoC GPIOs but not a safe physical Odessa test-point pinout. Do not probe or connect board pads without an authoritative schematic and voltage/ground verification.
- Qualcomm memory-dump, minidump, download-mode, and EUD support exists in the kernel, but retail firmware/debug policy and specialized Qualcomm collection tooling may block it. Do not enter EDL/download mode, read rawdump, or alter dump cookies as an exploratory step; preserve fastboot and the accepted Motorola restore path.
- The lowest-risk next diagnostic remains the prepared 4.14.317 recovery-only boundary test. If additional logging is needed, use a one-variable recovery kernel with `ignore_loglevel`, `loglevel=8`, `initcall_debug`, warning/oops-to-panic conversion, and lockup detection, then read pstore immediately from the known-good A-slot recovery. Persistent ftrace is possible only after enabling `CONFIG_FUNCTION_TRACER`/`CONFIG_PSTORE_FTRACE` and allocating a ramoops ftrace region, and it still cannot capture execution before ramoops registration.

## 2026-07-20 CosmicFresh binary evaluation

- The untrusted Telegram archive was copied to ignored `downloads/CosmicFresh-R5-FPC-KSU-SUSFS.zip` and extracted only for HOST ONLY static inspection under `downloads/CosmicFresh-R5-FPC-KSU-SUSFS/`. Archive SHA-256 is `2987cde4dc9c91fd3bad2c912783c8f1aba5a9f25bb29b81a1c2df39798b8e05`; no bundled executable or script was run and no phone was contacted.
- It is an AnyKernel3 package with a prebuilt `Image.gz`, base DTB, DTBO, installer scripts, and static tools, but no kernel source. The decompressed ARM64 image is 33,472,640 bytes, SHA-256 `76970d800a9cb5fe809382fcd32ba2c75f999e1eb4d18a0154c65822fdd2b5a4`, and identifies as genuine Linux `4.14.206-perf`, `CosmicFresh-R5`, built 2026-07-16 with a custom LLVM/Clang 23 toolchain.
- The binary contains active KernelSU and SUSFS implementations and disables LoadPin and Yama. It must not be adopted or shipped in the unrooted base ROM. The installer is also unsafe as a project installation path because it targets unsuffixed `boot`, sets `is_slot_device=0` on an A/B device, and imposes no Android-version or patch-level constraint. Do not flash the ZIP.
- Its included DTB and DTBO do not match the working Tequila artifacts: Cosmic DTB SHA-256 `fe52f6fc7bd49507878ba1da7bdde22623dea00ed9dde11b3a1c3ef76a8e7fea`; Cosmic DTBO SHA-256 `22263f0269d3d9a438790a94c26c03cd8e3c5c85579124e5726fa53b8a6a04e9`; Tequila DTBO SHA-256 `8e22e62e3ea1960f2413355ee589ad7811029d6ce911e292f5259c1a4b7413ad`. A direct one-variable test cannot use this package unchanged.
- The 2024 XDA CosmicFresh Odessa thread points to public source `ViShal69x/CosmicFresh-Liber`, now redirected to `Theimposter65/CosmicFresh-Liber`, branch `odessa`, tip `d41bc730e40e416deeb62b4bdddc58fc2e6864aa`. That tree is also Linux 4.14.206 and contains Android-common's real `Merge 4.14.206` commit `7b43d7449c76`, so it may provide conflict-resolution clues for the current stable-update investigation.
- The public source is not matching source for this exact binary: its tip predates the binary by more than two years and contains no KernelSU/SUSFS code. It is also not a drop-in baseline; against pre-update Motorola commit `92a96be148a0`, the merge base is `4fad07ec1ed1`, with 7,671 Cosmic-only and 4,823 Motorola-only commits. Treat it only as comparative evidence while the prepared 4.14.317 recovery boundary remains the next controlled hardware test.

## 2026-07-20 kernel debug branch publication

- The reviewed Qualcomm early-RNG correction was committed as `41038075962c29364e02cbe5a548904b1f88e028` (`random: Avoid scheduler sleep during early Qualcomm init`). The local kernel working branch remains `lineage-23.2` and is clean at that commit.
- The failing 4.14.336 integration, including the stable merge, mremap backport, FCM 6 configuration, and RNG correction, is published for review at branch `wip/odessa-4.14.336-boot-debug` in `ARLBR10/android_kernel_motorola_sm6150`; its tip is `41038075962c29364e02cbe5a548904b1f88e028`.
- The synthesized failing 4.14.317 boundary, including the reviewed merge resolutions, RNG correction, and Qualcomm event-timer adaptation, is published at branch `wip/odessa-4.14.317-boot-debug`; its tip is `0ce77b2bbc703c0c3ff576713acd14fe777c2b07`.
- The remote `lineage-23.2` branch remains unchanged at the working 4.14.190 baseline `92a96be148a072185131f60977af463c918b58cd`. The two published branches are explicitly WIP/debug history and must not be treated as bootable release kernels.

## 2026-07-20 Android-common 4.14.317 recovery boundary result

- The controlled recovery-only slot-B test of the verified `4.14.317-perf+` candidate (`f48fb65a957096cda9dd836e70dbf992e5d752853aedde349e574ee0c54392b9`) bootlooped before the Lineage Recovery UI or ADB, matching the prior 4.14.336 result.
- Bootloader preflight before the test verified product `odessa`, active successful slot A, `securestate: flashing_unlocked`, slot B with seven retries, and 4.408 V battery voltage. Only `dtbo_b`, `recovery_b`, and `vbmeta_b` were written; userdata, dynamic partitions, firmware, and slot A were not changed. The diagnostic vbmeta emitted the expected unlocked-device rollback-index warning (`0` versus `16`).
- Slot A was immediately made active again. Pixys recovery ADB then confirmed `ro.boot.slot_suffix=_a`, Android 11 Motorola recovery fingerprint `RPAS31.Q2-59-17-4-5-5`, and known-good kernel `4.14.190-perf+`.
- This narrows the stable-update regression to Android-common Linux `4.14.191` through `4.14.317`, inclusive. The post-merge mremap, FCM defconfig, and early-RNG commits are not required to reproduce the failure. The early-RNG correction remains valid but insufficient.
- A host-only exact midpoint synthesis for Android-common `4.14.254` was prepared at ignored `lineageos/.downloads/diagnostic-recovery-4.14.254-rng-fix-20260720/`, but it produced no flashable artifact. Exact upstream `mm/memory.c` at that boundary conflicts with Motorola's independently advanced clean-merged MM headers. Do not substitute later MM code merely to make the midpoint build: that would invalidate the bisection result. Provenance is recorded in its `SOURCE-PROVENANCE.md`; the working kernel tree remains clean at `41038075962c29364e02cbe5a548904b1f88e028`.

## 2026-07-20 Android-common 4.14.254 SPF-off recovery boundary result

- The first exact 4.14.254 midpoint merge combined upstream `mm/memory.c` with Motorola's enabled downstream speculative-page-fault (SPF) headers and callers, making the candidate unbuildable. This was a merge-resolution incompatibility, not an upstream 4.14.254 defect. The final Android 16 configuration already disables SPF because it is incompatible with later page-table movement work.
- A bounded corrected candidate retained `mm/memory.c` byte-identical to Android-common 4.14.254 `5b2d33ae`, explicitly disabled `CONFIG_SPECULATIVE_PAGE_FAULT`, and added only documented compatibility bridges for independently advanced Motorola MM/memcg/swap interfaces. It also retained the older-API equivalent early Qualcomm RNG correction. Source tip `f14359c8f5cc269b8be9231eebcdead0b1d342b7`; full provenance and bundle are ignored under `lineageos/.downloads/diagnostic-recovery-4.14.254-spf-off-rng-fix-20260720/`.
- The corrected 4.14.254 candidate built as `4.14.254-perf+`; Image SHA-256 `60e765817255d1cad3b23729e4501b9eea0b7f661fc8c7669f14600738923d9f`; recovery SHA-256 `b652196aa20df40871d3de052b02e4c7fac9033d241ced5d1353f6da4b2becb7`; DTBO SHA-256 `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; diagnostic flags-0 vbmeta SHA-256 `fb6139d1180e80ed7dacbfc233f47f5425edb62c7c50c88775066adfd1860ee2`. AVB, hashtree, and unchanged recovery-component comparisons passed.
- The controlled slot-B recovery-only test booted fully into Lineage Recovery. Root recovery ADB verified `odessa`, `ro.boot.slot_suffix=_b`, and `4.14.254-perf+`; installed recovery and DTBO hashes matched their diagnostic artifacts. The padded on-device vbmeta partition's whole-partition hash differs from the 8 KiB image as expected.
- Slot A was immediately restored active and TequilaOS ADB verified `odessa`, `ro.boot.slot_suffix=_a`, `sys.boot_completed=1`, and known-good `4.14.190-Amber`. No userdata, dynamic partition, firmware, or slot-A image was modified.
- The boot regression is now narrowed to Android-common Linux `4.14.255` through `4.14.317`, inclusive. The next valid binary-search boundary is an exact Android-common 4.14.286 candidate using the same bounded SPF-off/MM compatibility approach and recovery-only slot-B oracle.

## 2026-07-20 Android-common 4.14.286 midpoint build blocker

- The authoritative Android-common 4.14.286 milestone is `e1c62d43d5e078cd7391fddb929ef41ebede7a72` (`Merge 4.14.286 into android-4.14-stable`). A host-only candidate retained this exact `mm/memory.c` (SHA-256 `2abb8a7dd65a6c42ff5aab03e8dd665a1dc6b481fb39dcb8de6d0152094e9277`), retained the early-RNG correction, and disabled SPF.
- It did not build with Android clang because separately advanced Motorola interfaces conflict with the exact 4.14.286 stable code in RNG consumers, socket fragments, IRQ APIs, IOMMU `dev_archdata`, and DVB demux. Do not borrow their 4.14.336 versions: doing so would invalidate this boundary candidate. No Image, recovery, DTBO, vbmeta, AVB verification, or device test was produced.
- Provenance and failed logs are ignored in `lineageos/.downloads/diagnostic-recovery-4.14.286-spf-off-rng-fix-20260720/`. The next work is to adapt each interface using only code valid at or before 4.14.286, then rebuild this exact midpoint; no phone or working kernel-tree change occurred.

## 2026-07-20 Android-common 4.14.286 synthesis blocker

- HOST ONLY. Android-common's authoritative `Merge 4.14.286 into android-4.14-stable` milestone is `e1c62d43d5e078cd7391fddb929ef41ebede7a72`, a full-history ancestor of final Android-common `014241ad77dda0eafbdf671d5b8e86917d8ec97e`; the Motorola merge base remains `d2d05bcf4b4edf8d028fa420dee3c6644aa5b4ac`.
- A disposable worktree advanced the known booting bounded 4.14.254 candidate `f14359c8f5cc269b8be9231eebcdead0b1d342b7` toward the exact 4.14.286 milestone while preserving Android-common `mm/memory.c` byte-identically and retaining SPF-off plus the old-API Qualcomm early-RNG correction.
- Android clang r563880c / clang 21 did not build an Image. The independent Motorola/Android interface skew now includes random notifier/API consumers, socket-fragment APIs, IRQ handler signatures, IOMMU `dev_archdata`, and DVB demux interfaces. Importing later 4.14.336 resolution files or broad unrelated Motorola replacements would invalidate this bisection boundary, so no Image, recovery, DTBO, vbmeta, AVB verification, or SHA-256 artifact was produced.
- The ignored directory `lineageos/.downloads/diagnostic-recovery-4.14.286-spf-off-rng-fix-20260720/` contains provenance and all failed build logs. No phone command was issued; the Lineage working tree and published branches were not modified.

## 2026-07-20 Android-common 4.14.286 recovery packaging

- The prior 4.14.286 build blocker is superseded for packaging purposes: the exact supplied 4.14.286 SPF-off/RNG-fix Image was HOST-ONLY packaged into the ignored `lineageos/.downloads/diagnostic-recovery-4.14.286-spf-off-rng-fix-20260720/` candidate without modifying the main kernel worktree or contacting a phone.
- The one-variable diagnostic uses the exact failed Lineage Recovery template, preserving its header v2 metadata, ramdisk, embedded base DTB, embedded recovery DTBO, cmdline, OS metadata, and established external DTBO. Only the kernel payload, its recovery AVB footer, and the dependent top-level vbmeta differ.
- Artifact hashes: Image `e6fbfdfcbd4e22a85e608de238ed26ac72388e92937272f4959d5b46f4755022`; recovery `be15f14f60d354ed629331b23860b54f9bc4fa4b191e009bdb52d5cbe9467b3b`; DTBO `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; flags-0 test-key vbmeta `ee9f28677e609f427b51fd48696ee192a175e4d86ab1cd2dda50903690989ce6`.
- `avbtool verify_image` passed for recovery and DTBO. `avbtool verify_image --follow_chain_partitions --accept_zeroed_hashtree` passed for vbmeta with boot, DTBO, recovery, product, system, and vendor, including all product/system/vendor hashtrees. Full commands, descriptor outputs, hashes, and byte-comparison results are in the candidate `SOURCE-PROVENANCE.md` and adjacent ignored log files.
- This is package-verified only and has not been tested on hardware. Any recovery-only test remains separately authorized device-changing work.

## 2026-07-20 Android-common 4.14.282 recovery boundary result

- HOST ONLY synthesis/build/package completed for the exact Android-common `Merge 4.14.282 into android-4.14-stable` milestone `1f161a096b52aff01e5ababb9da7e76e5e4e12ff`. Candidate source commit is `2cfed6f0b1c45932868990ab79fa70c5b6cfd5c8`, tree `6dc3c65039601519001b3cf43f620d4a9182eaef`; disposable worktree `/tmp/opencode/sm6150-4.14.282-bisect`.
- The bounded candidate preserved Android-common `mm/memory.c` byte-identically (SHA-256 `2abb8a7dd65a6c42ff5aab03e8dd665a1dc6b481fb39dcb8de6d0152094e9277`), kept speculative page fault disabled, and retained the boundary-valid Qualcomm early-RNG correction. The only 4.14.282 merge conflict was `drivers/mmc/core/mmc_ops.c`, resolved using the established 4.14.278 boundary state without later stable source.
- Android clang r563880c built kernel release `4.14.282-perf+`; Image SHA-256 `29f8a47d2d0d75d3b06c578f983b314baafe91538a9e323b4a696cbbbbf65a1f`. Candidate directory is ignored at `lineageos/.downloads/diagnostic-recovery-4.14.282-spf-off-rng-fix-20260720/`.
- Recovery artifact SHA-256 is `fcb637b1e2702002f1d6d6a538784f7d4900ea236bd300f12d259ce31f0a3226`; DTBO is `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; diagnostic flags-0 vbmeta is `e5ccbfc3d96e81bc2c6f56a25f01edc389e9da09dfab122a95f84e42cf7d8bdb`. SHA256 and complete AVB verification passed.
- Live preflight verified `odessa`, Android fully booted on successful slot A, known-good `4.14.190-Amber`, two slots, `securestate: flashing_unlocked`, bootloader fastboot, and battery voltage about 4.418 V. Only `dtbo_b`, `recovery_b`, and `vbmeta_b` were written; the expected unlocked-device vbmeta rollback warning (`0` versus `16`) occurred. No userdata, dynamic partition, firmware, or slot-A image was modified.
- The 4.14.282 recovery-only slot-B test returned to the bootloader before the Lineage Recovery UI or ADB. Slot A was immediately restored active and Android confirmed `odessa`, `_a`, `sys.boot_completed=1`, and `4.14.190-Amber`.
- This is a FAIL result and narrows the stable-update regression to Android-common Linux `4.14.279` through `4.14.282`, inclusive, using the established 4.14.278 pass and 4.14.286 fail. Do not repeat the full-ROM, GApps, Magisk, or firmware-copy tests during this bisection.

## 2026-07-20 Android-common 4.14.282 repeat recovery boot

- The verified 4.14.282 candidate was flashed a second time from bootloader fastboot after preflight confirmed product `odessa`, current slot A, `securestate: flashing_unlocked`, bootloader fastboot, and 4.419 V battery. The artifact SHA256 gate passed before flashing.
- Only explicit `dtbo_b`, `recovery_b`, and `vbmeta_b` writes were performed, followed by `set_active b` and `reboot recovery`. The bootloader again warned about the diagnostic vbmeta rollback index (`0` versus `16`) and accepted it.
- On the repeat attempt, the user visually confirmed that the purple Lineage Recovery UI booted successfully. This confirms that the 4.14.282 kernel can reach recovery; the earlier bootloader return was not reproducible and should not be treated as the sole hardware result without further controlled repetition.
- Recovery ADB did not enumerate on the host after the user enabled ADB in the recovery menu and reconnected the USB cable. The host saw neither an ADB device nor a USB Motorola/Qualcomm/Android device, so `ro.boot.slot_suffix`, `uname -r`, and installed-partition hashes could not be collected from recovery.
- No second recovery retry or additional flash was made. At the user's request, no verification/rollback command was performed after the visual boot; the phone may remain in slot-B recovery. Before normal use, select recovery's Reboot to bootloader option and restore known-good slot A with `fastboot set_active a` followed by `fastboot reboot`.

## 2026-07-20 Android-common 4.14.270 recovery candidate

- The user reported that the `4.14.286` recovery result failed, narrowing the working bisection interval to `4.14.255` through `4.14.286`. The next midpoint is therefore `4.14.270`.
- HOST ONLY synthesis/build/package completed in disposable worktree `/tmp/opencode/sm6150-4.14.270-bisect`; no `adb` or `fastboot` command ran and the normal kernel worktree remains clean at `41038075962c29364e02cbe5a548904b1f88e028`.
- Exact source boundary is Android-common commit `e1a777beeb7da7133bf8c4c8244c83e3f12debbe` (`Merge 4.14.270 into android-4.14-stable`) from Motorola parent `92a96be148a072185131f60977af463c918b58cd`. Candidate source commit is `f92df260239f08c413edcfeb96656c3eda608e85`, tree `e41afee7d926fdbc6151a34b3e22409ad783c68d`.
- The bounded configuration disables speculative page fault and carries the boundary-valid Qualcomm early-RNG fix. `mm/memory.c` is byte-identical to upstream 4.14.270, SHA-256 `ce15bbd665a23a60ef1af9c0dab662a093935338c9fd0d7ee35083873ea827cf`.
- Android clang r563880c built `4.14.270-perf+` successfully. Ignored candidate directory: `lineageos/.downloads/diagnostic-recovery-4.14.270-spf-off-rng-fix-20260720/`.
- Artifact hashes: Image `ef79b4c6b966319ddea44ece5f59b60acb7fe517e12d1130d89abe5c2f6a3fd0`; recovery `3c9a76a406c788ea26c6d16f229d86822e787ea39940e25823d5517234388439`; DTBO `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; flags-0 test-key vbmeta `206596e2acf5096a5b210ccf9a2a3ecbdeea7193e4fb6dbb7f70ba1e9eb50c60`.
- The artifact gate (`SHA256SUMS.txt`) passed. AVB verification passed for recovery, DTBO, and top-level vbmeta including boot/DTBO/recovery descriptors plus product/system/vendor hashtrees. Recovery component comparisons confirm that only the kernel, recovery AVB footer, and dependent vbmeta differ from the exact failed Lineage Recovery template.
- This candidate has no hardware result. The next action requires explicit permission for the controlled destructive Slot-B recovery-only procedure: write only `dtbo_b`, `recovery_b`, and `vbmeta_b`, select B, boot recovery, then immediately restore known-good slot A.

## 2026-07-21 Android-common 4.14.286 repeat recovery result

- The package-verified `4.14.286-perf+` diagnostic was tested as a controlled recovery-only slot-B experiment. Host SHA-256 verification passed for the recovery, DTBO, vbmeta, control images, and kernel Image before the test.
- Bootloader preflight verified `odessa`, active successful slot A, two slots, `securestate: flashing_unlocked`, and battery voltage 4.413 V. Only explicit `dtbo_b`, `recovery_b`, and `vbmeta_b` writes were made, then slot B was selected and rebooted to recovery. The expected diagnostic-vbmeta rollback warning (`0` versus `16`) appeared.
- The phone bootlooped and returned to bootloader before displaying Lineage Recovery. No retry was performed. Slot A was immediately selected with `fastboot set_active a` and rebooted.
- Rollback was independently verified through Pixys Recovery ADB: `odessa`, slot `_a`, `4.14.190-perf+`, `sys.usb.config=adb`, `sys.usb.state=adb`, FunctionFS ready, and `adbd=running`. A subsequent normal reboot confirmed TequilaOS on `_a`, `sys.boot_completed=1`, and `4.14.190-Amber`.
- This supports a tentative boundary of Android-common `4.14.283` through `4.14.286`: the repeated 4.14.282 candidate visually reached Lineage Recovery, while this 4.14.286 candidate failed before Recovery. The 4.14.282 attempt's missing host USB enumeration is not a general host/cable/platform-tools failure because Pixys Recovery ADB enumerates and is healthy on the same host. It remains an unresolved candidate-kernel USB gadget/controller symptom.
- The 4.14.286 Image was supplied and package-verified rather than locally reproduced from its documented adaptation commits. Treat the boundary as diagnostic evidence, not a strict upstream-only bisection conclusion, until the exact image is reproducibly rebuilt from fully reviewed boundary-valid source.

## 2026-07-21 reproducible 4.14.283 recovery result and deferred range

- HOST ONLY reconstruction made the 4.14.286 diagnostic reproducible from reviewed source: Motorola base `92a96be148a072185131f60977af463c918b58cd`, Android-common 4.14.286 `e1c62d43d5e078cd7391fddb929ef41ebede7a72`, candidate `b8651ca9d5ccba87dfa91c550bf6e1fe3987a420`. Its recovery SHA-256 is `68ec41f5c30b7b04f30dc964353d9f34c497dcf8100eda27dd51128831e4b1c1`.
- A reproducible 4.14.283 candidate was built from Android-common `bc1a5b8c02ae4f3f821f3b325bad7bf87e679450`, with candidate source commit `1bd9d46c6b5f2870903474452f93d5ef71d1ee09`. It retains exact upstream `mm/memory.c` SHA-256 `2abb8a7dd65a6c42ff5aab03e8dd665a1dc6b481fb39dcb8de6d0152094e9277`, `CONFIG_SPECULATIVE_PAGE_FAULT=n`, and the boundary-valid Qualcomm early-RNG no-sleep correction. Android clang r563880c built it successfully; SHA256, component-equality, and complete AVB/hashtree verification passed. Artifact directory: ignored `lineageos/.downloads/diagnostic-recovery-4.14.283-spf-off-rng-fix-20260721/`; Image `b8f730ae4cdf2a90393a7d6aed7108c21af64310f4941cc274bf7247020e4dd3`, recovery `56bf3943cfbabdb16a12a73af55ff70892bd69cf0b1c1aacc218da27419d164e`, vbmeta `144a02354c8daa177eb0f979afba42b39c1c8337fecbcf2c7a1edf020851863d`.
- Controlled device test: preflight confirmed TequilaOS fully booted on successful slot A, `odessa`, two slots, `securestate: flashing_unlocked`, and 4.415 V battery. Only `dtbo_b`, `recovery_b`, and `vbmeta_b` were written. The expected unlocked-device rollback warning (`0` versus `16`) appeared. The 4.14.283 recovery bootlooped before the Lineage Recovery UI and returned to bootloader.
- Slot A was immediately restored with `fastboot set_active a`. Pixys Recovery ADB then confirmed `odessa`, slot `_a`, known-good `4.14.190-perf+`, and a live ADB service; a normal reboot subsequently confirmed TequilaOS on `_a`, `sys.boot_completed=1`, and `4.14.190-Amber`.
- Result: 4.14.283 is a reproducible FAIL. The early-RNG ordering changes introduced at this boundary remain a plausible contributor but are not the sole correction needed. Per user decision, do not continue the midpoint bisection. Treat Android-common 4.14.283 through 4.14.336, including the known failing 4.14.336 integration, as a deferred kernel bootloop investigation. Future work must start from the reproducible 4.14.283 source/artifact records and investigate early architecture/init, Qualcomm-specific integrations, and the reviewed 4.14.283-to-4.14.336 stable changes without importing later behavior into an earlier boundary.

## 2026-07-21 4.14.283 fix retry audit

- A HOST ONLY retry audited the reproducible 4.14.282 and 4.14.283 source/artifact boundaries specifically for an isolated early-boot fix. No phone command, source-tree modification, patch, image, or device test was made.
- The audited 4.14.283 candidate is `1bd9d46c6b5f2870903474452f93d5ef71d1ee09` from Android-common `bc1a5b8c02ae4f3f821f3b325bad7bf87e679450`. The relevant `.282` to `.283` delta has only eight files. `start_kernel`, `setup_arch`, all init code, RNG code, and `mm/memory.c` are byte-identical. The generated configurations differ only in the kernel-version comment.
- The boundary changes are not credible pre-Recovery causes: an unrelated IPQ8074 DTS sleep-clock value; Qualcomm `smp2p`/`smsm` DT-node reference balancing; compiled-out MSM serial support (`CONFIG_SERIAL_MSM=n`); PSI trigger lifetime code that runs only after userspace interacts with PSI; and trace behavior requiring trace setup absent from the recovery command line.
- Therefore no minimal `.283` fix or test image was created. Reverting a boundary change would be unrelated or simply recreate `.282`, invalidating the test. The earlier early-RNG theory is disproved for this exact `.282` to `.283` boundary because the affected code is identical. Future investigation must first explain the discrepancy between the claimed `.282` visual pass and the reproducible `.283` fail, including candidate construction/packaging or a repeated `.282` test with full artifact/slot verification, before attempting an arbitrary kernel fix.

## 2026-07-24 Btrfs ghost directory entry blocked a full build

- A full `m` build failed in the `PhotopickerLib` javac action: the rule's initial `rm -rf` could not remove a stale `srcjars` tree. Root cause was a corrupted Btrfs directory entry created 2026-07-23 22:47: readdir returned `dagger/hilt/processor/internal/definecomponent/codegej`, but lookup/unlink of both `codegej` and the presumed original `codegen` fail with ENOENT (`d?????????` in `ls`). The mangled name differs from `codegen` by one bit (`n`=0x6E → `j`=0x6A, bit 0x04 flipped).
- Btrfs device stats on `/dev/sdb1` are all zero (no read/write/flush/corruption/generation errors) and the current boot has no USB/UAS/xhci errors, so the filesystem never detected a checksum failure: the corruption was most likely introduced in host RAM before the metadata was written and checksummed, not by the USB transport.
- This is the third transient-corruption signal on this host: 2026-07-17 Clang SIGSEGV (initially blamed on a USB UAS reset), 2026-07-18 Rust LLVM SIGSEGV, and now a single-bit-flipped dirent. The evening of 2026-07-23 also shows four overlapping journald boot records (19:59, 20:04, 20:46, 20:54), suggesting hard crashes or clock anomalies. Treat host RAM/PSU/thermal stability as suspect until a memtest86+ run passes; do not trust long unattended builds to be reproducible until then.
- Fix applied (HOST ONLY): the corrupt tree was renamed to `.../PhotopickerLib/android_common_apex31/javac/srcjars.corrupt-20260724`, unblocking the build; no source defect existed. The ghost entry cannot be deleted online (unlink and rmdir both fail); removal requires offline `btrfs check` after unmounting, or it can simply be left harmlessly renamed until maintenance.
- Pending user-run diagnostics (need sudo): `sync && sudo sysctl -w vm.drop_caches=3` then re-read the corpse dir (if the ghost vanishes, corruption was RAM-only and the disk copy is fine; if it persists, the on-disk metadata is corrupt and needs offline `btrfs check`), `sudo btrfs scrub start /mnt/lineageos_drive`, and an overnight memtest86+.
- The build had not completed; resume incrementally with the usual constrained command (`lunch lineage_odessa-bp4a-userdebug`, sccache env, `m -j8 target-files-package`) preserving `out/`.

## 2026-07-22 4.14.282 USB gadget diagnostic results

- The exact 4.14.282 candidate reaches the Lineage Recovery UI but exposes no host USB device after Recovery's Enable ADB action. The host sees neither ADB, fastboot, nor any Motorola USB enumeration, so this is below `adbd` and not a host authorization or protocol-handshake issue.
- First HOST ONLY diagnosis found Android-common's generic DWC3 gadget import had removed `.vbus_session` while Motorola Qualcomm `dwc3-msm.c` still calls `usb_gadget_vbus_connect()` after runtime resume. A minimal diagnostic restored that callback and called existing `dwc3_gadget_run_stop()` for an OTG gadget with a bound driver. Artifact directory `lineageos/.downloads/diagnostic-recovery-4.14.282-usb-vbus-session-20260722/`; recovery SHA-256 `de736dc6384b1c2af30d269119774f50d8d0e277e65177db8faf767abd25ec9b`. AVB/component/hash verification passed. Controlled slot-B Recovery test did not restore USB enumeration.
- Second HOST ONLY diagnosis found the generic import also removed Motorola's persistent VBUS/soft-connect latching and runtime-PM acquisition. A 42-line `drivers/usb/dwc3/gadget.c` diagnostic restored both state latches and acquired DWC3 runtime PM before the existing `RUN_STOP` operation. It is based exactly on 4.14.282 candidate `2cfed6f0b1c45932868990ab79fa70c5b6cfd5c8`, retains exact upstream `mm/memory.c`, SPF-off, and the early-RNG correction. Artifact directory `lineageos/.downloads/diagnostic-recovery-4.14.282-usb-vbus-pm-20260722/`; kernel SHA-256 `ea999b87bdc869d69d08811155bdb34ee17c91801260b0ce54c038db8bb6209c`, recovery `633ac1df14ac1ad9785f9d404ec470b62f3c4964a3141001c130b01daf82ac2f`, vbmeta `16c4bde98671258527447d3896c28e4a9dd5fe4c7d2bc4be9a93041af3601914`. Source diff, full SHA-256, layout/component equality, and AVB/hashtree gates passed.
- The second controlled slot-B test also reached Recovery but still exposed no host USB device after Enable ADB. Both VBUS-handshake hypotheses are therefore insufficient. Do not carry either diagnostic patch into a release kernel or stack more unverified DWC3 changes. The next defensible work is a logging diagnostic that records DWC3 probe, runtime-PM state, role, UDC registration, configfs bind, and pullup/RUN_STOP results to a persistence mechanism reachable after rollback; early pstore may not capture it, so first establish a minimal persistent trace/log strategy without changing normal behavior.

## 2026-07-22 4.14.282 USB gadget diagnostic

- HOST ONLY audit found a concrete Qualcomm DWC3 integration break in the reproducible `.282` candidate, not a DT or Kconfig difference. Its Android-common generic DWC3 gadget import removed `.vbus_session`, while unchanged `dwc3-msm.c` starts peripheral mode by calling `usb_gadget_vbus_connect()` after runtime-PM resume. The imported pullup path can return success while runtime-suspended, so this leaves `RUN_STOP` unset and prevents all host USB enumeration while Recovery UI runs.
- A disposable worktree at `/tmp/opencode/sm6150-4.14.282-usb-gadget`, based exactly on candidate `2cfed6f0b1c45932868990ab79fa70c5b6cfd5c8`, has only a 19-line `drivers/usb/dwc3/gadget.c` diagnostic patch. It restores a VBUS-session bridge that calls the existing `dwc3_gadget_run_stop()` only for an OTG gadget with a bound driver. Qualcomm glue, DT, Kconfig, configfs/FunctionFS, RNG, SPF, and exact Android-common `mm/memory.c` remain unchanged.
- Android clang r563880c built `4.14.282-perf+` successfully using the established Android cross-tool paths. The exact `.282` generated configuration remains `d1dfa957234227bb30837b573eb6b3adc70463077bb3b102f971a87bb49564ca`; exact upstream `mm/memory.c` remains `2abb8a7dd65a6c42ff5aab03e8dd665a1dc6b481fb39dcb8de6d0152094e9277`.
- Ignored artifact directory: `lineageos/.downloads/diagnostic-recovery-4.14.282-usb-vbus-session-20260722/`. Kernel Image SHA-256 `0898c71b272fcb13f988bf3f3064ccece18a6794aaee19fc6f26bd67a55abe4a`; recovery `de736dc6384b1c2af30d269119774f50d8d0e277e65177db8faf767abd25ec9b`; DTBO `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; flags-0 test-key vbmeta `736888b769e87e89c68a1ca3a5cc76852d6977ff884cc2d5ee2830bd64e38ad3`.
- SHA256SUMS verification, recovery-component equality gates, and complete AVB verification passed. Vbmeta is RSA-4096 test-key, rollback index 0, flags 0, and only 4,736 bytes because the established template emits compact valid metadata. This diagnostic has no hardware result and is not approved for flashing.

## 2026-07-22 4.14.282 Qualcomm DWC3 restoration

- HOST ONLY root-cause review found that the synthesized 4.14.282 candidate did not retain the working Motorola/Qualcomm DWC3 controller implementation. Compared with the known recovery-ADB-working 4.14.254 candidate `f14359c8f5cc269b8be9231eebcdead0b1d342b7`, its `drivers/usb/dwc3/core.c` and `gadget.c` had been replaced by a generic implementation that removed the Qualcomm notifier/runtime-PM/IRQ/VBUS integration used by unchanged `dwc3-msm.c`. This replacement was candidate adaptation history, not a Linux 4.14.282 stable change.
- The two earlier one-function VBUS diagnostics were correctly rejected after hardware tests failed. The new bounded candidate instead restores the coherent 4.14.254 Motorola/Qualcomm `core.c` and `gadget.c` byte-for-byte atop exact 4.14.282 candidate `2cfed6f0b1c45932868990ab79fa70c5b6cfd5c8`; every other 4.14.282 source file is retained. Disposable worktree: `/tmp/opencode/sm6150-4.14.282-usb-qualcomm`.
- Android clang r563880c built `4.14.282-perf+` successfully without additional source adaptation. Image: 33,185,816 bytes, SHA-256 `d6ae6e894180011ad0fabe666809ec437b1acba3c97faf0b5cb8897cdc6747d6`. Generated config SHA-256 remains `d1dfa957234227bb30837b573eb6b3adc70463077bb3b102f971a87bb49564ca`.
- Ignored package directory: `lineageos/.downloads/diagnostic-recovery-4.14.282-qualcomm-dwc3-20260722/`. Recovery: 67,108,864 bytes, SHA-256 `9c368b6e1975053134aad7452be167f1f73ff062c6030765715b499500436cdd`; unchanged DTBO SHA-256 `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; matching flags-0 rollback-0 test-key vbmeta SHA-256 `6d267e555a4c80e64e0de12cc89b2621f045b8ff36cff452d492d1e8294ba86a`.
- SHA-256 manifest, source diff check, recovery layout/component equality, kernel equality, recovery/DTBO AVB verification, and top-level vbmeta verification including boot plus product/system/vendor hashtrees all pass. `SOURCE-PROVENANCE.md` and the exact two-file patch are stored with the ignored artifacts.
- This candidate is package-verified only. No phone was contacted or flashed, and recovery USB/ADB has not yet been validated on hardware. Do not confuse it with the failed `usb-vbus-session` or `usb-vbus-pm` candidates.

## 2026-07-22 4.14.282 Recovery ADB fix verified

- The package-verified Qualcomm-DWC3 recovery was tested on slot B after a read-only bootloader preflight confirmed `odessa`, bootloader fastboot (`is-userspace: no`), `securestate: flashing_unlocked`, successful/bootable fallback slot A, two slots, and 4.408 V battery voltage.
- Host SHA-256 verification passed immediately before writing. Only explicit `dtbo_b`, `recovery_b`, and `vbmeta_b` writes were performed, followed by selecting slot B and rebooting to recovery. Fastboot reported `OKAY` for every write. The unlocked bootloader emitted the expected diagnostic-vbmeta rollback warning (`0` versus `16`) and accepted the image.
- The purple Lineage Recovery UI booted. After Enable ADB, the host enumerated the recovery ADB interface; it initially reported `unauthorized`, then connected normally after device authorization. This fixes the prior 4.14.282 failure where the host saw no USB device at all.
- Root recovery ADB verified device `odessa`, slot `_b`, kernel `4.14.282-perf+`, `sys.usb.config=adb`, `sys.usb.state=adb`, `sys.usb.ffs.ready=1`, and `init.svc.adbd=running`.
- Direct installed-image verification matched the diagnostic artifacts exactly: `recovery_b` SHA-256 `9c368b6e1975053134aad7452be167f1f73ff062c6030765715b499500436cdd`; `dtbo_b` SHA-256 `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; first 8,192 bytes of `vbmeta_b` SHA-256 `6d267e555a4c80e64e0de12cc89b2621f045b8ff36cff452d492d1e8294ba86a`.
- Hardware result: PASS for Lineage Recovery boot, USB gadget enumeration, FunctionFS, and ADB on the bounded 4.14.282 Qualcomm-DWC3 candidate. This supersedes both failed one-function VBUS diagnostics and confirms that restoring the coherent Motorola/Qualcomm DWC3 `core.c` plus `gadget.c` integration fixes Recovery ADB.
- The verified two-file restoration is committed in the kernel repository on local branch `wip/odessa-4.14.282-usb-adb-fix` as `0625428fb4ec75101674bbef22bc72362085ec5e` (`usb: dwc3: Restore Qualcomm gadget integration`). The branch is based on exact 4.14.282 candidate `2cfed6f0b1c45932868990ab79fa70c5b6cfd5c8`; it has not been pushed.
- The phone remained in slot-B Lineage Recovery at the end of verification. Slot A was not modified and remains the known-good fallback; before returning to normal TequilaOS use, reboot to bootloader, select slot A, and reboot.

## 2026-07-22 corrected 4.14.283 recovery candidate

- HOST ONLY. The previously failing 4.14.283 diagnostic did not contain the subsequently hardware-verified coherent Motorola/Qualcomm DWC3 restoration, so it could not provide the same recovery USB/ADB observability as the corrected 4.14.282 pass.
- Local branch `wip/odessa-4.14.283-usb-adb-fix` now combines exact reproducible 4.14.283 candidate `1bd9d46c6b5f2870903474452f93d5ef71d1ee09` with only the two verified DWC3 files. Source commit `6a01c7ef2a186f243fb35d5b08942dbbd0684ee5`, tree `9791000973e3e4bdf171782cc74dd56ca5cd75cf`; the worktree is clean and the branch has not been pushed.
- Android clang r563880c built genuine `4.14.283-perf+`. Generated config SHA-256 is `7fda929910493513c45a734b67a218f2159fa675c85cd256495a6edc4dece690`; exact boundary `mm/memory.c` remains `2abb8a7dd65a6c42ff5aab03e8dd665a1dc6b481fb39dcb8de6d0152094e9277`; kernel Image SHA-256 is `0326aebc1e345ba8ec093f890e2157cf5bbeb6055f397c66b7930ec45d95dc98`.
- Ignored package directory: `lineageos/.downloads/diagnostic-recovery-4.14.283-qualcomm-dwc3-20260722/`. Recovery SHA-256 `3b0c4040dfbe83886070a52f69316c094110c2311f1f08e7173173f0f2c7891a`; unchanged DTBO `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; matching flags-0 rollback-0 test-key vbmeta `70b2d6b6e47a96f395da27832bed488e6ff37f935a0511fbc68c7bc1a74b6cec`.
- SHA-256, source-bundle, recovery layout/component equality, kernel equality, recovery/DTBO AVB, and complete top-level vbmeta verification all pass. No phone command was issued and hardware behavior remains untested.
- If this corrected baseline still bootloops before Recovery/ADB, the first focused revert candidate is 4.14.283 commit `cf90ea494bb4c0231214e905e4bc977cd9cbdae7`, which replaces the Qualcomm UFS reference-clock `wmb()` with a synchronous MMIO `readl()` on an enabled boot-storage path. Test it alone rather than carrying a permanent revert without hardware evidence.
- Do not prioritize `ac70d51feabc37ded85be090fbf28541606b057f`: Odessa has `CONFIG_DRM_MSM_DSI=n` and uses the staging DSI implementation, so the changed generic `dsi_host.c` is not linked. SMP2P commit `7f868a3a4950919fed3dcada35fbff8b18c24fa2` is enabled but only releases the temporary DT-node reference after `syscon_node_to_regmap()`; keep it behind the UFS test unless evidence changes.

## 2026-07-23 corrected 4.14.283 failure and UFS fix candidate

- The package-verified 4.14.283 Qualcomm-DWC3 baseline was tested after fresh SHA-256 verification and a preflight that confirmed fully booted TequilaOS on successful slot A, `odessa`, bootloader fastboot, two slots, `securestate: flashing_unlocked`, and 4.450 V battery voltage.
- Only explicit `dtbo_b`, `recovery_b`, and `vbmeta_b` writes were made before selecting B and rebooting to recovery. Every fastboot write succeeded; the expected diagnostic-vbmeta rollback warning (`0` versus `16`) appeared. The phone bootlooped before Lineage Recovery, confirming that coherent DWC3 restoration alone does not fix the 4.14.283 startup regression.
- Slot A was immediately selected and rebooted. The user declined the subsequent Android verification wait; do not claim that post-test TequilaOS boot was independently checked in this session. No retry, firmware copy, userdata operation, dynamic-partition write, OTA, GApps, or Magisk action occurred.
- A minimal HOST-ONLY fix candidate now restores Motorola's pre-4.14.283 `wmb()` after the Qualcomm UFS reference-clock `writel_relaxed()` instead of stable commit `cf90ea494bb4c0231214e905e4bc977cd9cbdae7`'s synchronous MMIO `readl()`. It is the only source modification relative to corrected baseline `6a01c7ef2a186f243fb35d5b08942dbbd0684ee5`; worktree `/tmp/opencode/sm6150-4.14.283-ufs-fix`, local branch `wip/odessa-4.14.283-ufs-fix`. The change remains intentionally uncommitted pending hardware proof.
- Exact patch is preserved as `ufs-ref-clock-wmb.patch`, SHA-256 `6259e256c064aa9f2967261d9efa089a899aaeae8acb4f230dcdf4de997dc40d`, under ignored package `lineageos/.downloads/diagnostic-recovery-4.14.283-qualcomm-dwc3-ufs-fix-20260723/`.
- Android clang r563880c built `4.14.283-perf+`; Image SHA-256 `a9fd667c544084cf03d4eebbf5d8bafb4607cc27287c80d5c430096b5739f4cc`. Recovery SHA-256 `de328441f51244fadf5b2c040d1e8d2493269d05c36fac3b81c336e0768b801e`; unchanged DTBO `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; matching flags-0 rollback-0 test-key vbmeta `d3b9d61ba02c82a1a81d3a087fad05f9cf28dd846ccabcac0f23763dfb2af147`.
- Config and exact boundary `mm/memory.c` remain byte-identical to the corrected baseline. Source diff/check, both SHA-256 manifests, component equality, kernel equality, recovery/DTBO AVB, and complete top-level vbmeta follow-chain verification all pass. Hardware behavior is untested, so this is a focused fix candidate, not yet a confirmed bootloop fix.
- At the user's explicit request, the UFS-fix candidate was written to explicit `dtbo_b`, `recovery_b`, and `vbmeta_b` partitions. Every fastboot write returned `OKAY`; the expected unlocked-device rollback warning (`0` versus `16`) appeared for `vbmeta_b`. Slot B was not selected or booted, no post-write verification was performed, and slot A was left active. Immediately before this request, bootloader fastboot reported slot A bootable but `slot-successful:a: no`; the user declined the proposed fallback verification, so automatic fallback is not confirmed.

## 2026-07-23 UFS failure and nodemask candidate

- The user selected and booted the 4.14.283 Qualcomm-DWC3 UFS-revert candidate on slot B and reported the same pre-Recovery bootloop. This rules out stable commit `cf90ea494bb4c0231214e905e4bc977cd9cbdae7` as the sole regression. Per user instruction, no slot-A or recovery-A validation followed.
- A linked-object comparison between the hardware-passing corrected 4.14.282 kernel and failing corrected 4.14.283 kernel found 41 behavior-bearing linked object deltas, including changes propagated through headers that the earlier source-only audit missed. The strongest remaining pre-userspace delta is the 4.14.283 nodemask change affecting generated cpuset and IRQ-affinity code during CPU bring-up.
- New worktree `/tmp/opencode/sm6150-4.14.283-nodemask-fix`, local branch `wip/odessa-4.14.283-nodemask-fix`, is based on corrected 4.14.283 Qualcomm-DWC3 commit `6a01c7ef2a186f243fb35d5b08942dbbd0684ee5`. Its only uncommitted source changes restore `include/linux/nodemask.h` and `lib/nodemask.c` to 4.14.282 semantics; UFS remains unmodified 4.14.283 code. Exact patch SHA-256 is `357fb798c4cf12dd3c18aaf473be7dac981791119a90b4d656fee5f8b54dd3e0`.
- Android clang r563880c built `4.14.283-perf+`; Image SHA-256 `4bdcf4a8f5ac90dff75638553a0aed08ec87c26750f4a589fb685fc926f75e9e`. The fixed nodemask executable `.text` is byte-identical to the passing 4.14.282 implementation.
- Ignored package: `lineageos/.downloads/diagnostic-recovery-4.14.283-qualcomm-dwc3-nodemask-fix-20260723/`. Recovery SHA-256 `1864aae86b2888cf260216badb3648d7a453a3801162ad74b725d24300171e8e`; unchanged DTBO `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; matching flags-0 rollback-0 test-key vbmeta `19c9d086a3a429a643d9a47fe252fc1cb21f4a8e9161bf11ed9ffa2d675743f1`. Source, build, component-equality, SHA-256, recovery/DTBO AVB, and complete top-level vbmeta follow-chain gates pass.
- At the user's request the nodemask candidate was written to explicit slot-B DTBO/recovery/vbmeta, B was selected, and Recovery boot was requested. All fastboot operations returned `OKAY`; the expected diagnostic vbmeta rollback warning appeared. No slot-A validation was performed. Hardware result is pending the user's visual report.
- The user reported that the nodemask candidate also bootlooped before Recovery. This rules out the 4.14.283 nodemask/cpuset/IRQ-affinity closure as the sole cause. No slot-A or recovery-A validation was requested or performed.
- Detailed continuation instructions, exact pass/fail matrix, ruled-out hypotheses, artifact hashes, repository state, and next candidate order are recorded in `docs/kernel-4.14.283-bootloop-handoff-20260723.md`. The next focused candidate is the two-commit `kernel/trace/trace.c` initialization group from corrected baseline `6a01c7ef2a18`; if that fails, proceed with mailbox core, extcon registration, then the coherent ext4 group before switching to a coarse grouped-revert/add-back strategy.

## 2026-07-23 trace diagnostic failure

- A clean diagnostic based on corrected 4.14.283 Qualcomm-DWC3 commit `6a01c7ef2a186f243fb35d5b08942dbbd0684ee5` restored only `kernel/trace/trace.c` to exact Android-common 4.14.282 semantics, reverting the behavior of `be1f323fb9d9` and `0816ec55fc0b` without stacking the failed UFS or nodemask changes.
- Android clang r563880c built genuine `4.14.283-perf+`; the generated config remained SHA-256 `7fda929910493513c45a734b67a218f2159fa675c85cd256495a6edc4dece690`, exact boundary `mm/memory.c` remained unchanged, and the Image SHA-256 was `e488212ba1369b8e3cd22cc6e4696269b61cd0f6f06cd0285b39ebe85cd0072d`.
- Ignored package: `lineageos/.downloads/diagnostic-recovery-4.14.283-qualcomm-dwc3-trace-fix-20260723/`. Recovery SHA-256 `ad384f2b88a9b8cc67a4329eb47bf7a607a9dab956dca046d7f5128ccb280753`; DTBO `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; vbmeta `c9313521e21c8a3f36627a0fc78a1b77b9505a40cb2b43243a99025892eafec4`. Source allowlist, component equality, SHA-256, and complete AVB follow-chain gates passed.
- Only explicit slot-B `dtbo`, recovery, and vbmeta were written, B was selected, and Recovery was requested. Every fastboot operation returned `OKAY`; the expected diagnostic-vbmeta rollback warning appeared. The user reported the same pre-Recovery bootloop and return to bootloader.
- This rules out the two trace commits as the sole regression. Per the established order, the next clean candidate restores only the mailbox core closure (`drivers/mailbox/mailbox.c` plus `include/linux/mailbox_controller.h`) from 4.14.282 while retaining the Qualcomm DWC3 fix.

## 2026-07-23 mailbox failure and extcon pass

- A clean corrected-4.14.283 diagnostic restored only `drivers/mailbox/mailbox.c` and `include/linux/mailbox_controller.h` from passing synthesis `2cfed6f0b1c4`. It retained the Qualcomm DWC3 fix and did not stack trace, UFS, or nodemask changes. The verified recovery still bootlooped before Recovery, ruling out mailbox stable commit `e75b5ea2d6b1` as the sole cause.
- The next clean candidate restored only `drivers/extcon/extcon.c` from passing synthesis `2cfed6f0b1c4`. Android clang r563880c built `4.14.283-perf+`; config SHA-256 remained `7fda929910493513c45a734b67a218f2159fa675c85cd256495a6edc4dece690`, Image SHA-256 was `39c5d8e0c862286643ef1722e8d73c19b87e1800a893a0b0080f0c057d5cba11`, recovery `7aa2a3ea9628e5968601f13fb0d970a9a8235f6928a850904954c990cc4ed6a4`, DTBO `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`, and vbmeta `eceb0cf0c483865fdd68ecde9817ab6f76b4f282a65ff87730e33f9453e2be95`. SHA-256 and complete AVB follow-chain verification passed.
- The extcon diagnostic booted Lineage Recovery on slot B and exposed the recovery USB/ADB interface. This isolates the boot regression to the `drivers/extcon/extcon.c` delta introduced by stable commit `6e721f3ad0535b24f19a62420f4da95212cf069c`.
- Root cause: that stable commit correctly delays `device_register()` until after `dev_set_drvdata()`, and converts upstream `edev->nh` from devm allocation to explicit `kcalloc` because the extcon `struct device` is not initialized before `device_register()`. Motorola's local `edev->bnh = devm_kzalloc(&edev->dev, ...)` remained before the delayed registration. It therefore accesses the uninitialized device-resource lock during early extcon registration and can hang before Recovery. The forward fix must retain the stable registration ordering while converting local `bnh` to explicit allocation and balanced frees; do not ship the broad 4.14.282 extcon revert.
- The forward-safe candidate made exactly that three-site correction: allocate Motorola `bnh` with `kcalloc`, free it on registration failure, and free it during unregister. It retained every other 4.14.283 change and the Qualcomm DWC3 fix. Android clang r563880c built `4.14.283-perf+`; Image SHA-256 `a326ee2aedc96ea88450bb4d968f35ddefc89fd2bed98a6b25e3cdf9b86d9b0f`, recovery `0f4e88c42af2e3a34cd8beefa69a30d7cf27c9df62fe627d922fc278e8e78597`, DTBO `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`, and vbmeta `818668d43e7063b6f641ff0f4be328c4a6d3869342eb5c47c1979d99927cba6b`. SHA-256, component equality, and complete AVB verification passed.
- The forward-safe candidate booted Lineage Recovery on slot B. This confirms the fix without reverting stable commit `6e721f3a`; no ext4 or coarse grouped revert is needed for the 4.14.283 boot regression.
- A clearly named final source worktree exists at `/tmp/opencode/sm6150-4.14.283-final-boot-fix`, branch `wip/odessa-4.14.283-final-boot-fix`. Commit `f22e2c86abfb` (`extcon: Fix notifier allocation before registration`) applies only the hardware-tested extcon fix on corrected baseline `6a01c7ef2a18`. Its patch is byte-identical to the hardware-tested worktree, SHA-256 `fcb0b489d0605010eda1573695fdc8399924e777859c7b1ecdbd50d2eab0c69b`.

## 2026-07-23 Linux 4.14.310 recovery PASS

- Android-common `deprecated/android-4.14-stable` milestone `9b19b769a59207ac22f4555dfd668fd7c5b8a7e8` is the authoritative `Merge 4.14.310 into android-4.14-stable`. Worktree `/tmp/opencode/sm6150-4.14.310-boot-test` and branch `wip/odessa-4.14.310-boot-test` advance hardware-tested/pushed `f22e2c86abfb` to that exact boundary. Final merge commit `d3fa64ad9611ea74e514d256d814f20f834e249b` has parents `f22e2c86abfb843192099a3e141c0ce4ca01154a` and `9b19b769a59207ac22f4555dfd668fd7c5b8a7e8`; its tree is the exact flashed tree `a31297b3d95179c4b4ff30040f03c99d3f31c785`.
- Reviewed adaptations preserve the Qualcomm early-RNG no-sleep path, coherent Motorola/Qualcomm DWC3 integration, hardware-tested extcon `bnh` allocation fix, and disabled speculative page fault. Exact 4.14.310 `mm/memory.c` and ext4 implementation are retained; post-4.14.310 behavior and failed UFS/nodemask/trace/mailbox diagnostic reverts are absent. `git diff --check` passes.
- Android clang r563880c, LLVM/IAS, `vendor/odessa_defconfig`, `LOCALVERSION=+`, build number 310, and `-j8` produced genuine `4.14.310-perf+`. Config SHA-256 is `012f349bd642d2981feceb316df04c24fe14628e62cc38688dd6e86a84f9f54b`; Image SHA-256 is `66115534b78b409dccf9bdadb49a0a252d86aa779a171b33be05ca60b5641509`.
- Sealed ignored package: `lineageos/.downloads/diagnostic-recovery-4.14.310-boot-test-20260723/`. Recovery SHA-256 `aa7be7b89a5906eb2f6a6c5db8ec8bd081163f5e28e2b04d9162a41ad1b4c03a`; unchanged DTBO `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; flags-0 test-key vbmeta `84d95ae3cda01974feee4c997e6680d76d1e9b4230754798dfa0c723582f198d`. SHA-256, one-variable component equality, recovery/DTBO AVB, and complete vbmeta follow-chain verification through boot/recovery/DTBO/product/system/vendor all passed.
- Immediately before writing, fastboot reported product `odessa` and bootloader fastboot (`is-userspace: no`). Only explicit `dtbo_b`, `recovery_b`, and `vbmeta_b` were written, all with `OKAY`; the expected unlocked-device vbmeta rollback warning (`0` versus `16`) appeared. `set_active b` and `reboot recovery` both returned `OKAY`. No slot-A image, `boot_b`, firmware, super/dynamic partition, userdata, or other partition was written, and no rollback was performed.
- The user reported that this exact candidate successfully booted Lineage Recovery on slot B. This is a hardware PASS for reaching the Recovery UI with the 4.14.310 kernel; it does not by itself validate recovery ADB, normal Android boot, slot A, or broader hardware functionality.
- Final source was pushed without force to `origin/wip/odessa-4.14.310-boot-test` (`https://github.com/ARLBR10/android_kernel_motorola_sm6150.git`). The local branch is clean, tracks that remote branch, and is synchronized at `d3fa64ad9611ea74e514d256d814f20f834e249b`.

## 2026-07-23 Linux 4.14.336 recovery launch

- Local branch `wip/odessa-4.14.336-boot-test` advances the hardware-passing 4.14.310 merge `d3fa64ad9611ea74e514d256d814f20f834e249b` to authoritative Android-common 4.14.336 commit `014241ad77dda0eafbdf671d5b8e86917d8ec97e`. Merge commit `69454130e6fbf6b94d35750be9a2860533be0e4e` has tree `01f3dcd4c5c01f3baec9d84785413a0e3f86d395` and remains local/unpushed.
- Reviewed merge resolutions preserve the hardware-tested Motorola/Qualcomm DWC3 implementation, the extcon `bnh` allocation fix, the Qualcomm early-RNG no-sleep path, and disabled speculative page fault while incorporating applicable 4.14.336 stable behavior. Focused compilation of extcon and DWC3 objects passed, and the full ARM64 Image built as genuine `4.14.336-perf+` with Android clang r563880c.
- Ignored package: `lineageos/.downloads/diagnostic-recovery-4.14.336-boot-test-20260723/`. Kernel Image SHA-256 `5a1c67f39a0a49e662c2e5221f5d2c7e5d4554eda03e6df2d08bbe88b2939c01`; recovery `df5e64fad0ad2b0fe4c0ccbe402fb33ffb547d9e118085266aa3091766ceced6`; unchanged DTBO `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; flags-0 rollback-0 test-key vbmeta `a3d9d079e54bad14da7a60557c914f882924b0e2a679980236e217dba0291bf9`.
- SHA-256 manifests, one-variable recovery component equality, recovery/DTBO AVB checks, and complete vbmeta follow-chain verification through boot, recovery, DTBO, product, system, and vendor all passed before flashing.
- Immediate bootloader preflight reported `odessa`, bootloader fastboot (`is-userspace: no`), `securestate: flashing_unlocked`, two slots, current slot B, compatible partition sizes, and battery voltage 4.423 V. No boot-A or recovery-A check was performed per user instruction.
- Only explicit `dtbo_b`, `recovery_b`, and `vbmeta_b` were written. Every send/write returned `OKAY`; the expected unlocked-device vbmeta rollback warning (`0` versus `16`) appeared. `set_active b` and `reboot recovery` both returned `OKAY`. No slot-A image, `boot_b`, firmware, dynamic partition, userdata, or other partition was written.
- This records a successful flash and recovery launch request only. Recovery UI/ADB and kernel identity were not checked after reboot, so hardware boot behavior is not yet claimed as PASS or FAIL.

## 2026-07-23 Linux 4.14.336 publication and lineage integration

- The user reported that the exact slot-B recovery launched from `wip/odessa-4.14.336-boot-test` worked. This upgrades the prior launch-only record to a hardware PASS for reaching the Recovery UI with the packaged `4.14.336-perf+` kernel; recovery ADB, normal Android boot, and the broader hardware matrix remain untested by that operation.
- The exact hardware-passing branch was pushed without force to `origin/wip/odessa-4.14.336-boot-test` at `69454130e6fbf6b94d35750be9a2860533be0e4e`.
- It was merged into local `lineage-23.2` with merge commit `dee98796a331396f070a4739a46b7654acabc191`, tree `96367d6cc1365208a1cc55c7ec8ca1da8a83a8f0`, and parents previous lineage head `41038075962c29364e02cbe5a548904b1f88e028` plus passing branch head `69454130e6fbf6b94d35750be9a2860533be0e4e`.
- Overlapping stable-update conflicts retain the hardware-passing implementation. The final merged tree differs from the passing parent only in six files implementing the already reviewed Android 16 PMD/PUD mremap capabilities, FCM 6 Odessa configuration, and KGSL `TRACE_GPU_MEM` selection. The extcon allocation fix, coherent Qualcomm/Motorola DWC3 implementation, and early-RNG no-sleep behavior are byte-identical to the passing branch.
- Android clang r563880c built the merged tree successfully as `4.14.336-perf+`. Merged Image: 33,187,864 bytes, SHA-256 `bbfe94ef2508204f6d9f606a44f639c294197e41e4bac891eb0f1ca9ee8b36af`; generated config SHA-256 `56575300fc20e97c515f283dde7205950bb708a08fd0c36f9bb1129202729b94`. Required FCM options and disabled speculative page fault were verified.
- `origin/lineage-23.2` was pushed normally from `92a96be148a072185131f60977af463c918b58cd` to `dee98796a331396f070a4739a46b7654acabc191`. The merged Android 16 Image has not yet been hardware-tested; do not conflate the passing diagnostic Image with this configuration-augmented lineage Image.

## 2026-07-23 DTB build configuration fix

- A full product retry built the kernel Image but failed when the Android kernel rule invoked `dtbs`: `arch/arm64/boot/dts/qcom/Makefile:3: recipe commences before first target`.
- The Motorola Makefile had a tab before its top-level `$(error ...)`, which GNU Make parsed as an orphan recipe. Removing the tab exposed the underlying configuration defect: `vendor/odessa_defconfig` requested `CONFIG_BUILD_ARM64_DT_OVERLAY=y`, but the merged `arch/arm64/Kconfig` no longer declared that standard Qualcomm option, so `silentoldconfig` discarded it.
- Restored the Qualcomm `BUILD_ARM64_DT_OVERLAY` boolean with its `OF` dependency and corrected the Makefile directive indentation. Regenerating `vendor/odessa_defconfig` retained the option, and a focused Android-clang `make -j8 dtbs` built `sdmmagpie-odessa-base.dtb` plus the EVT1, DVT2, and PVT overlay DTBOs successfully.
- The known Motorola multi-value touchscreen `status` properties still emit `status_is_string` DTC warnings. They are unchanged and remain a bootloader/hardware validation risk, not a failure of this fix. The constrained full product build still needs to resume without cleaning `out/`.

## 2026-07-23 4.14.310-to-4.14.336 Recovery ADB audit

- The user reports that Recovery ADB worked on the exact 4.14.310 candidate but not on the exact 4.14.336 candidate, although both reached the Lineage Recovery UI. Prior records validated only the UI on those two builds, so the new report is the current hardware observation; no 4.14.336 runtime log is available yet to distinguish host enumeration from FunctionFS/adbd state.
- Extcon is not the new regression. Between source commits `d3fa64ad9611` and `69454130e6fb`, `drivers/extcon/extcon.c` gains only kernel-doc text. Its executable behavior and the hardware-tested Motorola `bnh` allocation/free fix remain unchanged.
- The strongest source and linked-object delta is the 14-line suspended-event/runtime-PM path added to the retained Qualcomm-integrated `drivers/usb/dwc3/gadget.c`. It can disable `irq_gadget` while suspended and expects generic `dwc3_runtime_resume()` to process pending events, but the installed Qualcomm notifier makes that function return early and `dwc3_msm_resume()` does not perform the generic pending-event completion.
- A HOST ONLY one-file diagnostic was built from exact 4.14.336 commit `69454130e6fb`, restoring `gadget.c` byte-for-byte to the 4.14.310 implementation while retaining every other 4.14.336 change. Worktree: `/tmp/opencode/sm6150-4.14.336-dwc3-pm-test`; ignored package: `lineageos/.downloads/diagnostic-recovery-4.14.336-dwc3-pm-test-20260723/`.
- Generated config matches the original 4.14.336 diagnostic, SHA-256 `5e6202cc7e86a31e17a517ed79923fb6bdb0b243c646183f5d7140b864eac0f9`. Kernel Image SHA-256 is `4ade0780cac4e24a92be232359151beb4cec8ad4aa582845ada7099832568317`; recovery `63db58717bf9c7738157e502bb91ad0c71755ad5b860763816667efd290e75f9`; unchanged DTBO `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`; diagnostic vbmeta `067589652058b35ece1ac78e191e4951ce49a649b30c3941129d70e88d0934f9`.
- Source allowlist/diff checks, component equality, SHA-256, recovery/DTBO AVB, and complete top-level vbmeta follow-chain verification passed. No phone command ran. The next checkpoint requires explicit permission for the established slot-B recovery-only write/test; test Recovery UI, host USB enumeration, and ADB separately.
- The user hardware-tested that exact diagnostic and reports that Recovery ADB works. This confirms the incompatible DWC3 suspended-event/runtime-PM merge delta as the regression and confirms extcon was unrelated to the 4.14.310-to-4.14.336 ADB change.
- The exact hardware-tested 14-line DWC3 deletion was then applied to the main `kernel/motorola/sm6150` `lineage-23.2` worktree so subsequent product/target-files builds include the working Recovery USB behavior. It remains uncommitted pending source/build verification.

## 2026-07-23 vendor image RFS path normalization fix

- The user's incremental `target-files-package vbmetaimage` build compiled the hardware-tested DWC3 change and rebuilt the kernel, DTBs, modules, and module staging. It then failed only while creating `vendor.img`: `rfs/msm/adsp/: not normalized`.
- The generated vendor file list contained four trailing-slash directory targets: `rfs/msm/adsp/`, `cdsp/`, `mpss/`, and `slpi/`. They came from obsolete directory-valued `ALL_DEFAULT_INSTALLED_MODULES` rules in `device/motorola/sm6150-common/Android.mk`.
- Branch-current `hardware/qcom-caf/common` already installs every required child RFS symlink through explicit Soong `install_symlink` modules, and those modules were present in the Odessa output graph. The duplicate legacy RFS directory rules were removed while retaining the unrelated Wi-Fi, IMS, and expat symlink rules.
- HOST ONLY focused verification with `m -j8 vendorimage` completed successfully in 2m02s. It produced `out/target/product/odessa/vendor.img`, 530,710,528 bytes. The regenerated vendor `file_list.txt` contains none of the four non-normalized trailing-slash RFS entries, and no new fatal error appeared. Log: `lineageos/.downloads/build-logs/vendorimage-rfs-rule-fix-20260723-attempt2.log`.
- No phone command ran. Resume the preserved incremental build with `m -j8 target-files-package vbmetaimage`; do not clean `out/`.

## 2026-07-23 target-files sideload rejection and corrected OTA

- The user attempted to sideload `lineage_odessa-target_files.zip` through Recovery and received status 1. That archive is an input to OTA tooling, not an installable package: the current 2,615,225,827-byte archive, SHA-256 `408bc32ddfa1a44fd1b2b350dd5f7213046462f4291cfdffb8a751b45cbebb79`, contains no `payload.bin`, OTA metadata, or update binary. Recovery therefore had no updater to execute. Do not sideload target-files archives.
- Because the target-files archive contains no install mechanism, this rejection should occur before partition payload application. Do not nevertheless assume slot state before a later flash; re-query it at the destructive-step preflight.
- A new HOST ONLY installable A/B OTA was generated from that exact target-files archive without bypassing VINTF. Output: `lineageos/out/target/product/odessa/lineage-23.2-20260723-DWC3-UNOFFICIAL-odessa.zip`, 1,028,362,502 bytes, SHA-256 `1093e921def1bb0629dd236c4b2977216d80ee8263871c436e4744773f081a18`.
- OTA generation exited zero, verbose VINTF returned `COMPATIBLE`, ZIP integrity passed, and required `payload.bin`, `payload_properties.txt`, OTA metadata, and `care_map.pb` entries are present. AOSP payload inspection reports version 2 and partitions `boot`, `dtbo`, `product`, `recovery`, `system`, `vbmeta`, and `vendor`; payload SHA-256 `9510f692dde83be1c860697a6f68cadc1f31dce7e805ba5b3a7e147008818718` matches `payload_properties.txt`.
- The old July 19 OTA remains unchanged and must not be used because it predates the hardware-tested DWC3 fix. No phone command was issued during corrected OTA generation. A future sideload remains device-changing and requires a live identity/slot/fallback preflight; test the base ROM without GApps or Magisk first.

## 2026-07-24 Recovery AIDL BootControl blocker and migration

- Read-only collection of the live Lineage Recovery `/tmp/recovery.log` found the exact OTA status-1 cause. Whole-file package signature verification succeeds, but Android 16 `update_engine_sideload` reports `AIDL IBootControl not available`, falls back to HIDL, rejects versions 1.1 and earlier, and exits before initializing its BootControlInterface. No payload partition operation begins.
- The product still explicitly selected `android.hardware.boot@1.1-service` and the local HIDL QTI implementation. `device/motorola/sm6150-common/common.mk` now selects branch-current `android.hardware.boot-service.qti` and `android.hardware.boot-service.qti.recovery` instead. These use the same Qualcomm GPT implementation through the AIDL interface required by Android 16.
- Focused HOST ONLY builds of both QTI AIDL services, `recoveryimage`, and `selinux_policy` passed. The rebuilt Recovery contains the AIDL executable, init interface declaration, and VINTF fragment; obsolete HIDL service/implementation artifacts are absent. SELinux labels/tests pass. Log: `lineageos/.downloads/build-logs/bootctrl-aidl-20260723-attempt2.log`.
- Regenerated target-files: 2,614,867,109 bytes, SHA-256 `20ac2c2d7cfd0f438f2aab1da94e0b7061ce3c1e84f308632264b07b6113b29b`; ZIP integrity, verbose VINTF `COMPATIBLE`, and complete AVB follow-chain verification pass.
- New installable OTA: `lineageos/out/target/product/odessa/lineage-23.2-20260723-AIDLBOOTCTRL-UNOFFICIAL-odessa.zip`, 1,028,399,639 bytes, SHA-256 `d5dc8077e7fb59c5a6cd75ccfd68e4ed760cd94188997c07f4c6f2fb6eee11b1`. Payload verification passes and includes `boot`, `dtbo`, `product`, `recovery`, `system`, `vbmeta`, and `vendor`. Its internal build version is dated 20260724 because generation crossed UTC midnight.
- Sideloading that OTA from the old Recovery would still fail before the OTA can replace Recovery, creating a bootstrap dependency. The exact AIDL Recovery stack is sealed read-only under ignored `lineageos/.downloads/install-images-aidl-bootctrl-20260724/`: recovery SHA-256 `c1bf16f0915ae1e3ddf1144d90f54b4798acd59aca187acf18b483e2ca881879`, DTBO `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`, and vbmeta `a10b1d18d3a654310b84df493b388e30a11ca6fbd00e9874cbddcf926b0f674c`. Source archive, AVB, component, and service-content verification pass.
- Live read-only inspection before ADB disconnected confirmed the phone was in slot-B Recovery on `4.14.336-perf+`, build `23.2-20260723-UNOFFICIAL-odessa`, with no QTI AIDL Recovery files. Current slot-B recovery/DTBO/vbmeta whole-partition hashes differ from the sealed AIDL set. No write/reboot/slot command was issued. The next destructive checkpoint is bootloader preflight followed by an explicit slot-B AIDL Recovery-stack install, preserving slot A as fallback, before retrying only the new AIDLBOOTCTRL OTA.

## 2026-07-23 AIDL BootControl final artifact regeneration

- HOST ONLY `m -j8 target-files-package vbmetaimage` completed successfully under `lineage_odessa-bp4a-userdebug` with the documented `/home/arthu/bin/sccache-android` wrapper and preserved incremental `out/`. No Android source was edited or cleaned and no phone command ran. Build log: `lineageos/.downloads/build-logs/target-files-aidl-bootctrl-20260723.log`.
- Regenerated target-files: `lineageos/out/target/product/odessa/obj/PACKAGING/target_files_intermediates/lineage_odessa-target_files.zip`, 2,614,867,109 bytes, SHA-256 `20ac2c2d7cfd0f438f2aab1da94e0b7061ce3c1e84f308632264b07b6113b29b`; ZIP integrity passed.
- Its RECOVERY tree contains the QTI AIDL executable `android.hardware.boot-service.qti.recovery`, matching init declaration, and AIDL VINTF fragment. Its VENDOR tree contains `android.hardware.boot-service.qti` with matching init and AIDL VINTF fragment. Neither tree contains an obsolete `android.hardware.boot@...` HIDL service or implementation artifact. The AIDL executables intentionally retain the branch-current HIDL interface library dependency used by the QTI implementation; this is not a shipped HIDL service/implementation.
- Standalone verbose `check_target_files_vintf` exited zero and returned `COMPATIBLE`; full log: `lineageos/.downloads/build-logs/check-target-files-vintf-aidl-bootctrl-20260723.log`. No compatibility check was bypassed.
- New installable A/B OTA: `lineageos/out/target/product/odessa/lineage-23.2-20260723-AIDLBOOTCTRL-UNOFFICIAL-odessa.zip`, 1,028,399,639 bytes, SHA-256 `d5dc8077e7fb59c5a6cd75ccfd68e4ed760cd94188997c07f4c6f2fb6eee11b1`; generator exited zero and ZIP integrity passed. Generator log: `lineageos/.downloads/build-logs/ota-from-target-files-aidl-bootctrl-20260723.log`.
- Required OTA metadata, payload properties, `payload.bin`, `care_map.pb`, and `apex_info.pb` entries are present. Payload version 2 contains exactly `boot`, `dtbo`, `product`, `recovery`, `system`, `vbmeta`, and `vendor`. Payload size is 1,028,392,345 bytes and SHA-256 is `8016bb6838940d046b250917908a1eb35805d7dc82d967b7f68360742e94b8f8`; recomputed payload properties, including metadata hash, exactly match `payload_properties.txt`.
- The recovery image extracted from this exact OTA payload is byte-identical to the target-files `IMAGES/recovery.img`: 67,108,864 bytes, SHA-256 `c1bf16f0915ae1e3ddf1144d90f54b4798acd59aca187acf18b483e2ca881879`. Unpacking that image confirmed the same QTI AIDL executable/init/VINTF triplet and no obsolete HIDL boot service/implementation.
- Complete AVB follow-chain verification passed for the exact target-files vbmeta with boot, DTBO, recovery, product, system, and vendor. The OTA payload's vbmeta is byte-identical to target-files `IMAGES/vbmeta.img`, SHA-256 `a10b1d18d3a654310b84df493b388e30a11ca6fbd00e9874cbddcf926b0f674c`.
- Provenance caveat: mutable loose `out/target/product/odessa/vbmeta.img` has SHA-256 `45c80ab670b819d03041ca7087cf0a36e2ef352292c64c4d86f2c75369fc292d` and differs from the exact target-files/OTA vbmeta. Continue to use images extracted from the exact target-files/OTA pair, not loose `out/` images. The prior DWC3 and July 19 OTA hashes remain unchanged, proving they were not overwritten.
- The build environment emitted internal `LINEAGE_VERSION=23.2-20260724-UNOFFICIAL-odessa` because its UTC build date had crossed midnight, while the explicitly requested output filename retains `20260723`. This naming difference does not affect the verified target-files-to-OTA provenance.

## 2026-07-24 OTA slot-activation failure and UFS BSG fix

- The latest live Lineage Recovery `recovery.log` proves the AIDL BootControl migration resolved the previous pre-payload rejection. Whole-file and payload signatures pass, the full OTA is applied to target slot A, and `boot_a`, `dtbo_a`, `product_a`, `recovery_a`, `system_a`, `vbmeta_a`, and `vendor_a` all hash-verify against the payload.
- The fatal status-5 error occurs only afterward when AIDL `IBootControl.setActiveBootSlot(0)` returns service-specific error `-2`. The recovery postinstall message `boot-complete not detected` is nonfatal because update_engine records all postinstall commands as successful before slot activation. The missing `/metadata/ota` lock explains the repeated checkpoint/resume warnings but does not stop payload application or verification.
- Root cause is the shared device configuration forcing QTI GPT utilities onto the legacy UFS `/dev/sg*` ioctl path. `device/motorola/sm6150-common/common.mk` now sets `QTI_GPT_UTILS,USE_BSG_FRAMEWORK` to `true`, selecting the current `/dev/ufs-bsg*` `SG_IO` transport used when the QTI AIDL service changes the XBL boot LUN.
- The user's HOST ONLY recovery build incorporated the fix. `out/soong/build.lineage_odessa.incremental.ninja` contains `-D_BSG_FRAMEWORK_KERNEL_HEADERS` for the recovery `libgptutils.qti` variant. Rebuilt `out/target/product/odessa/recovery.img` is 67,108,864 bytes, SHA-256 `255372e1fc3d5e5d1fea36db71a43d52bd5b46775410835dec939dcc164d6e6b`; its unpacked AIDL recovery service is 136,936 bytes, SHA-256 `d936417b60ce6b81b11d4a6d16bce0b5af5c93b839daca79ab6f9cfe26ef2006`.
- No phone command was issued while diagnosing or fixing this failure. The raw root-level `recovery.log` is untracked and contains device identifiers; never commit or share it without redaction.
- Critical state warning: the failed sideload used source slot B and target slot A, and it fully wrote and verified the LineageOS payload on slot A before activation failed. Do not assume slot A still contains TequilaOS or remains a known-good fallback. Re-query bootloader slot metadata and establish the actual bootable recovery path before any further write, reboot-to-system, or OTA retry.

## 2026-07-24 Recovery fastboot partition rejection

- The user attempted unsuffixed `dtbo`, `vbmeta`, and `recovery` flashes from Recovery's limited fastboot mode. Each image transfer completed, but every write returned `Invalid partition name`; `reboot recovery` was also rejected. No partition was written by this attempt.
- Read-only fastboot queries in that mode reported `odessa`, `is-userspace: no`, current slot A, but an impossible `slot-count: 1`, unknown metadata for both slots, and no sizes for explicit `dtbo_a/b`, `recovery_a/b`, or `vbmeta_a/b`. Treat this interface as Recovery fastboot despite its incorrect userspace report; it does not expose the physical A/B partitions. Do not retry a flash there.
- The attempted mutable loose outputs are not an internally reviewed set: `out/target/product/odessa/dtbo.img` is SHA-256 `9ec96bbc7858e3aef73fa09836be427d511fcec525b2164c176e307877dd9200`, loose `vbmeta.img` is `45c80ab670b819d03041ca7087cf0a36e2ef352292c64c4d86f2c75369fc292d`, and the BSG-rebuilt `recovery.img` is `255372e1fc3d5e5d1fea36db71a43d52bd5b46775410835dec939dcc164d6e6b`. Do not flash them together or substitute the old sealed AIDL vbmeta; regenerate and verify a matching target-files/AVB set first.
- The phone remains in the limited fastboot interface after the rejected recovery reboot. The next safe transition is to Motorola bootloader fastboot only, without booting system or switching slots, then repeat read-only A/B metadata checks. Slot A remains critical because the prior OTA fully wrote it before activation failed.
- Correction after visual and USB verification: this is Motorola `AP Fastboot Flash Mode (Secure)`, USB `22b8:2e80`, running MBM `...-220629`, not Recovery fastboot. A warm `reboot bootloader` and a full power-off/cold Volume-Down+Power boot both retained the abnormal one-slot view and absent physical partition map. MBM still reports `odessa`, `flashing_unlocked`, and normal battery voltage but cannot enumerate `boot_a/b`, `dtbo_a/b`, `recovery_a/b`, `vbmeta_a/b`, or `super`.
- Selecting Recovery now returns `No operational system found`. The user ran Recovery Factory reset twice; this affects userdata/metadata but cannot remove the physical GPT and is not the cause of MBM's missing partition map.
- Source review confirms QTI `set_active_boot_slot()` updates GPT attributes before attempting the UFS XBL boot-LUN switch. The OTA log's later `-2` therefore permits a partial state where slot A attributes were changed but the boot LUN switch failed. Do not attempt a manual `set_active`, erase, GPT flash, or loose-image flash to repair this state.
- The accepted recovery path is now the documented **DESTRUCTIVE** Motorola Software Fix Rescue using the automatically selected exact-device `ODESSA_RETAIL_RPAS31.Q2-59-17-4-3-9` package. Do not improvise its `flashfile.xml` as manual fastboot commands, use EDL/QFIL, relock, or substitute the older Android 10 package.

## 2026-07-24 install failure root cause: UFS BSG vs sg boot-LUN transport

This entry **corrects and supersedes** the "UFS BSG fix" root cause recorded on 2026-07-24 ("Root cause is the shared device configuration forcing QTI GPT utilities onto the legacy UFS `/dev/sg*` ioctl path ... now sets `USE_BSG_FRAMEWORK` to `true`"). That analysis was inverted; see below.

### Proven from the live recovery.log (AIDLBOOTCTRL OTA, slot-B Lineage Recovery)

- The A/B install does **not** fail writing the payload. All 2268 payload operations completed; `boot_a`, `dtbo_a`, `product_a`, `recovery_a`, `system_a`, `vbmeta_a`, and `vendor_a` all hash-verified against the payload (`FilesystemVerifierAction` kSuccess).
- The only fatal error is the final slot-activation step: `IBootControl.setActiveBootSlot(0)` returned service-specific `-2: Operation failed` → `ErrorCode::kPostinstallRunnerError` → recovery `Error in /sideload/package.zip (status 5)` → "Installation aborted".
- `markBootSuccessful` and `setSlotAsUnbootable` earlier in the same session are **best-effort** in update_engine (log-only on failure), so the log cannot prove they succeeded; however, the bootloader subsequently seeing slot A as current proves the GPT attribute flip inside `set_active_boot_slot()` did commit before the `-2`.
- The `otapreopt_script: Error: boot-complete not detected.` message is normal for recovery sideloads and nonfatal. `/metadata` and `userdata` had invalid ext4/f2fs superblocks at recovery start — leftovers of prior near-brick episodes/Software Fix restores, not causes of this failure. The "downgrade" warning is expected because the running recovery build (2026-07-23 22:12) was newer than the OTA (21:01).

### Root cause (verified in source, kernel, and binaries)

- QTI `set_active_boot_slot()` flips GPT slot attributes first (succeeded), then switches the UFS boot LUN via `gpt_utils_set_xbl_boot_partition()` → `set_boot_lun()` (failed). `set_boot_lun()` has two compile-time transports: BSG (`/dev/ufs-bsg*` + `SG_IO`) or legacy sg (`/dev/sgN` + `UFS_IOCTL_QUERY`).
- `hardware/qcom-caf/bootctrl/gpt-utils/Android.bp` selects the transport with `select(soong_config_variable("QTI_GPT_UTILS", "USE_BSG_FRAMEWORK"), { false: [], default: ["-D_BSG_FRAMEWORK_KERNEL_HEADERS"] })`. When the variable is **unset**, Soong's `default:` arm matches (verified in build/soong docs and `module.go`), so **BSG was compiled into the AIDLBOOTCTRL build even though nobody set the variable**. Confirmed: the sealed failing recovery image (`.downloads/install-images-aidl-bootctrl-20260724/recovery.img`, SHA-256 `c1bf16f0...`) contains `ufs-bsg` strings (4 hits).
- Odessa's 4.14 kernel has **no** `CONFIG_SCSI_UFS_BSG` — the option does not exist in `drivers/scsi/ufs/Kconfig` and is absent from `vendor/odessa_defconfig` — so `/dev/ufs-bsg*` never exists. `get_ufs_bsg_dev()` returns `-ENODEV`, `set_boot_lun()` fails, `setActiveBootSlot()` returns -2. This is the whole install failure.
- Therefore the earlier `USE_BSG_FRAMEWORK=true` edit was a **no-op** (BSG was already on via the default arm). The BSG-"fixed" recovery (`255372e1...`) would have failed identically; it was never install-tested because the phone was already in the broken state.

### Why the failed install nearly bricks the phone

The failure lands after (1) payload fully written and verified on the target slot, (2) GPT attributes for all A/B partitions flipped to target-active on both primary and backup GPTs — but **without** the UFS boot-LUN switch (`bBootLunEn` unchanged). The bootloader then sees GPT attributes saying "boot the new slot" while the boot LUN still points at the old slot's `xbl`: an inconsistent boot chain on a device whose per-slot low-level firmware differs. Symptoms match the user's report and the 2026-07-24 entries: "No operational system found", bootloader losing its A/B partition view, recovery "bugged". The accepted Software Fix Rescue rewrites the GPT and repartitions, which is the user's "it deletes the partition tables" observation (and why `userdata`/`metadata` later show invalid superblocks).

### Fix applied, built, and verified (HOST ONLY)

- `device/motorola/sm6150-common/common.mk` now sets `QTI_GPT_UTILS.USE_BSG_FRAMEWORK` explicitly to **false** (explicit is mandatory — unset also compiles BSG via the select default). `libgptutils.qti` now uses `/dev/sgN` + `UFS_IOCTL_QUERY`: supported by `CONFIG_CHR_DEV_SG=y`, `ufshcd_ioctl` (registered in the UFS host template, handles `UFS_IOCTL_QUERY`), and `sg_ioctl`'s default→`scsi_ioctl` dispatch in the 4.14.336 kernel. The recovery SELinux policy already grants `hal_bootctl` rw on `vendor_sg_device` and `vendor_gpt_block_device`. This is the same transport that stock Motorola/TequilaOS/Pixys boot control used to switch slots successfully on this exact phone (2026-07-19).
- Focused build (`android.hardware.boot-service.qti`, `.recovery`, `libgptutils.qti`) passed; log `lineageos/.downloads/build-logs/bootctrl-bsg-off-20260724.log`. Rebuilt vendor and recovery boot-service binaries contain **zero** `ufs-bsg` strings; `out/soong/soong.lineage_odessa.variables` records `USE_BSG_FRAMEWORK: ""` (bool). The failing sealed recovery contains them — binary-level before/after proof.
- Still required: regenerate target-files + OTA with this fix, re-flash matching recovery/dtbo/vbmeta from that exact build, factory-reset/format data, and sideload the new OTA. Success criterion: `Install completed with status 0` and a consistent slot switch. Do not flash loose `out/` images mixed with other builds.

### Committed and pushed

- `device/motorola/sm6150-common` `lineage-23.2`, pushed `31eea31c..496a793c` to `origin` (ARLBR10): `2ae8427a` "Remove duplicate legacy RFS directory rules"; `496a793c` "Migrate boot control to AIDL QTI service" (includes the BSG=false fix and full rationale).
- `kernel/motorola/sm6150` `lineage-23.2`, pushed `dee98796a331..5be9b397181c` to `origin` (ARLBR10): `cae5f73efe37` "ARM64: Restore Qualcomm DT overlay build option" (Kconfig + dts Makefile); `5be9b397181c` "usb: dwc3: Drop suspended-event path incompatible with Qualcomm glue" (the hardware-tested Recovery-ADB fix, previously uncommitted).
- All five project repos are now clean and in sync with their `origin/lineage-23.2` branches.

### Corrections to earlier interim concerns

- The Android.mk RFS rule removal does **not** remove runtime RFS symlinks: `hardware/qcom-caf/common` installs the child links via Soong `install_symlink`; verified present in `out/target/product/odessa/vendor/rfs/msm/adsp/` (`hlos`, `ramdumps`, `readonly`, `readwrite`, `shared`). No modem-side follow-up is owed for that change.
- Full Android boot on the merged `4.14.336-perf+` kernel (recovery boot proven, Android not yet) remains the next hardware milestone after a successful install; pstore/ramoops capture plan from earlier entries applies.
- Device state before any retest: re-verify identity, slot metadata, and fallback with bootloader fastboot first; the phone was last known in the post-failed-install inconsistent state, and the user restores it via the documented Software Fix path.

## 2026-07-24 successful OTA install, ABL boot rejection, and AVB vbmeta flags

Full detail: `docs/avb-vbmeta-flags-boot-failure-20260724.md`.

### The A/B install pipeline is now proven on hardware

- The user wiped, sideloaded `lineage-23.2-20260724-UNOFFICIAL-odessa.zip` (1,028,460,442 bytes, SHA-256 `4e4944d0f69480e47b46fffcb7e645a4654e4553e04bd63709116802c89f428a`) from Lineage Recovery on slot B, and pulled `/tmp/recovery.log` before rebooting.
- The log shows `Using AIDL version of IBootControl`, `source_slot: B` / `target_slot: A`, dynamic-partition metadata created and copied, `boot_a`/`dtbo_a`/`recovery_a`/`vbmeta_a` hash-verified, `DownloadAction`/`FilesystemVerifierAction`/`PostinstallRunnerAction` all `ErrorCode::kSuccess`, `Update successfully applied`, and `Install completed with status 0`.
- There is no `SetActiveBootSlot` error line; update_engine logs that call only on failure, so slot activation succeeded.
- This supersedes the open failure in "2026-07-24 OTA slot-activation failure and UFS BSG fix" and "2026-07-24 install failure root cause: UFS BSG vs sg boot-LUN transport". The AIDL BootControl migration and `QTI_GPT_UTILS.USE_BSG_FRAMEWORK := false` are validated. Do not reopen them.
- The untracked project-root `recovery.log` is the captured artifact. It contains device identifiers; never commit or share it unredacted.

### Firmware slot asymmetry is eliminated as a cause

- The user flashed the official `RPAS31.Q2-59-17-4-3-9` package with explicit `_b` suffixes for `bootloader`, `radio`, `bluetooth`, `dsp`, and `logo`; slot B then booted stock Android 11. The following OTA targeted slot A, which also held freshly flashed stock firmware, and failed identically.
- Current, self-consistent low-level firmware on the target slot does not change the symptom. The `docs/first-install-checkpoint.md` firmware-synchronization gate is answered by experiment: it was not the blocker. `copy-partitions` remains prohibited.

### Motorola MBM slot-suffix quirk

- Unsuffixed `fastboot flash <partition>` from Motorola AP Fastboot Flash Mode wrote to `_a` partitions even with slot B active. Both stock `flashfile.xml` and `servicefile.xml` use only unsuffixed names, so a stock restore refreshes one slot only, and not necessarily the selected one. Always use explicit suffixes when a specific slot matters, and re-verify.

### Actual failure and leading root cause

- After the successful install and slot switch, the bootloader reports `No valid operating system could be found` with `OS Fingerprint: N/A`, immediately, with no boot animation and no repeated attempt. The fingerprint is an AVB property descriptor inside `vbmeta`, so ABL rejected the slot before reading it.
- HOST ONLY `avbtool info_image` comparison: stock `RPAS31` vbmeta uses the Motorola key `fd29248b78aa9d6427e8f569eda90be62b9fa0ee`, SHA256_RSA2048, flags 0, rollback index 16. Tequila/Pixys, proven to boot Android on this phone, uses the AOSP test key `2597c218aae470a130f61162feaae70afd97f011`, SHA256_RSA4096, **flags 3**, rollback index 0. The failing LineageOS build uses the same AOSP test key, SHA256_RSA4096, **flags 0**, rollback index 0.
- The signing key is therefore not the discriminator; the vbmeta flags field is. Flags 3 is `VERIFICATION_DISABLED | HASHTREE_DISABLED`.
- `device/motorola/sm6150-common` commit `31eea31c` (2026-07-16, "Remove stale legacy integration") deleted `BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --flags 3`. That line is upstream LineageOS configuration for this platform, added by the LineageOS Motorola SM6150 maintainer in `8db0b6129ceb90f100aedcdd59f2a51816ea0d30` ("Simplify AVB flag logic"). Every hardware install attempt after `31eea31c` failed this way.
- Unresolved counter-evidence: flags-0 test-key vbmeta images did boot Lineage Recovery repeatedly (verified `Flags: 0` on `diagnostic-recovery-4.14.310-boot-test-20260723` and `diagnostic-recovery-4.14.190-20260719`). This bootloader tolerates a verification-enabled custom-key vbmeta on the recovery path but apparently not on normal boot; the mechanism is not proven, and the rollback index 0 against a stored 16 may contribute. Treat the flags restoration as the leading hypothesis, not a proven cause, until a flags-3 build boots.

### Change applied and security consequence

- `device/motorola/sm6150-common/BoardConfigCommon.mk` restores `BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --flags 3` with an explanatory comment. Uncommitted pending a hardware result.
- This is a real reduction relative to stock and must be carried into Phase 8 as an explicit documented limitation. Do not describe the result as verified boot, and do not extend the precedent to SELinux permissive, disabled encryption, or disabled update verification.

### Verified device state

- Read-only bootloader queries after the user's stock restore: `product: odessa`, `securestate: flashing_unlocked`, `secure: yes`, `is-userspace: no`, `slot-count: 2`, `current-slot: a`, full physical partition map enumerable (`boot_a/b`, `recovery_a/b`, `dtbo_a/b`, `xbl_a/b`, `modem_a/b`, unslotted `super` 0x244000000), `slot-unbootable:a/b: no`, `slot-retry-count:a: 7`, `slot-retry-count:b: 0`, `slot-successful:b: no`, bootloader `MBM-3.0-odessa_retail-e69c40c38d6-22...`. This is a healthy view, unlike the earlier `slot-count: 1` near-brick state.
- Querying `slot-successful:a` reset the USB fastboot session once; the device re-enumerated on its own. Treat that variable as unreliable on this bootloader.

### Next steps

- The user runs the rebuild (their shell has the consistent sccache configuration). Verify the regenerated vbmeta reports `Flags: 3` before flashing.
- Keep a stock bootable fallback slot; slot B currently holds full stock firmware and booted Android 11.
- Always capture `/tmp/recovery.log` before rebooting after a sideload; it is what made this diagnosis possible.
- If boot still fails, read `/sys/fs/pstore/` from Lineage Recovery after the failed attempt to separate an ABL-stage rejection from a kernel-stage failure.

## 2026-07-24 vbmeta flags disproven; UFS boot LUN / GPT slot mismatch found

Full detail: `docs/boot-lun-slot-mismatch-20260724.md` and the result section of `docs/avb-vbmeta-flags-boot-failure-20260724.md`.

- The AVB flags hypothesis is **disproven**. The rebuild's vbmeta reports `Flags: 3` with the AOSP test key, matching the Tequila/Pixys configuration exactly; `lineage-23.2-20260724-FLAGSFIX-UNOFFICIAL-odessa.zip` again installed with `Install completed with status 0` and the boot failure was unchanged. `BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --flags 3` is kept because it matches upstream LineageOS sm6150-common, not because it fixed anything.
- First inspection of the phone in the **post-failure state** before any restore. `fastboot getvar all` reported `current-slot: a` but `running-boot-lun: 2`, plus `running-bl-slot: unknown/_a`, `slot-count: 1`, all slot metadata `unknown`, and empty `partition-size` for `boot_a`, `boot_b`, and `super`. `logical-block-size` is `0x1000`.
- In QTI `gpt-utils`, `BOOT_LUN_A_ID` is 1 and `BOOT_LUN_B_ID` is 2. The GPT attributes therefore point at slot A while the SoC still boots XBL from slot B. MBM detects the split boot chain, degrades to a one-slot view, and stops enumerating partitions. **This degraded view is the recurring near-brick state**, and it is why a full `gpt.bin` plus stock reflash is needed to recover.
- `set_active_boot_slot()` rewrites GPT attributes first and only then switches the boot LUN, returning -1 if the switch fails. `update_engine` logged no error, so the code believed the switch succeeded while the bootloader shows it did not. The two steps are not atomic, so any step-3 failure leaves this exact state.
- Eliminated on the host with the exact sources and built binaries: BSG-versus-sg transport (sg is compiled in; the recovery boot service contains `UFS query ioctl failed` and `scsi_generic` strings and no `ufs-bsg` strings); the `_GENERIC_KERNEL_HEADERS` silent-no-op branch in `recovery-ufs-bsg.cpp` (that macro appears zero times in the generated ninja, though it remains a trap if build flags change); `is_ufs` being false (`ro.boot.bootdevice=1d84000.ufshc` is present in the recovery log); and kernel support (`ufshcd_ioctl` handles `UFS_IOCTL_QUERY`, and `ufshcd_query_ioctl` accepts `WRITE_ATTR` for `QUERY_ATTR_IDN_BOOT_LU_EN`).
- **Correction:** the 2026-07-24 "UFS BSG vs sg boot-LUN transport" entry concluded that compiling the sg transport would fix slot activation. It did not. Its diagnosis that BSG is unusable on this kernel stands; its conclusion that this was the whole install failure does not. Likewise, slot activation is not "validated" — only the return value is.
- **Open gap:** no healthy-state baseline exists for `running-boot-lun` and `running-bl-slot`. Capture `fastboot getvar all` on a restored, booting stock slot-A device before any further code change. Expected if the diagnosis holds: `running-boot-lun: 1`, `running-bl-slot: _a/_a`, `slot-count: 2`.
- This 4.14 tree exposes no UFS sysfs attribute for the boot LUN. Reading it at runtime needs a small `READ_ATTR` helper, which the kernel does support.
- Do not re-run an OTA install until the boot LUN switch is proven or replaced; each attempt reproduces the split boot chain and forces a full stock reflash. Manual `fastboot set_active` remains prohibited and was not attempted.

## 2026-07-24 CORRECTION: boot LUN is not the failure; MBM cannot read the GPT

- The healthy-state baseline was captured on a restored, booting stock device and confirmed directly: `current-slot: a`, `running-bl-slot: _a/_a`, **`running-boot-lun: 2`**, `slot-count: 2`, all partitions enumerable, `logical-block-size: 0x1000`.
- **`running-boot-lun: 2` is the normal value on this device for slot A.** It is identical in the healthy and failed states. The "UFS boot LUN / GPT slot mismatch" conclusion recorded earlier the same day is **wrong** and is corrected in place at the top of `docs/boot-lun-slot-mismatch-20260724.md`. `set_boot_lun()` is not proven broken.
- The failure signature reduces to exactly one fact: after a successful OTA install, MBM can no longer read the partition table. `running-bl-slot` degrades to `unknown/_a`, `slot-count` drops to 1, and `partition-size` for `boot_a`, `boot_b`, and `super` returns empty. Everything else follows from that, including why recovery requires reflashing `gpt.bin`.
- Still standing and independently verified: the install is complete and correct with all target partitions hash-verified and status 0; slot activation returns success; and the eliminations of BSG-versus-sg, the `_GENERIC_KERNEL_HEADERS` no-op branch, `is_ufs`, kernel `WRITE_ATTR` support, AVB flags, and firmware slot asymmetry.
- Remaining suspect, **not** a conclusion: `boot_ctl_set_active_slot_for_partitions()` → `gpt_disk_commit()`, which rewrites all four GPT structures (primary header, primary entry array, secondary header, secondary entry array) on every call. An offset or size error there would corrupt both copies at once. The code reads the block size via `BLKSSZGET` rather than assuming 512, but correctness of every offset for 4 KiB logical blocks is unverified.
- Three confident root causes have now been wrong in one session (firmware asymmetry, AVB flags, boot LUN). Do not record another without a measurement.
- Planned measurement, pending user approval: build AOSP `bootctl` (`system/extras/bootctl`), flash Lineage Recovery to both slots with explicit suffixes, capture the GPT read-only from recovery ADB, run `bootctl set-active-boot-slot` alone with no OTA, recapture, and diff on the host. This keeps bootable stock on slot A throughout and isolates the single suspect operation.

## 2026-07-24 ROOT CAUSE PROVEN: slot activation marks the target slot's XBL unbootable

Full detail: `docs/xbl-unbootable-root-cause-20260724.md`. This supersedes every earlier root-cause claim for "No valid operating system could be found".

- Method: `tools/capture-gpt.sh` run from Lineage Recovery immediately before the sideload and again immediately after `Install completed with status 0`, without rebooting; decoded and diffed on the host with `tools/decode-gpt.py`. Install ran source slot A, target slot B.
- **The GPT is not corrupted.** All primary and backup header CRCs and entry-array CRCs are valid on every LUN, and no partition name or LBA range changed. Only attribute bytes changed.
- Partition-to-LUN map on this device: `sdc` = `xbl_a`/`xbl_config_a`; `sdd` = `xbl_b`/`xbl_config_b`; `sde` = slot A boot/recovery/dtbo/vbmeta/modem/firmware; `sdf` = slot B equivalents; `sdb` = `super` + `userdata`; `sda` = small misc.
- Decisive diff: `xbl_b`, `xbl_config_b`, `multiimgoem_b`, and `multiimgqti_b` went `0x00` to **`0x80` unbootable**, while every other slot-B partition went `0x00` to `0x3f` active. Slot A deactivated correctly (`0x44` to `0x40`), and `xbl_a` stayed `0x44 active,successful`.
- Cause: `boot_control.cpp` has two attribute writers and only one excludes the UFS boot-LUN partitions. `set_active_boot_slot()` skips `xbl`, `xbl_config`, `multiimgoem`, `multiimgqti` when `gpt_utils_is_ufs_device()`; `update_slot_attribute()` did not. `update_engine` calls `setSlotAsUnbootable(target)` at install start (log line `Marking new slot as unbootable`), which marks every target partition unbootable including `xbl`; `setActiveBootSlot(target)` then skips those four, so the unbootable bit is never cleared.
- This explains the immediate failure with no boot animation, `OS Fingerprint: N/A`, why reflashing `gpt.bin` recovers, why firmware sync / AVB flags / boot LUN were all irrelevant, why `fastboot set_active` slot switches always worked (MBM implements that itself), and why the earlier BSG `-2` failure also bricked the phone.
- Fix committed as `5d92d9f` in `hardware/qcom-caf/bootctrl` (base `846dfb0`): `update_slot_attribute()` now applies the same exclusion, factored into one shared `ptn_selected_by_ufs_boot_lun()` predicate used by both call sites.
- **Residual uncertainty:** the fix leaves `xbl_b` at `0x00` and `xbl_a` at `0x44` because the code now never touches either, matching the upstream premise that the boot LUN selects them. It is not proven that MBM agrees; if it also needs the active bit moved, a further swap is required. `0x80` on the activating slot is wrong under any reading, and this is the minimal upstream-consistent change. The next install will show, and the GPT capture makes it observable.
- **Repository placement problem:** `hardware/qcom-caf/bootctrl` is an upstream LineageOS repo, not one of the five tracked repos and not pinned in `manifests/odessa.xml`, so `repo sync` would discard the fix. It is exported to `patches/hardware-qcom-bootctrl/` as a stopgap. Fork it to the project remote and pin it, as was done for the kernel, before treating the build as reproducible.
- New tooling, validated against a real GPT before use: `tools/capture-gpt.sh` (READ ONLY on-device capture of GPT metadata only) and `tools/decode-gpt.py` (host-side decode/diff with CRC validation and A/B attribute decoding). Known gap: `sdb` was skipped by the capture loop and its `-b` guard; harmless here since `super`/`userdata` are not slotted, but worth fixing.

## 2026-07-24 recovery bootstrap: the fix was never actually tested

- The bootctrl fix was built (binaries 18:39, `recovery.img` 18:46) but the phone still ran a recovery built at **16:09**, so the 18:52 install exercised the **old** code. Confirmed from `ro.build.version.incremental=1784920145` in the pulled recovery log.
- The rebuilt `recovery.img` does contain the fix: the embedded `system/bin/hw/android.hardware.boot-service.qti.recovery` is byte-identical to the freshly built binary, SHA-256 `e79b61a8080011a8bb8960d2cdaa5215be55eb3b1117883ae01c3fbc68ce7c25`.
- The 18:52 capture diff still shows `xbl_b`/`xbl_config_b`/`multiimgoem_b`/`multiimgqti_b` going `0x00` to `0x80`, plus `xbl_a`/`multiimgoem_a`/`multiimgqti_a` going `0x04` to `0x44` from `markBootSuccessful` — all old-code behaviour.
- **Durable operational rule:** the boot-control HAL that writes GPT slot attributes during a sideload is the one inside the **running recovery**, not the one in the OTA payload. Any boot-control change must be flashed as a new `recovery` and booted *before* the install that is meant to test it. Building modules, or even `recovery.img`, changes nothing on device by itself. This is the same bootstrap dependency recorded for the AIDL BootControl migration.
- Always confirm which recovery is running before trusting a result: compare `ro.build.version.incremental` in `/tmp/recovery.log` against the build time of the artifact that was flashed.
- `hardware/qcom-caf/bootctrl` is now pinned in `manifests/odessa.xml` to fork `ARLBR10/android_hardware_qcom_bootctrl` at `5d92d9f0e1d531adc3ad63efc219bf4abde2d09f`, with a `<remove-project>` for the upstream entry. `.repo/local_manifests/odessa.xml` is a symlink to that file, so the pin is already active. The fork must be created and pushed or `repo sync` will fail.

## 2026-07-24 CORRECTION: the bootctrl fix was applied to dead code

- The first fix went into `hardware/qcom-caf/bootctrl/boot_control.cpp`, which **is not compiled** for this product. Two hardware installs were burned before this was caught. The GPT captures were right all along; the code under test never changed.
- That repository carries two copies of the same implementation. `boot_control.cpp` backs the legacy HIDL `bootctrl_hal_defaults` module and is unused here. `1.1/libboot_control_qti/libboot_control_qti.cpp` is what the AIDL `android.hardware.boot-service.qti` binaries actually compile, via `libboot_control_qti_defaults`. Build-graph proof: the recovery service's objects are `BootControl.o`, `libboot_control_qti.o`, `main.o`; the ninja references `libboot_control_qti.cpp` 24 times and `bootctrl/boot_control.cpp` zero times.
- Both files are now fixed in commit `6863795de5ec856c98244b1e5c3a4cd1f1b9be1c` (amended from the earlier `5d92d9f`, never pushed). `manifests/odessa.xml` pins the new SHA.
- **Also wrong:** the claim that the phone was running an older recovery, based on `ro.build.version.incremental=1784920145` versus a refreshed `out/build_date.txt`. The rebuilt `recovery.img` carries the same `ro.build.date.utc=1784920145` internally, so that property never distinguished builds. **Do not use build timestamps to identify which recovery is running.**
- **Reliable check instead:** compare `adb shell sha256sum /system/bin/hw/android.hardware.boot-service.qti.recovery` on the phone against the same path unpacked from the `recovery.img` being flashed. The dead-code build's hash was `e79b61a8080011a8bb8960d2cdaa5215be55eb3b1117883ae01c3fbc68ce7c25`; a build with the real fix must differ.
- General lesson for this codebase: before trusting that a source change is under test, confirm the file appears in `out/soong/build.lineage_odessa.incremental.ninja` and that its object exists in the module's intermediates.

## 2026-07-24 XBL-unbootable fix verified working; boot still fails. SESSION HANDOFF

Start here: `docs/handoff-20260724-evening.md`.

- The bootctrl fix is **confirmed working on hardware**. Post-fix GPT capture: `xbl_a`/`xbl_config_a`/`multiimgoem_a`/`multiimgqti_a` unchanged at `0x04 active`, `xbl_b`/`xbl_config_b`/`multiimgoem_b`/`multiimgqti_b` unchanged at `0x00`, slot A `0x04` to `0x40`, slot B `0x00` to `0x3f`, `Install completed with status 0`. No GPT corruption at any point; all CRCs valid and no LBA range ever changed.
- **The device still does not boot**: `No valid operating system could be found`, `OS Fingerprint: N/A`. So the XBL-unbootable bug was real and is fixed, but it was not the whole cause.
- Open question: after activating slot B, `xbl_a` remains `0x04 active` and `xbl_b` is `0x00`, because the fix follows upstream in never touching them. **That premise is unconfirmed for this bootloader.** Leading next hypothesis: MBM does read XBL attribute bits and the active bit must swap to `xbl_b`, meaning upstream's blanket UFS skip is wrong for this device. Correct behaviour would be to swap active/inactive on the XBL pair while never marking either unbootable.
- Unexplained and worth resolving: a healthy stock slot-A device reports `running-boot-lun: 2`, but `gpt-utils` maps slot A to `BOOT_LUN_A_ID` = 1. The value was identical in healthy and failed states so it has not been shown to matter, but the mismatch is unexplained.
- Fork pushed: `ARLBR10/android_hardware_qcom_bootctrl` branch `lineage-23.2` at `6863795de5ec856c98244b1e5c3a4cd1f1b9be1c`, pinned in `manifests/odessa.xml` with a `<remove-project>` for the upstream entry.
- Disproven by hardware experiment, do not revisit: firmware slot asymmetry, AVB vbmeta flags, UFS boot LUN mismatch, GPT corruption, BSG-versus-sg transport, `_GENERIC_KERNEL_HEADERS`, `is_ufs`, kernel `WRITE_ATTR` support.
- Next unexplored evidence if the XBL-swap hypothesis fails: read `/sys/fs/pstore/` from recovery after a failed boot. Nothing yet rules out the simpler possibility that this ROM has never booted Android on this hardware — recovery boot is proven, Android boot is not.

## 2026-07-24 night: degraded state measured; booting `xbl_b` is the failure

Full detail: `docs/xbl-boot-lun-degraded-state-20260724.md`.

- The post-failed-install "semi-brick" was queried read-only with `fastboot getvar`. ABL is alive and correct (`MBM-3.0-odessa_retail-e69c40c38d6-220818`, the RPAS31 bootloader) but enumerates **zero partitions**: every `partition-size:` query returns empty, including `boot`, `super`, `gpt`, `partition`, and even `xbl`/`xbl_a`/`xbl_b`. `has-slot:boot: no`, `slot-suffixes: not found`, `slot-count: 1`, and all slot metadata `unknown`. `Invalid partition name boot_a` is a symptom of that, not a suffix problem. The Rescue still works because `flashfile.xml` uses only unsuffixed names.
- **`running-boot-lun` is resolved and is not an anomaly.** It reports the UFS LUN index: 2 = `sdc` = `xbl_a`, 3 = `sdd` = `xbl_b`. Healthy stock on slot A reads 2; the failed slot-B state reads 3. Close the "unexplained mismatch" open question from `docs/handoff-20260724-evening.md`.
- Therefore `set_boot_lun()` **works**. The install really moved the SoC's XBL source to `xbl_b`. It is not silently failing.
- **Why every slot-B test passed and every OTA failed:** all kernel/recovery slot-B tests used `fastboot set_active b`, which MBM implements itself and which flips GPT attributes only, leaving the boot LUN at 2 — so they kept booting the known-good `xbl_a`. The A/B OTA path is the only thing that has ever called `gpt_utils_set_xbl_boot_partition()` and moved the SoC onto `xbl_b`. **Booting from `xbl_b` is the failure.**
- The XBL-unbootable fix (`ARLBR10/android_hardware_qcom_bootctrl` `6863795d`) is still a real, hardware-confirmed bug fix. It was not this bug. Do not revert it.
- `bootloader.img` is a `SINGLE_N_LONELY` container whose recipe flashes fourteen **unsuffixed** partitions: `cmnlib cmnlib64 keymaster hyp tz devcfg storsec uefisecapp prov aop abl qupfw xbl_config xbl`. With the Motorola unsuffixed-writes-to-`_a` quirk, **every stock restore in this project refreshed slot A's low-level firmware and never slot B's.** The 2026-07-19 comparison already found `xbl`/`xbl_config` differing between slots.
- Two candidates remain, separable by a free read-only measurement: **(A)** `xbl_b`/`xbl_config_b` content is stale or bad; **(B)** switching the boot LUN at all is wrong on this device, since MBM's own `set_active` never does it and LineageOS OTAs never update `xbl`.
- Next-session sequence: restore stock; confirm `current-slot: a`, `running-boot-lun: 2`, `slot-count: 2`; flash Lineage Recovery unsuffixed; from recovery root ADB hash the fourteen firmware partitions on both slots. If `xbl`/`xbl_config` differ, flash `bootloader_b` from the RPAS31 package and rerun the OTA (no rebuild). If they are identical, make `gpt_utils_set_xbl_boot_partition()` a no-op and let the `xbl` pair follow GPT attributes, then rebuild recovery and flash it before the install.

### Host findings the same night (HOST ONLY)

- The LineageOS `boot.img` and `vbmeta.img` are structurally equivalent to the known-booting Tequila configuration: boot header v2, 4096-byte pages, embedded dtb, AOSP test key `2597c218aae470a130f61162feaae70afd97f011`, SHA256_RSA4096, flags 3, rollback index 0. There is no boot-image-format or AVB-composition blocker.
- **The `GPTFIX` OTA zip is not internally the fixed build.** Its embedded `system/bin/hw/android.hardware.boot-service.qti.recovery` hashes to `e79b61a8080011a8bb8960d2cdaa5215be55eb3b1117883ae01c3fbc68ce7c25`, the recorded dead-code hash. The real fix (`1e55e8fce77e70a0b7048700ce5b23ffd24cc13d571b7ac234280f4948c91584`) exists only in `out/target/product/odessa/recovery.img`, built after the zip was sealed. The hardware result stands because that recovery was flashed separately, but the installed ROM carries an unfixed vendor boot-control HAL. Regenerate the OTA from the fixed tree before any real A/B update.
- `multiimgoem_*` and `multiimgqti_*` live on `sde`/`sdf`, the ordinary slot LUNs — not on the boot LUNs `sdc`/`sdd`. Upstream's `ptn_selected_by_ufs_boot_lun()` predicate therefore over-applies to them, and the fix now pins `multiimgoem_b`/`multiimgqti_b` at `0x00` permanently. Their contents are identical across slots (2026-07-19), so this is probably benign, but narrow the predicate to `xbl`/`xbl_config` on the next rebuild.
- A self-consistent, AVB-verified image set was extracted from the exact `GPTFIX` target-files into ignored `lineageos/.downloads/gptfix-images/` (no rebuild needed): `boot.img` `6c687d09...c631`, `dtbo.img` `8d807087...7293`, `vbmeta.img` `cd2b4dae...c716`, `recovery.img` `9716e188...32f3`, and `super.img` `e3cbcbb0...4daf` (2,601,933,248 bytes sparse, built with `build_super_image.py`). Every vbmeta hash descriptor matches its image footer.
- Raw `fastboot getvar all` output contains the USB serial, `uid`, `battid`, and `pcb-part-no`. It was kept in the session scratchpad only; never commit it.

## 2026-07-25 ROOT CAUSE FOUND AND FIXED: the XBL pair is selected by GPT attributes, not the boot LUN

This supersedes every earlier root-cause claim for "No valid operating system could be found" and for the recurring near-brick. Proven by measuring the bootloader's own behaviour, twice.

### The measurement that settled it

- `fastboot set_active b` (MBM's own slot switch) was captured with `tools/capture-gpt.sh`. MBM sets **all 24 A/B partitions**, including `xbl_b`, `xbl_config_b`, `multiimgoem_b`, `multiimgqti_b`, to `0x04 active`, and clears the `_a` copies to `0x00`. It leaves `bBootLunEn` alone: `running-boot-lun` stayed 2.
- Independently confirmed on the failure path: after the LineageOS boot failed its retries, ABL performed a full fallback to slot A **and flipped `xbl_a`/`multiimgoem_a` back to `0x04 active` itself**.
- Therefore upstream QTI's premise — that on UFS these four partitions are selected by the boot LUN and their GPT attributes are irrelevant — is **false on this device**. Skipping them left twenty partitions pointing at one slot and four at the other; MBM saw a split boot chain and refused to enumerate the partition table at all (`slot-count: 1`, every `partition-size` empty, `has-slot:boot: no`). That degraded bootloader, not GPT damage, was the "nuked partition table" all along.
- The encoding is **not** the issue: QTI-style `0x3f`/`0x3a` on `boot_a`/`boot_b` coexisted with a perfectly healthy MBM.

### Fix (five files, gated behind one soong config bool)

`XBL_SLOT_BY_GPT_ATTRIBUTES` = "this device selects the XBL chain by GPT attributes, like its bootloader actually does":

- `hardware/qcom-caf/bootctrl/1.1/libboot_control_qti/libboot_control_qti.cpp` and `boot_control.cpp`: `ptn_selected_by_ufs_boot_lun()` returns false under the flag, so xbl/xbl_config/multiimgoem/multiimgqti follow the normal A/B attribute flow in both `update_slot_attribute()` and `set_active_boot_slot()`.
- `hardware/qcom-caf/bootctrl/gpt-utils/gpt-utils.cpp`: `gpt_utils_set_xbl_boot_partition()` is a no-op under the flag; `bBootLunEn` is never touched.
- `.../1.1/libboot_control_qti/Android.bp` and `.../gpt-utils/Android.bp`: `-DXBL_SLOT_BY_GPT_ATTRIBUTES` via `select()`, with the **`default:` arm preserving upstream behaviour** so an unset variable cannot silently enable the quirk.
- `device/motorola/sm6150-common/common.mk`: `$(call soong_config_set_bool,QTI_GPT_UTILS,XBL_SLOT_BY_GPT_ATTRIBUTES,true)`.

Uncommitted as of this entry. The bootctrl fork pin in `manifests/odessa.xml` must be updated after the commit is pushed.

### Result on hardware

- The bootloader now **accepts and boots the activated slot**, with `OS Fingerprint` populated. The red "No valid operating system could be found" screen is gone.
- A failed boot now degrades **gracefully**: ABL retries, marks `boot_b` `0x80 unbootable`, and falls back to slot A. No degraded bootloader, no `gpt.bin` reflash, no Rescue. The near-brick failure mode is eliminated.
- Every prior "root cause" is now explained as a symptom of this one: the original `0x80`-on-xbl_b bug, the later "leave them untouched" fix that also failed, why `fastboot set_active` always worked (MBM does it correctly), and why firmware sync, AVB flags, and the boot LUN were all irrelevant.

### Boot-LUN question closed

`running-boot-lun` reports the UFS LUN index: 2 = `sdc` = `xbl_a`, 3 = `sdd` = `xbl_b`. Healthy stock on slot A reads 2. A build that switched the boot LUN to 3 still produced the degraded bootloader even with `xbl_b` byte-identical to `xbl_a`, so the LUN switch was disproven as the cause; the no-op is kept because MBM never touches it either.

### Recovery shortcut discovered

From the degraded state, `fastboot flash bootloader bootloader.img` (unsuffixed, from the official RPAS31 package) restores `running-boot-lun` and the partition view. A full Software Fix Rescue is not required. In the degraded state only **unsuffixed** partition names are accepted, because ABL reports `has-slot:boot: no`.

## 2026-07-25 NEXT PROBLEM: LineageOS bootloops after the bootloader accepts it

- Observed sequence: black screen, Motorola logo, bootloader-unlocked warning, Motorola logo held for **10-15 seconds**, then reset. No LineageOS boot animation.
- The second logo is the continuous-splash framebuffer inherited from ABL, so the kernel is running for those 10-15 seconds and dies before `bootanimation`. This is the first time in the project that Android boot has progressed past the bootloader.
- `CONFIG_PANIC_TIMEOUT=5` matches the timing: a panic a few seconds in, plus a 5-second delay before reset. `CONFIG_PANIC_ON_SSR_NOTIF_TIMEOUT=y` is also set and is a plausible trigger for a fresh port.
- Kernel has `CONFIG_PSTORE=y`, `PSTORE_RAM`, `PSTORE_CONSOLE`, `PSTORE_PMSG`. The `sdmmagpie-moto-common-overlay.dtsi` reserves `ramoops_mem` with `console-size`, plus `mmi_annotate_mem`, `wdog_cpuctx_mem`, and `tzlog_dump_mem`. A `kpan` partition exists at `sdb11`.
- **`/sys/fs/pstore/` was empty after the first bootloop.** The cause was a 15-second Power-key force-off, which cold-resets DRAM and clears the ramoops region. `kpan` was also empty.
- **Durable rule: never force the phone off with the Power key when a kernel log is wanted.** Catch the reset by holding **Volume Down** so it lands in the bootloader on a warm path, then select Recovery and read `/sys/fs/pstore/`.
- The boot ramdisk's `fstab.qcom` was reviewed on the host and looks correct: logical `system`/`vendor`/`product` with `slotselect`+`first_stage_mount`, `metadata` and `userdata` entries, firmware mounts for `modem`/`dsp`/`bluetooth`/`fsg`, and the `misc` entry update_engine requires.

## 2026-07-25 bootloop diagnosis: dies at the zygote handoff, no kernel panic

First successful capture of a failed Android boot on this device. Artifact: ignored `lineageos/.downloads/pmsg-bootloop-20260725.bin` (120,589 bytes, from `/sys/fs/pstore/pmsg-ramoops-0`). Contains device identifiers; never commit or share unredacted. Host parser: scratchpad `pmsg.py` (pstore pmsg format: `pmsg_log_header_t` magic `0x6c`, then `android_log_header_t`, then priority/tag/msg).

### How the capture was finally obtained

- Warm path only: let the boot actually fail, catch the reset with **Volume Down** into the bootloader, then select Recovery. **Any power-off clears the ramoops DRAM region** - two captures were lost that way, one to a deliberate 15-second Power hold and one to an accidental power-off.
- Going bootloader -> Recovery *without* letting a boot fail leaves pstore empty; the boot must actually run.
- `dmesg-ramoops-0` was **absent** (no kernel panic) and `console-ramoops-0` was **absent** too, so init's own log was not recoverable. Only pmsg survived, with roughly 28% single-bit corruption (`ramoops ... ecc: 0/0`, no ECC configured). Treat ramoops as unreliable across a reset on this device.

### What the log proves

- The boot reaches the **end of `post-fs-data`**, far deeper than expected: `apexd` ran, `vold` generated the "key storage" and standard storage keys, `fscrypt_prepare_user_storage` succeeded, `vold_prepare_subdirs` set up `/data/misc_ce/apexdata/...` and `/data/misc/profiles/cur/0`, `keystore2` reached `maintenance.rs:287 - await a change to 'apexd.status'`, and `odsign`/`odrefresh` completed with "Boot images on /system OK" and "on-device signing done". **FBE and metadata encryption work.**
- **Zero log lines from `zygote`, `system_server`, `servicemanager`, `bootanim`, `installd`, `statsd`.** The 120 KB buffer never wrapped in its 256 KB zone, so this is the complete userspace log - those processes genuinely never logged.
- `zygote` is armed as critical: `init.zygote64.rc` has `critical window=${zygote.critical_window.minute:-off} target=zygote-fatal`, and **`zygote.critical_window.minute=10` is set** in the build. Four fast failures triggers the reboot, which matches the observed ~37 second cycle (4 x ~8 s).
- Leading hypothesis: **zygote fails at the dynamic-linker/exec stage**, which prints to stderr -> kmsg, the one buffer that did not survive. That explains a critical service failing repeatedly while writing nothing to pmsg.
- Tail of the log is `QC-time-services` (`time_daemon`) looping `ats_0`..`ats_15` with `genoff_post_init:Error in accessing storage` and `Unable to open file`, reading `/mnt/vendor/persist/time/ats_N`. Real defect, but not obviously the reboot cause.
- `libperfmgr` emits repeated `Failed to read Node[N]'s <HoldFd|AllowFailure|WriteOnly|Paths|DefaultIndex|...>` - the Power HAL's `powerhint.json` is not parsing. Real defect, follow up after boot.
- `adbd` **never enumerated on USB** during the 37-second attempt (verified by a host-side `adb`/`fastboot` state watcher). This blocks live debugging and is itself a bug to fix.

### Checked and eliminated (all free, host-side)

- `init.zygote64_32.rc` looks like it only defines `zygote_secondary`, but it **imports `init.zygote64.rc`** which defines the primary critical `zygote`. Not a defect.
- `ro.zygote=zygote64_32` and all three `init.zygote*.rc` files are installed. Not a defect.
- `system/lib/libart.so` missing is **normal** - libart ships in the ART APEX.
- All 13 direct `NEEDED` libraries of `app_process64` resolve, including `libnativeloader.so` and `libsigchain.so` from `apex/com.android.art/lib64`.
- The boot ramdisk `fstab.qcom` is correct.

### Recommended next step

Make the failure live-debuggable instead of fighting ramoops: rebuild with `zygote.critical_window.minute` unset/`off` so a zygote failure no longer reboots the device, plus whatever is needed to bring `adbd` up early, then install once and read `logcat`/`dmesg` directly. Optionally add `ecc-size` to the `ramoops_mem` node in `sdmmagpie-moto-common-overlay.dtsi`, though ~28% corruption likely exceeds what Reed-Solomon can correct.

## 2026-07-25 XBL GPT-attribute fix committed

- The hardware-verified fix is no longer loose in a working tree. Committed on the local `lineage-23.2` branches:
  - `hardware/qcom-caf/bootctrl`: `6024c10` (`bootctrl: Select the XBL chain by GPT attributes on odessa`), on top of `6863795`. The repository had been left on a detached HEAD; the branch was checked out before committing.
  - `device/motorola/sm6150-common`: `f64cb3e5` (`sm6150-common: Select the XBL chain by GPT attributes`), on top of `aed760a0`.
- Neither commit is pushed. The bootctrl fork remote is `fork` = `https://github.com/ARLBR10/android_hardware_qcom_bootctrl.git`. `manifests/odessa.xml` still pins `6863795`, which does **not** contain the fix; update the pin only after the commit is pushed to a remote the manifest can fetch.

## 2026-07-25 root cause of "adbd never enumerated": ro.adb.secure gates persist.sys.usb.config

Proven from build-system source on the host, not theorised. This is why no USB device of any kind appeared during the 37-second bootloop window.

- `vendor/lineage/config/common.mk` sets, for every variant except `eng` and except when `WITH_ADB_INSECURE` is defined: `ro.adb.secure=1` **and** `PRODUCT_NOT_DEBUGGABLE_IN_USERDEBUG := true`.
- `build/soong/scripts/gen_build_prop.py` turns `ProductNotDebuggableInUserdebug` into `enable_target_debugging = False`, so the current build ships **`ro.debuggable=0` even though `ro.build.type=userdebug`**. Confirmed in the built `out/target/product/odessa/system/build.prop`.
- `build/make/tools/post_process_props.py:mangle_build_prop()` auto-adds `persist.sys.usb.config=adb` **only when `ro.adb.secure == "0"`**. With Lineage's default it is never added, and it is set nowhere else in the build.
- `system/core/rootdir/init.usb.rc:109` is `on boot && property:persist.sys.usb.config=*` -> `setprop sys.usb.config ${persist.sys.usb.config}`. With the property unset, that trigger never fires, `sys.usb.config` is never set, no configfs gadget is ever composed, and `adbd` is never started. Normally the user enables USB debugging in Settings, which sets `persist.sys.usb.config` from `UsbDeviceManager` - impossible on a device that never finishes booting.
- The rest of the USB path is already correct and needs no change: `sys.usb.configfs=1` is set by `init.mmi.chipset.rc` and `init.target.rc`; `init.mmi.usb.rc` mounts functionfs `adb` and drives `sys.usb.controller` from `vendor.usb.controller`; AOSP `init.usb.configfs.rc:17,20` handles a plain `adb` composition. Recovery ADB already works on this kernel, so the UDC and DWC3 stack are fine.
- Fix for bring-up: build with `WITH_ADB_INSECURE=true`. Verified by product config on 2026-07-25 that it yields `ro.adb.secure=0` and leaves `PRODUCT_NOT_DEBUGGABLE_IN_USERDEBUG` empty (hence `ro.debuggable=1`, hence `persist.sys.usb.config=adb`). `ro.adb.secure=0` is required, not merely convenient: with authentication on there is no UI to accept the host key.
- `zygote.critical_window.minute=10` was commented out in `device/motorola/sm6150-common/properties.mk` so a repeatedly failing zygote no longer reboots the device. **Both of these are temporary bring-up settings and must be reverted before any release build.**
- Note on the earlier pmsg capture: liblog's `PmsgWrite` gates on the **compile-time** `ANDROID_DEBUGGABLE` macro, not runtime `ro.debuggable`. A userdebug build therefore writes all log ids to pmsg regardless of `ro.debuggable=0`, so "zygote/system_server/servicemanager never logged" remains a valid conclusion.
- `ro.dalvik.vm.enable_uffd_gc=false` was checked in the built `product/etc/build.prop` and is correct for Linux 4.14. It is not a zygote suspect.

## 2026-07-25 bootctrl fork published and manifest pinned

- `hardware/qcom-caf/bootctrl` commit `6024c10` was pushed to `https://github.com/ARLBR10/android_hardware_qcom_bootctrl.git` branch `lineage-23.2`. Full SHA `6024c108fc43286e09b4d63b7c620ed8ef0a5903`.
- `manifests/odessa.xml` now pins that revision, replacing `6863795de5ec856c98244b1e5c3a4cd1f1b9be1c`. Its stale comment, which described the disproven "upstream marks xbl unbootable" theory and pointed at `docs/xbl-unbootable-root-cause-20260724.md`, was rewritten to the proven GPT-attribute cause. `lineageos/.repo/local_manifests/odessa.xml` is a symlink to the tracked file, so it needs no separate update.
- `device/motorola/sm6150-common` `f64cb3e5` is committed locally but its remote is `origin`; it has not been published.

## 2026-07-25 ADB-debuggable bring-up build verified on the host

- Built from the fixed trees with `WITH_ADB_INSECURE=true`. Target-files: `out/target/product/odessa/obj/PACKAGING/target_files_intermediates/lineage_odessa-target_files.zip`, 2,614,932,420 bytes.
- Confirmed in the built property files: `ro.debuggable=1` (`system/build.prop`), `ro.adb.secure=0` and `persist.sys.usb.config=adb` (`system/system_ext/etc/build.prop`), and `zygote.critical_window.minute` absent everywhere.
- **Both shipping boot-control binaries now contain the fix**, unlike the GPTFIX zip. Test: the disabled `gpt_utils_set_xbl_boot_partition()` body is the only source of the literals `scsi_generic`, `lun as boot lun` and `Failed to locate secondary xbl`; a control grep for `block dev lseek64`/`by-name/xbl_a` proves gpt-utils is statically linked in and its strings are visible.
  - `recovery/root/system/bin/hw/android.hardware.boot-service.qti.recovery`, SHA-256 `af60d7bf86515846b2bc7ad13b2929aa5148b0c75e5eedaa7ba2a6c090bcc02a`: control 1, boot-LUN 0.
  - `vendor/bin/hw/android.hardware.boot-service.qti`, SHA-256 `7e6dd52b6cc031e173f5d1c7dbf89287a2304d873a453c60535a2148bcc2fbae`: control 1, boot-LUN 0.
- Use this string test rather than hashing `vendor/lib*/libgptutils.qti.so`, which is stale and unused because the library is linked statically.

## 2026-07-25 device state before the ADB-debug install

READ ONLY bootloader queries, no writes:

- `product: odessa`, `securestate: flashing_unlocked`, `is-userspace: no`, `battery-voltage: 4455`.
- **`slot-count: 2`, `has-slot:boot: yes`** - the bootloader enumerates partitions normally. This is direct confirmation that the XBL GPT-attribute fix eliminated the degraded `slot-count: 1` state; no `gpt.bin` reflash is needed any more.
- `current-slot: b`; `slot-successful:a/b: no`; `slot-unbootable:a/b: no`.
- `running-boot-lun: 3` (the B-side XBL LUN) **with a healthy bootloader**. This independently confirms the boot LUN is irrelevant on this device: an earlier session blamed LUN 3 for the degraded view, but that was confounded by the split GPT attributes. Do not reopen the boot-LUN theory.
- Slot layout: A = stock Android 11 `RPAS31.Q2-59-17-4-3-9`, B = the bootlooping LineageOS.
- Decision (user, 2026-07-25): sideload from slot B's recovery so the payload installs to **slot A**, accepting the loss of the stock fallback. The recovery path is bootloader fastboot plus the official RPAS31 package, which has already been used successfully.

## 2026-07-25 slot-A install: boots die before userspace

The ADB-debug build was installed to slot A by sideload from slot B's recovery. `Install completed with status 0`, and **the partition table survived a full install plus slot switch** - `slot-count: 2`, `has-slot:boot: yes` throughout. The XBL GPT-attribute fix is holding under the exact operation that used to near-brick the device.

### What the failure looks like

- Slot A failed 7 times, ABL set `slot-unbootable:a: yes` / `slot-retry-count:a: 0` and fell back to slot B (`slot-retry-count:b: 7`).
- With `tools/watch-usb.sh` running: **53 seconds from reboot to catching it in the bootloader, with no USB device of any kind** - no adb, no raw gadget. About three cycles, so roughly 18 s each, against ~37 s for slot B's build. It never reaches `on boot`, where the USB gadget is composed.
- After those failed boots `/sys/fs/pstore/` was **completely empty**. pstore presents the previous boot's data and then zeroes the zone, so an empty pstore means the last boot wrote nothing at all: no Android log, no panic record.
- The earlier `pmsg-ramoops-0` capture (262,000 bytes, the full zone) contained only `update_engine_sideload` content - `vold` 0, `zygote` 0, `odsign` 0, `keystore` 0 exact matches. Seven boots reaching `post-fs-data` like slot B's build would have flushed that out. They did not.

### Eliminated

- **Slot A's kernel, dtbo and AVB chain are fine**: `fastboot reboot recovery` on slot A boots Lineage Recovery with working ADB, reporting `ro.boot.slot_suffix=_a` and `23.2-20260725-UNOFFICIAL-odessa`.
- **The ramoops region is properly reserved**: `ramoops: attached 0xbf800@0xaf000000, ecc: 0/0`. `CONFIG_PSTORE_CONSOLE=y` is set in the built kernel config. `console-ramoops-0` has nevertheless never appeared in any capture on this device; treat the console zone as not surviving reset here. `pstore: allocate compression buffer error!` only disables compression of panic records and falls back to uncompressed.
- **Virtual A/B is not enabled** (`misc_info.txt` has `ab_update=true` and `use_dynamic_partitions=true` but no `virtual_ab=true`), so snapshot merge is not involved.
- **The changed properties cannot be the cause of a pre-userspace failure.** `ro.debuggable=1`, `ro.adb.secure=0` and `persist.sys.usb.config=adb` live in `/system/build.prop` and `/system/system_ext/etc/build.prop`, which are read only after first-stage mount succeeds.

### Leading hypothesis

Slot A is a different firmware environment. `docs/firmware-slot-comparison-20260719.md` recorded **16 of 19 low-level firmware partitions differing between slots**, including `tz`, `hyp`, `keymaster`, `cmnlib`, `cmnlib64`, `devcfg`, `aop`, `abl`, `xbl`, `xbl_config`, `modem`, `bluetooth`, `qupfw`, `storsec` and `uefisecapp`. None are carried by the OTA payload. Slot A boots stock Android 11 fine, so its firmware is internally consistent - but it is not the firmware the LineageOS vendor image was validated against on slot B.

The decisive experiment is to install the same OTA to slot B and compare: same build, different firmware. Do not conclude anything about the properties change until that runs.

### Tooling

- `tools/watch-usb.sh` (new, HOST ONLY) prints one timestamped line per change in `lsusb` / `adb devices` / `fastboot devices`. It catches raw USB enumeration that never reaches `adbd`, which `adb devices` alone cannot, and logs no serial numbers.
- Recovery ships `fastbootd`, `update_engine_sideload`, `sha256sum` and `dmesg`, but **no `lpdump`, `dmctl` or `lptools`**. Inspect logical partitions through fastbootd's `is-logical:` / `partition-size:` variables instead.
- `/proc/cmdline` on this device contains the serial, Wi-Fi MAC and Bluetooth MAC. Always redact before sharing or recording.

## 2026-07-25 slot-B control run: the slot/firmware hypothesis is dead

The same ADB-debug OTA was installed to slot B from slot A's recovery (`Install completed with status 0`) and behaves **identically to slot A**: `tools/watch-usb.sh` recorded 55 seconds with no USB device of any kind, and the user counted about **7 logo cycles, so roughly 8 s per boot attempt**. The bootloader was entered by hand with Volume Down; the phone does not reach it on its own.

Same build, two very different firmware environments, identical failure. `docs/firmware-slot-comparison-20260719.md`'s 16-of-19 firmware differences are therefore **not** the cause. Do not reopen that.

### `super` is healthy - not a dynamic-partition problem

Read from **fastbootd** (`adb reboot fastboot` from recovery; recovery ships `fastbootd` but no `lpdump`):

- `is-userspace: yes`, `is-logical:system_a: yes`, `is-logical:system_b: yes`
- `partition-size:system_a` = `system_b` = `0xAA6D5000` (2,858,536,960 B)
- `partition-size:vendor_b` = `0x1FA42000` (531,341,312 B), `partition-size:product_b` = `0x4788B000` (1,200,033,792 B)

Slot B totals ~4.59 GB against a 4,864,868,352 B group. Metadata and sizing are sane on both slots.

### The failing build is functionally identical to the one that reached zygote

Compared today's build against `lineage-23.2-20260724-GPTFIX-TRY2-UNOFFICIAL-odessa.zip`, the build that reached the zygote handoff. Extracted with `out/host/linux-x86/bin/ota_extractor -payload payload.bin -partitions boot,dtbo,vbmeta`, unpacked with `unpack_bootimg`:

- **kernel byte-identical**: `2da1095572cf5a2b580d9349fbf4080e91fd077359b10baf611ced3ceba78d62`
- **boot ramdisk identical**: `diff -r` over both extracted ramdisks reports no difference (8 files: `init`, `fstab.qcom`, `e2fsck`/`resize2fs`/`tune2fs`, three libs)
- **kernel cmdline identical**, header v2, page size 4096
- **DTBO device trees identical**: all three FDT entries match (`91b70dfc…`, `dfa2887c…`, `6d96c774…`). The whole-image hashes differ (`8d807087…c87293` vs `0c8998fc…c627b9`) **only** in 244 bytes of AVB footer past the 802,816-byte payload - the per-build random salt and the `com.android.build.dtbo.fingerprint` property. **`8d807087…` recorded as "unchanged DTBO" in earlier entries is not evidence of anything; that value simply came from reusing one file.** Do not treat a differing `dtbo.img`/`vbmeta.img` hash as a real change without comparing the payload separately from the footer.

The only functional difference between the two builds is the contents of `system`, `vendor` and `product`.

### Where that leaves the diagnosis

An ~8 s cycle is consistent with bootloader time plus `CONFIG_PANIC_TIMEOUT=5`. A first-stage mount failure would make init abort, and a dead init panics the kernel - which fits. But first-stage init is the *same binary* that worked, and `super` is healthy, so a straightforward mount failure is hard to explain. Do not commit to this until measured.

Kernel options available for the next step: `CONFIG_MAGIC_SYSRQ=y` (default enable mask `0x1`, so `echo 1 > /proc/sys/kernel/sysrq` is needed before `echo c > /proc/sysrq-trigger`), `CONFIG_PANIC_TIMEOUT=5`, `CONFIG_PSTORE_RAM=y`. The ramoops DT node sets `no-dump-oops`, so only real panics produce a dump record.

`fstab.qcom` mounts `system`/`vendor`/`product` as **ext4**, `logical`, `slotselect`, `first_stage_mount`, with `avb=vbmeta` plus GSI `avb_keys` on `system` and plain `avb` on `vendor`.

### Next experiments, in cost order

1. **Validate the pstore dump zone** with a deliberate sysrq panic from recovery, then check whether `dmesg-ramoops-0` appears. `console-ramoops-0` has never survived on this device; if the dump zone does not survive either, ramoops must be abandoned as a channel and the cmdline needs `androidboot.init_fatal_panic=true` plus another sink.
2. **Install TRY2 to the inactive slot** so the known-good-to-zygote build and the failing build live on different slots and can be compared by `fastboot set_active` alone. This separates "the build regressed" from "the device state changed", and given the boot-image equivalence above, the latter is the more likely of the two.

## 2026-07-25 the ADB-debug regression is exactly four properties

TRY2 (`lineage-23.2-20260724-GPTFIX-TRY2-UNOFFICIAL-odessa.zip`, reaches the zygote handoff) was reinstalled and **still holds the logo far longer than the ADB-debug build**, so the device state is fine and the regression is genuinely in the build.

### Method note - three false findings came from comparing the wrong artifacts

Loose `out/target/product/odessa/*.img` are stale and must never be compared against payload-extracted images. Doing so produced three wrong conclusions in one session: a "changed DTBO", "six missing audio HAL libraries", and "45 missing vendor entries including every `/rfs/msm/...` directory". All three evaporated under a like-for-like comparison. A fourth, "today's system is 1.76 GB smaller", came from stat-ing a file that was still being written by a background extraction. **Always extract both sides with `out/host/linux-x86/bin/ota_extractor -payload payload.bin -partitions ...` and confirm the extraction finished.**

### Like-for-like payload comparison

- `boot.img` byte-identical: `9edfc27c2a9472b9…`
- `dtbo.img` byte-identical: `8d80708752b4bcc2…` (the long-familiar value)
- `system`: identical block count 687033, used blocks 379473, inode count 172032, **used inodes 7170 on both**; recursive file listing gives 7161 entries on both with **zero path differences**, and zero mode/size differences apart from the two files below
- Tool: scratchpad `ext4ls.py` walks an ext4 image with `debugfs -f` one directory level per invocation, no mounting and no root

### The complete functional delta

`/system/build.prop`: `ro.debuggable` 0 -> 1; added `dalvik.vm.lockprof.threshold=500` and `persist.debug.dalvik.vm.core_platform_api_policy=just-warn`.
`/system/system_ext/etc/build.prop`: `ro.adb.secure` 1 -> 0; added `persist.sys.usb.config=adb` (auto-added by `post_process_props.py`).

Everything else is build timestamps. Nothing else in `system` changed at all.

### Leading hypothesis, not yet proven

`persist.sys.usb.config=adb` is the only one of the four that touches hardware. Without it `init.usb.rc:109` (`on boot && property:persist.sys.usb.config=*`) never fires, `sys.usb.config` is never set, and **the USB gadget is never composed in full Android** - true of every build that has ever reached zygote on this device. Composing it exercises `init.mmi.usb.rc` (two gadgets, diag FunctionFS, vendor USB HAL) on a DWC3 stack with a long failure history here.

Counter-evidence to weigh: recovery composes an adb gadget on the same kernel and works. And `on boot` runs *after* `post-fs-data`, so a failure there should still leave `vold`/`apexd` output in pmsg - which was not seen. **The pstore evidence on this device is unreliable enough that "dies before userspace" should no longer be treated as established.**

### Free test before any rebuild

Boot the already-installed debug build **with the USB cable unplugged**. Gadget pullup/VBUS only engages with a cable, so if the loop stretches back out toward the old ~37 s logo-hold behaviour, the USB gadget is confirmed as the trigger at zero cost.

If a rebuild is needed to bisect, the two variants are: (a) clear `PRODUCT_NOT_DEBUGGABLE_IN_USERDEBUG` without `WITH_ADB_INSECURE`, giving `ro.debuggable=1` + `ro.adb.secure=1` and **no** `persist.sys.usb.config`; (b) `WITH_ADB_INSECURE` as now. Variant (a) booting cleanly would confirm the USB property.

## 2026-07-25 BISECTED: `persist.sys.usb.config=adb` breaks the boot

Full detail and handoff: `docs/handoff-20260725-usb-gadget.md`.

A second bisect build was made with `WITH_ADB_INSECURE=true` **plus**
`PRODUCT_NOT_DEBUGGABLE_IN_USERDEBUG := true` re-asserted in
`device/motorola/sm6150-common/common.mk`, giving `ro.debuggable=0`,
`ro.adb.secure=0`, `persist.sys.usb.config=adb`. Verified from the OTA payload,
not from loose `out/` images. It was installed successfully and **still bootloops**.

Payload-to-payload comparison against TRY2 (the last build that reaches the zygote
handoff): `boot.img` and `dtbo.img` byte-identical (`9edfc27c…`, `8d807087…`);
`system` has 7161 entries on both with zero path, mode or size differences except
one file. That file is `/system/system_ext/etc/build.prop`, and the entire
functional delta is `ro.adb.secure` 1 -> 0 plus the auto-added
`persist.sys.usb.config=adb`.

- **`ro.debuggable` is exonerated.** It was 1 in the first failing build and 0 in
  this one; both fail.
- `ro.adb.secure=0` only waives ADB authentication at runtime, so the functional
  trigger is `persist.sys.usb.config=adb`.
- That property is the only thing that makes `init.usb.rc:109`
  (`on boot && property:persist.sys.usb.config=*`) fire, set `sys.usb.config`, and
  **compose the USB gadget in full Android** - a path that has never once run on
  this device, because LineageOS ships `ro.adb.secure=1` and
  `post_process_props.py` only adds the property when it is `0`.
- The gadget *infrastructure* is built in `on init` by `init.mmi.usb.rc` on every
  build; the only addition is binding the controller
  (`write /config/usb_gadget/g1/UDC ${sys.usb.controller}`). Recovery composes an
  adb gadget successfully on this same kernel, so the bug is specific to the
  full-Android path.

Unexplained and worth re-measuring: the bisect build's cycle was reported as ~3 s
while the earlier debug build was ~28 s, even though the bisect build is *closer*
to TRY2. TRY2 itself has still never been timed.

Consequence for the whole debugging strategy: the obvious way to get live
`logcat`/`dmesg` off a failing boot is itself what breaks the boot. Fix DWC3
controller binding under full Android first, or find an observability channel that
does not need USB.

## 2026-07-26 persistent-log diagnostic OTA

- The USB-property bisection identifies a separate regression in the ADB-debug
  build; it does not explain TRY2's original failure at the zygote handoff.
  Investigation therefore returned to the original failure without requiring
  full-Android USB, boot timing, or ramoops.
- Removed the temporary `PRODUCT_NOT_DEBUGGABLE_IN_USERDEBUG := true` bisect
  override from `device/motorola/sm6150-common/common.mk`. The build must be made
  without `WITH_ADB_INSECURE` so normal Lineage properties remain in effect.
- Added temporary bring-up defaults `persist.logd.logpersistd=logcatd` and
  `ro.logd.kernel=true`. Android's existing `logcatd` service writes all log
  buffers under `/data/misc/logd`, allowing retrieval from recovery after a cold
  reset. `zygote.critical_window.minute` remains disabled for this diagnostic.
- Correction to the USB-gadget handoff: init does not automatically send zygote
  stdout/stderr to kmsg. `SetupStdio()` sends both to `/dev/null` unless the
  service explicitly has `stdio_to_kmsg`. The dynamic linker can also log to
  logd, so persistent logcat is the first non-USB evidence channel to test.
- User-built OTA:
  `lineage-23.2-20260726-BOOTLOOP-TRY2-UNOFFICIAL-odessa.zip`, 1,028,459,341
  bytes, SHA-256
  `c7a079102ad3a8538e6dbb496bcc5825c3f4333608100d6d3b8356d100d7f71c`.
  ZIP integrity and payload-property hashes pass; extracted payload SHA-256 is
  `981b1adeeb6acd4697f29cc7fa57231296be594d7b170018c89c5f19020c0d24`.
- Exact payload extraction verifies `ro.debuggable=0`, `ro.adb.secure=1`, no
  `persist.sys.usb.config`, `persist.logd.logpersistd=logcatd`, and
  `ro.logd.kernel=true`. `/system/etc/init/logcatd.rc` is present. Extracted
  system image SHA-256 is
  `52ed111b55b771ac3ad4fd192b57783704726a4983865b7e410a0ed66e8546db`.
- This is HOST ONLY validation. The OTA has not been installed or booted, and no
  phone command was issued while validating it.

## 2026-07-26 persistent-property and log-retrieval results

- The diagnostic OTA installed from recovery A to slot B with AIDL BootControl,
  all 2,268 payload operations, filesystem verification, postinstall, and slot
  activation succeeding. Recovery reported `Install completed with status 0`.
  The post-install bootloader remained healthy with two slots and a complete
  partition view.
- Before that sideload, loose `boot_b`, `dtbo_b`, `recovery_b`, and `vbmeta_b`
  images were manually flashed; manual `system_b`, `product_b`, and `vendor_b`
  resize attempts failed before image transfer because they were issued in
  bootloader fastboot. The subsequent verified OTA replaced the complete slot-B
  image set and removed this mixed-image state. Do not manually flash dynamic
  partitions or use mutable loose output images.
- The first boot of the nominally normal-USB diagnostic still showed the rapid
  regression. A directly captured slot-B pmsg record was only 834 bytes but
  contained repeated corrupted-yet-identifiable `adbd`, authentication, and
  FunctionFS endpoint messages. Artifact:
  `.downloads/pmsg-bootloop-slotb-direct-20260726.bin`, SHA-256
  `24c870e23f07460e4a43f4c1e6b0c7187cd3babf9c0370cde622d42911340a18`.
- Root cause of that misleading retest: `persist.sys.usb.config=adb` from the
  earlier insecure build survived in metadata-encrypted userdata. Removing the
  property from a later build image does not clear an existing persisted value.
  Recovery factory reset was performed with user approval, erasing userdata and
  persisted properties.
- After the wipe, the rapid loop disappeared. Slot B returned to the original
  behavior: Motorola logo, unlock warning, a long logo hold, black screen, then
  reset. Two B retries were consumed while B remained selected and the
  bootloader/partition view stayed healthy. This separates the stale USB gadget
  regression from the original boot failure and confirms that USB is not the
  next root-cause path.
- Immediate post-wipe slot-B pstore was empty. Android's `logcatd` likely wrote
  under `/data/misc/logd`, but recovery cannot retrieve it: userdata is metadata
  encrypted, recovery starts no `vold` or `keystore2`, and creates no decrypted
  dm mapping. Raw userdata correctly fails the F2FS magic check. `/metadata`
  mounts read-only and contains the metadata-encryption key directory, but no key
  material was displayed or copied.
- Temporary uncommitted diagnostic changes now redirect existing `logcatd` from
  `/data/misc/logd` to unencrypted `/metadata/logd`. The path is labeled
  `misc_logd_file`, and init receives only the parent-directory permission needed
  to create it. The service remains gated by the temporary
  `persist.logd.logpersistd=logcatd` property. `git diff --check` passes in
  `system/logging`, `system/sepolicy`, and `device/motorola/sm6150-common`; no
  build has yet validated policy or packaging.

## 2026-07-26 metadata-log diagnostic artifact

- The user completed cached `target-files-package` and OTA generation
  successfully after the `/metadata/logd` changes.
- Target-files archive SHA-256 is
  `8bad580d500e82541605cae02b7f08b5d74e43342e74b9cddadb0619c7a0773b`;
  ZIP integrity passes.
- Installable OTA:
  `lineage-23.2-20260726-BOOTLOOP-TRY3-UNOFFICIAL-odessa.zip`, 1,028,459,846
  bytes, SHA-256
  `39fb5ec2f3cb225cdbf3892592e8c24288c2193171c2dc8d136aacb15265ee91`.
  ZIP integrity and payload-property hashes pass.
- Exact OTA payload SHA-256 is
  `ce46f2c0b5fb718aa3ab9c2b3d15b50c6449b82c1696207b10cda5e74d7958ec`.
  Exact payload-extracted system image SHA-256 is
  `c5e6c9d2211b086b6b115a9423492533b5ee035d6c108e0609668f92c4b4c7ab`.
- Payload extraction verifies the shipping system image contains the
  `/metadata/logd` mkdir, clear, and continuous `logcatd` output paths plus
  `/metadata/logd(/.*)? -> misc_logd_file` in compiled platform file contexts.
  Shipping properties are `ro.debuggable=0`, `ro.adb.secure=1`,
  `persist.logd.logpersistd=logcatd`, and `ro.logd.kernel=true`, with no
  `persist.sys.usb.config` in either checked property file.
- This validation is HOST ONLY. TRY3 has not yet been installed or booted.

## 2026-07-26 TRY3 failure and diagnostic-channel decisions

- TRY3 installed from recovery A to target slot B with all payload operations,
  filesystem verification, postinstall, and slot activation succeeding;
  recovery reported status 0. The bootloader remained healthy.
- TRY3 then reset rapidly until B exhausted all seven retries and became
  unbootable, after which slot A showed the older long-logo failure and consumed
  one retry. Recovery mounted `/metadata` read-only afterward, but
  `/metadata/logd` did not exist. The relocated logger never reached its own
  output trigger and changed boot behavior, so it is rejected as a diagnostic.
- Exact payload audit confirms TRY2 and TRY3 have byte-identical boot, DTBO, and
  product partitions. TRY3 changes system policy/init, vendor precompiled policy,
  recovery policy, and dependent vbmeta. This is a real payload difference, not
  a loose-output mismatch or AVB rejection; both vbmeta images use flags 3.
- The `/metadata/logd` init, file-context, policy, and property changes were fully
  reverted. `system/logging` and the two touched `system/sepolicy` files are back
  to their original bytes.
- Ramoops was tested directly rather than inferred: with recovery userdata and
  metadata unmounted, SysRq was enabled and a deliberate kernel panic was
  triggered. The phone warm-reset to bootloader, but immediate recovery showed
  an empty `/sys/fs/pstore`. Therefore this device's ramoops setup cannot retain
  even a known panic and must not be used as an evidence channel.
- The saved known-working Pixys recovery was inspected host-only. Like Lineage
  Recovery, it contains no `vold`, `vdc`, or `keystore2`; it cannot unlock the
  metadata-encrypted userdata. A correct recovery decrypt implementation would
  require normal Android's vold/keystore2/Qualcomm Keymaster stack, Binder/init
  ordering, libraries, linker namespaces, and recovery SELinux. Do not invent a
  recovery-only dm-default-key path as a shortcut.

## 2026-07-26 TRY4 bounded zygote-log design

- Temporary uncommitted TRY4 keeps stock `logcatd` writing to
  `/data/misc/logd`, which is the exact logger arrangement under which post-wipe
  TRY2 retained the original long failure behavior.
- `persist.logd.logpersistd=logcatd` and `ro.logd.kernel=true` are enabled; normal
  secure USB properties remain, with no `persist.sys.usb.config` default.
- The existing primary zygote service has one new `onrestart copy` action:
  `/data/misc/logd/logcat` to the exact unencrypted path
  `/metadata/vold/bootloop-logcat`. It does not list, read, or copy metadata key
  material. Recovery will later mount metadata read-only and pull only that exact
  file.
- Existing SELinux types are reused. Init gains read permission for
  `misc_logd_file` and create/write permission for `vold_metadata_file`; there is
  no new type, domain, service, executable, USB path, or recovery component.
  Zygote's critical reboot remains disabled. `git diff --check` passes in the
  device, `system/core`, and `system/sepolicy` repositories. No TRY4 build has
  run yet.

## 2026-07-26 TRY4 installed; retrieve metadata log next

Full continuation guide: `docs/handoff-20260726-bootloop-observability.md`.

- Exact installable TRY4 OTA is 1,028,459,562 bytes, SHA-256
  `b8ba2eda848e8bb6ac108f3ea372307564f50427415849126da602f343daa704`.
  Direct payload extraction verifies the zygote `onrestart copy` action and
  compiled init SELinux permissions. Extracted system image SHA-256 is
  `8d0305bd177c0ce2336a912217a2bb636d3fa92b57deb5681673046d6ee4d7b6`.
- Provenance caveat: the mutable target-files ZIP remained stale at TRY3's hash
  and timestamp while the exact TRY4 OTA payload contained the intended bytes.
  Preserve and reason from the validated OTA; regenerate target-files before any
  reproducibility claim.
- TRY4 installed from recovery B to target A with status 0. Recovery log
  `recovery-slotb-try4-20260726.log`, SHA-256
  `94ea4e77e7419d36d677275bca3fe1c299cdf6aa90a122d2885a5db9f6c87a84`,
  records AIDL BootControl and successful download, filesystem verification,
  postinstall, and activation.
- TRY4 failed all seven slot-A retries and A became unbootable. Automatic
  fallback B then consumed two retries. Current verified bootloader state:
  current B, A unbootable with zero retries, B bootable with five retries,
  `slot-count: 2`, `has-slot:boot: yes`, `securestate: flashing_unlocked`, battery
  4.461 V. Partition enumeration remains healthy.
- Immediate next action: from the current bootloader, boot recovery B, enable
  ADB, mount `/metadata` read-only, and retrieve only
  `/metadata/vold/bootloop-logcat`. Do not boot Android, re-arm A, build, wipe, or
  flash first. The file may contain identifiers and must remain ignored and
  unredacted only locally.

## 2026-07-26 TRY4 log absent; TRY5 stage markers pending

- The phone was still in Motorola bootloader fastboot. It was rebooted directly
  to recovery without changing slots or partitions. Recovery ADB confirmed slot
  `_b`.
- `/metadata` was mounted read-only and only the exact diagnostic path
  `/metadata/vold/bootloop-logcat` was queried. The file did not exist. Metadata
  was immediately unmounted; no Android boot, wipe, flash, slot change, or other
  device write followed. The phone remains in slot-B Lineage Recovery.
- The absent file does not distinguish a pre-zygote failure from zygote not
  restarting or `/data/misc/logd/logcat` being unavailable. TRY4's copy action
  runs only from the primary zygote service's `onrestart` path.
- Temporary TRY5 source adds two init built-in markers without moving logcatd or
  adding a service/executable/domain: `/metadata/vold/bootloop-zygote-start` is
  written at the start of the existing `zygote-start` action, and
  `/metadata/vold/bootloop-zygote-restarted` is written before TRY4's existing
  log copy when primary zygote restarts. Existing narrowly scoped init policy
  for `vold_metadata_file` and `misc_logd_file` covers the markers and copy.
- Interpretation after one controlled TRY5 boot: no start marker means init did
  not reach `zygote-start` (or the vold metadata directory was unavailable);
  start marker without restart marker means zygote did not restart; both markers
  without the copied log means the logcatd source was unavailable/unreadable;
  all three files provide the required zygote failure log. Check only these exact
  paths from read-only metadata and do not list `/metadata/vold`.
- `git diff --check` passes in `system/core`, `system/sepolicy`, and the SM6150
  common device tree. A fresh target-files archive and exact TRY5 OTA still need
  to be built and payload-verified before any sideload.
- The user completed the fresh TRY5 target-files build. Archive:
  `lineageos/out/target/product/odessa/obj/PACKAGING/target_files_intermediates/lineage_odessa-target_files.zip`,
  2,614,933,712 bytes, SHA-256
  `d9648eb39e66587033cae25af3845cbaa0222c1d8ba62e6cb86f3157f65a9c89`;
  ZIP integrity passes.
- Direct archive inspection confirms the `zygote-start` marker, zygote-restart
  marker, and TRY4 log copy are all present. Compiled platform policy grants init
  the required `misc_logd_file` read and `vold_metadata_file` create/write
  permissions. Properties remain `ro.debuggable=0`, `ro.adb.secure=1`,
  `persist.logd.logpersistd=logcatd`, and `ro.logd.kernel=true`; there is no
  `persist.sys.usb.config` or zygote critical-window property. Generate and verify
  an OTA only from this exact target-files archive.
- Exact TRY5 installable OTA:
  `lineageos/out/target/product/odessa/lineage-23.2-20260726-BOOTLOOP-TRY5-UNOFFICIAL-odessa.zip`,
  1,028,459,980 bytes, SHA-256
  `9eee5669f7fc416678ec19da8b8ff1759e42b7bceab9589ebb25a8cb6df15a3b`.
  ZIP integrity passes and required A/B OTA entries are present. Payload size is
  1,028,452,686 bytes, SHA-256
  `1912a1d2728c7829577a0503717317398ab72779f9ffb994d1412f7af5f8c4a6`;
  its base64 hash exactly matches `payload_properties.txt`.
- Direct extraction of `system` from that exact payload produced SHA-256
  `cec2dfe22dec802dcaedc7e042f6e5363148846888efc91ecd558e6dafbef1ed`.
  Filesystem inspection reconfirms both stage markers, the restart log copy,
  `ro.debuggable=0`, `ro.adb.secure=1`, persistent logcat enabled, and no USB
  persist or zygote critical-window property. This supersedes TRY4's stale
  target-files provenance caveat for TRY5.
- Live read-only preflight finds Lineage Recovery ADB on `odessa`, slot `_b`, at
  98% battery. No install, wipe, reboot, slot change, or partition write has yet
  been performed with TRY5.
- After explicit user authorization, TRY5 was sideloaded from recovery B to
  target slot A. The host-side `adb sideload` display remained around 47% and
  hit its ten-minute command timeout while recovery continued processing; it
  must not be retried. The recovery UI subsequently reported completion.
- Captured ignored recovery log:
  `lineageos/.downloads/recovery-slotb-try5-20260726.log`, SHA-256
  `53893d10a13881e43df17e561b306a9fe580549105996d64e1671d2d89a93534`.
  It may contain identifiers and must not be committed or quoted unredacted.
  The log proves source B, target A, `DownloadAction`,
  `FilesystemVerifierAction`, and `PostinstallRunnerAction` all `kSuccess`,
  `Update successfully applied`, and `Install completed with status 0`.
- TRY5 has not yet been booted. On its first boot, catch the first reset with
  Volume Down and retrieve only the three exact metadata paths before any
  further Android boot.
- TRY5 was booted after the status-0 install. It reset rapidly twice before the
  user caught Motorola fastboot. Read-only metadata then showed current slot A
  with five retries remaining; the bootloader still had a healthy two-slot
  partition view. Recovery subsequently booted from slot B without re-arming or
  changing either slot.
- Recovery mounted metadata read-only. All three exact TRY5 paths were absent:
  `bootloop-zygote-start`, `bootloop-zygote-restarted`, and `bootloop-logcat`.
  `/metadata/vold` itself exists, so the destination parent is not the missing
  prerequisite. Metadata was unmounted immediately.
- This disproves the current zygote/linker-restart hypothesis for TRY5: init did
  not reach the start of the `zygote-start` action. The next diagnostic must use
  one bounded stage file updated at checkpoints from post-fs through
  post-fs-data and BPF loading; do not add another zygote-only logger or return
  to USB/pstore.

## 2026-07-26 TRY6 pre-zygote stage diagnostic

- Temporary `system/core/rootdir/init.rc` instrumentation overwrites the single
  exact path `/metadata/vold/bootloop-stage` at 13 checkpoints: post-fs,
  post-fs-data start, data-key installed, persist properties loaded, APEX and
  KeyMint ready, user 0 initialized, classpath derived, odsign key done,
  post-fs-data complete, BPF loader start/complete, BPF programs loaded, and
  zygote start. It adds no service, executable, shell, USB path, logging
  relocation, or policy broadening.
- Fresh target-files archive: 2,614,933,941 bytes, SHA-256
  `73ef0bf5366ab9ffc34ab17186eef2de3be363830b8ee1e591b484463603d953`;
  ZIP integrity passes. Direct archive inspection confirms all stage writes,
  the existing zygote restart/log copy, and compiled init permissions.
- Exact installable TRY6 OTA:
  `lineageos/out/target/product/odessa/lineage-23.2-20260726-BOOTLOOP-TRY6-UNOFFICIAL-odessa.zip`,
  1,028,459,956 bytes, SHA-256
  `9ee1e663d3e976fc6dde4d88ec4f99f29ce293ae07ed2114f1590f44794f0572`.
  ZIP integrity and required A/B entries pass. Payload size is 1,028,452,662
  bytes, SHA-256
  `b5701d80032c293e074694edcb0efa952c6c5578bd8b10b91ffd6517cf70f368`;
  its hash matches `payload_properties.txt`.
- Direct payload extraction produced raw system image SHA-256
  `a23efd753674599970606091efc434c9eac0e0d30176156811f3b36f35281fb3`.
  Converting target-files' sparse `IMAGES/system.img` to raw yields the same hash
  and a byte-for-byte `cmp` match. Exact payload filesystem inspection confirms
  all 13 stages, secure USB properties, persistent logcat, and no zygote critical
  window. TRY6 is approved for a controlled diagnostic sideload only after a new
  explicit destructive authorization.
- After explicit authorization, TRY6 installed from recovery B to target A.
  Ignored recovery log `lineageos/.downloads/recovery-slotb-try6-20260726.log`,
  SHA-256 `6554a410f6adec417c57d138333b8941e4177bcdd2a7ac3ac2b9d581c9932111`,
  proves all three update actions succeeded, the update was applied, and final
  status was 0. It may contain identifiers and must remain untracked/unquoted.
- TRY6 exhausted slot A's retries and automatically fell back to B; B retained
  seven retries. Recovery B mounted metadata read-only, but
  `/metadata/vold/bootloop-stage` was absent. Metadata was unmounted.
- Absence does not yet prove a pre-`post-fs` reset because init's regular-file
  `write` builtin closes without `fsync`, and every attempt reset rapidly. TRY7
  therefore adds a temporary `write_sync` init builtin that writes the marker,
  fsyncs the file, and fsyncs its parent directory. Only the diagnostic markers
  use it. The earliest marker now runs from device `on fs` immediately after the
  early `mount_all`; another runs at the first line of platform `on post-fs`.
  Existing later checkpoints use the same durable builtin. No production
  behaviour should be inferred until this durability-correct diagnostic runs.
- TRY7 static `git diff --check` passes in system core, platform policy, and the
  common device tree. The new init builtin and rc syntax still require a focused
  compile/host-init-verifier gate before target-files packaging.
- The first focused TRY7 compile failed only because this branch disables
  implicit `unique_fd` to integer conversion; both `fsync` calls now use the
  explicit `.get()` accessor. `m -j8 init host_init_verifier` subsequently
  completed successfully. The full target-files/boot/vendor/system/AVB package
  still requires regeneration and exact inspection before any TRY7 OTA.
- Fresh TRY7 target-files archive: 2,614,937,112 bytes, SHA-256
  `a7c0375db022f036f70d2faa69f51b20bcfa11bad8c73da15d54454c999e2544`;
  ZIP integrity passes. The packaged normal second-stage and recovery init
  binaries contain `write_sync`; the deliberately minimal first-stage ramdisk
  init does not parse these system/vendor rc actions and need not contain it.
  Packaged system and vendor rc contain the early and later durable stage calls.
- The first TRY7 OTA generation failed only during final ZIP metadata insertion
  because `/tmp` was full. No output ZIP was produced. Removing the agent-created
  TRY5/TRY6 verification directories freed about 10.3 GiB; source and
  target-files were unchanged. Regeneration from the same target-files archive
  then succeeded.
- Exact TRY7 OTA:
  `lineageos/out/target/product/odessa/lineage-23.2-20260726-BOOTLOOP-TRY7-UNOFFICIAL-odessa.zip`,
  1,028,460,874 bytes, SHA-256
  `c0dc7772f01d2b59d83139617433d97c47e318f797e54208ae83d3e3e5d09596`;
  ZIP integrity and required A/B entries pass. Payload size is 1,028,453,580
  bytes, SHA-256
  `130f74d3ca797802d33a548ecfa1cde1d8ee2268b75b1da3cb82bd23f43e201a`,
  matching `payload_properties.txt`.
- Exact payload images: boot
  `9edfc27c2a9472b9b25dbbf9c49ecfc05ee0de688697b2485b31e71110fd498b`,
  raw system
  `0b54c93ca29872d6efb47c0b6348261d0b98b4e463fd2c46bd1122e1d85fa32e`,
  vendor
  `54cfa31c9fb5dea59fdeb9e23c4390c99948ca1d84b8b3995130d89a647e910d`.
  Each is byte-identical to the corresponding target-files image after sparse
  system conversion. Direct filesystem/ramdisk inspection proves the exact
  payload has the `write_sync` implementation and every intended rc call. TRY7
  is approved for a controlled diagnostic sideload after explicit authorization.
- After explicit authorization, TRY7 installed from recovery B to target A with
  status 0. Ignored recovery log
  `lineageos/.downloads/recovery-slotb-try7-20260726.log`, SHA-256
  `833ceb62c0759b35647e2b5f51178ec6aa010b55cb2a3d5d640a5690c615432e`,
  proves all OTA actions succeeded. It may contain identifiers and must remain
  untracked/unquoted.
- TRY7 reset twice; slot A remained selected, bootable, and had five retries.
  Recovery B then mounted metadata read-only, but even the durable stage file
  was absent. Metadata was immediately unmounted.
- Bootstrap review confirms first-stage ramdisk init intentionally does not
  contain the new builtin. After first-stage mounts it explicitly execs
  `/system/bin/init` for SELinux setup, which then execs the same system binary
  for second stage. The exact payload's system init contains `write_sync`, so it
  was not an unknown-command failure. Absence localizes the gap before rc action
  execution, but not yet between first-stage mounts, SELinux setup, second-stage
  entry, and boot-script parsing.
- Temporary TRY8 code adds direct fsynced markers independent of rc parsing at
  exactly those four transitions: `first-stage-mounts-complete`,
  `selinux-setup-complete`, `second-stage-main`, and `boot-scripts-loaded`.
  `WriteFileSync` is shared by the diagnostic builtin and direct markers and
  fsyncs both the file and parent directory. Marker failures log and return; they
  are not fatal. Static `git diff --check` passes; focused init/first-stage/host
  compilation is still required before packaging.
- Focused `m -j8 init init_first_stage host_init_verifier` passed. Direct string
  inspection of the focused binaries found the first-stage mount marker in
  ramdisk init and the SELinux/second-stage/script markers plus `write_sync` in
  system init.
- Fresh TRY8 target-files archive: 2,614,937,918 bytes, SHA-256
  `4363aa046e000f7d07d865d2a173a198498314977e3901218d130840269fc513`;
  ZIP integrity passes. Packaged binary and rc inspection confirms all direct
  and action-based markers.
- Exact TRY8 OTA:
  `lineageos/out/target/product/odessa/lineage-23.2-20260726-BOOTLOOP-TRY8-UNOFFICIAL-odessa.zip`,
  1,028,478,895 bytes, SHA-256
  `2bc9ffae66dedc07108da7307081ef6e394b273bd997d4378ec04cd7bb15a7ee`;
  ZIP integrity passes. Payload size is 1,028,471,601 bytes, SHA-256
  `7f0b0c6158400759eed62b3fb02f8cfe2e9f58c7a308d2acf7d9ea21b289d3ef`,
  matching `payload_properties.txt`.
- Exact payload boot image SHA-256 is
  `6236a4a1413a818f51d803b1451599733ced901933c55c14dd47aaa6b03fc5e8`;
  raw system is
  `199a353930a8827de080effd61150c21b952f5c487865e6cd88c07e37a09c94a`.
  They are byte-identical to target-files boot and sparse-to-raw system.
  Unpacking the exact payload again proves the first-stage and later markers are
  in the executable binaries. TRY8 is approved for one controlled diagnostic
  sideload after explicit authorization.
- After explicit authorization, TRY8 installed from recovery B to target A with
  status 0. Ignored recovery log
  `lineageos/.downloads/recovery-slotb-try8-20260726.log`, SHA-256
  `ffca11679ddf7f9685939091b20cf58e0a6b51f291b3327419d16ac0784bce66`,
  proves all OTA actions succeeded. It may contain identifiers and must remain
  untracked/unquoted.
- TRY8 exhausted slot A and fell back to B. Recovery B again found no
  `/metadata/vold/bootloop-stage`, then unmounted metadata. The exact payload
  contains the direct first-stage marker, so normal `DoFirstStageMount()` did not
  reach completion.
- Source inspection shows `DoCreateDevices()` mounts metadata before creating
  logical partitions, then `DoFirstStageMount()` mounts system-as-root and the
  remaining first-stage partitions. Temporary TRY9 instrumentation records
  device/logical setup success or failure, system mount start/failure/success,
  each remaining partition mount start/failure/success, and the outer mount
  failure. Because metadata is available before these operations, the exact
  failing first-stage step should now survive. Static diff checks pass; focused
  first-stage compilation remains required.
- The user built a pre-correction TRY9 target-files archive: 2,614,941,963 bytes,
  SHA-256 `2ce942af970158f9693d8fea9a2cb8d24843bd8bf8f716220d31c9a52d982ca2`;
  ZIP integrity and packaged markers passed. It is **not approved**: the outer
  `first-stage-mount-failed` marker would overwrite the specific system or
  partition failure. That one outer marker has now been removed from source, so
  the archive is stale and must not be used to generate an OTA.
- Full continuation guide:
  `docs/handoff-20260726-first-stage-mount.md`. The immediate next step is to
  rebuild `init_first_stage` and `target-files-package` from the corrected
  source, then inspect and generate TRY9 from that exact new archive. Current
  phone state is slot-B Recovery with ADB enabled, 100% battery, metadata
  unmounted, and slot A unbootable after TRY8.

## 2026-07-26 TRY9 metadata channel proof and verified artifact

- Root concern found before building: `RecordBootloopStage()` called
  `mkdir_recursive("/metadata/vold")` unconditionally. `first_stage_mount.cpp`
  `DoCreateDevices()` ignores a failed `/metadata` mount (the `MountPartition`
  result is only used to gate `CopyDsuAvbKeys()`), and the boot ramdisk ships a
  `/metadata` directory. If that mount failed, every marker was created on the
  initramfs, `fsync()` succeeded on ramfs, and the evidence was freed with the
  ramdisk. This alone explains TRY5-TRY8 returning nothing and would have made
  TRY9 return nothing too.
- Fix applied to the temporary diagnostics: `RecordBootloopStage()` now compares
  `stat("/").st_dev` with `stat("/metadata").st_dev` and refuses to write unless
  metadata is a distinct mounted filesystem. `DoCreateDevices()` records
  `first-stage-metadata-mounted` on success and
  `first-stage-metadata-mount-failed` / `first-stage-metadata-absent-from-fstab`
  otherwise. `sys/stat.h` was added to `system/core/init/util.cpp`.
- The generic outer `first-stage-mount-failed` marker is confirmed absent from
  every built artifact; only the per-partition `first-stage-mount-failed:` form
  remains.
- Verified TRY9 target-files archive:

```text
size: 2,614,944,502 bytes
SHA-256: 59f6c5145f7848b4b7c3ca264b05be3bc5ea9758db8fd1dbcc1dabdeea1489f6
```

- Verified TRY9 OTA
  `lineageos/out/target/product/odessa/lineage-23.2-20260726-BOOTLOOP-TRY9-UNOFFICIAL-odessa.zip`:

```text
size: 1,028,483,153 bytes
SHA-256: 171f5b413014301bf69b3dfaca27b4793f8bec9de6da8e5f972d21f88fd996a6
payload size: 1,028,475,859 bytes
payload SHA-256: aa8c0f34b69bba8b0212b1165d658026b829614ed462d0d70fc71086e12b338e
```

  ZIP integrity passes, required A/B entries are present, and the payload's
  base64 SHA-256 matches `payload_properties.txt` `FILE_HASH` exactly.
- Provenance chain closed: payload `boot.img` SHA-256
  `6618b642c503ca12995a77d2e92872757761bacde0e7717a7015b24bade74269` is
  byte-identical to target-files `IMAGES/boot.img`, and its unpacked ramdisk
  `init` SHA-256 `964a3d79e0ceb44d6626eaed72bd4dd56c9177c7e2fb0b9acebc1c00c5e1d069`
  matches both `BOOT/RAMDISK/init` and the freshly built
  `out/target/product/odessa/ramdisk/init`. All 13 markers and the guard string
  are present in that exact payload binary.
- `ota_from_target_files` must not be given `--output_metadata_path /dev/null`;
  the tool appends `.pb` and fails at the final metadata write with
  `PermissionError: /dev/null.pb`. Omit the flag.
- New observation to test, not yet a finding: in the shipping ramdisk
  `fstab.qcom`, `/metadata` is the only entry using `/dev/block/by-name/` while
  every other entry uses `/dev/block/bootdevice/by-name/`. If that symlink does
  not resolve during first-stage device init, the silently ignored mount failure
  above follows. Investigate this first if TRY9 still returns no marker.
- Unexplained correlation to keep open: every build that writes to `/metadata`
  early (TRY3 onward) loops in about 2-3 s with no bootloader unlock warning,
  while TRY2, which does not, held the logo about 20-37 s and did show the
  warning. The user reconfirmed the fast signature on 2026-07-26. TRY3 was
  already rejected once for changing boot behaviour; that precedent was never
  applied to TRY4-TRY9.
- TRY9 has not been installed or booted. The phone remains in slot-B Lineage
  Recovery; slot A is unbootable after TRY8.

## 2026-07-26 BREAKTHROUGH: the boot dies at the BPF loader, not in first-stage mount

- TRY9 installed from recovery B to target A with `Install completed with status 0`,
  `source_slot: B`, `target_slot: A`, and `DownloadAction`,
  `FilesystemVerifierAction`, `PostinstallRunnerAction` all `kSuccess`. Ignored
  recovery log `lineageos/.downloads/recovery-slotb-try9-20260726.log`, SHA-256
  `127f4b6672b2501d71068d7efe2ad85be06389cf998df4aa7369478337a1db3e`. The
  `Failed to submit transaction in checkpointing` errors are pre-existing noise:
  130 in TRY7, 128 in TRY8, 130 in TRY9, all with status 0.
- After the slot-A boot test, `/metadata/vold/bootloop-stage` **exists** and
  contains exactly `bpfloader-start` (15 bytes). This is the first non-empty
  stage result in the entire TRY5-TRY9 series.
- `bpfloader-start` is written by temporary instrumentation at the first line of
  `on load-bpf-programs` in `system/core/rootdir/init.rc`. The next marker,
  `bpfloader-complete`, is written immediately after `exec_start bpfloader`.
  **The boot therefore dies at `exec_start bpfloader`.**
- This overturns the TRY8 conclusion. First-stage mounting, SELinux setup,
  second-stage entry, boot-script parsing, `post-fs`, and the whole of
  `post-fs-data` (data key, persist props, APEX/KeyMint, `init_user0`,
  classpath, odsign, `verity_update_state`) all complete. It also explains TRY5:
  `zygote-start` was never reached because BPF loading precedes it.
- Provenance: the file's mtime is a real 2026 date, and recovery's clock is
  bogus (`1970-01-14`), so full Android wrote it. Only slot-A builds TRY6-TRY9
  write this path, and TRY6, TRY7 and TRY8 were each verified absent after their
  own runs, so TRY9 wrote it.
- Honest caveat, not yet resolved: the recorded mtime is about 32 minutes behind
  host wall-clock for the observed boot attempts. The device RTC has not synced
  since it last booted fully, so the offset is plausible but unverified. The
  contradiction with TRY6-TRY8 producing nothing is also not fully explained;
  do not treat the earlier "dies before post-fs" conclusion as merely a
  measurement artifact until that is understood.
- Prime suspect: Android 16's BPF loader against Linux 4.14.336. The built
  kernel config has `CONFIG_BPF`, `CONFIG_BPF_SYSCALL`, `CONFIG_BPF_JIT`,
  `CONFIG_BPF_JIT_ALWAYS_ON`, `CONFIG_BPF_EVENTS`, `CONFIG_CGROUP_BPF` and
  `CONFIG_NET_CLS_BPF`, but **`CONFIG_DEBUG_INFO_BTF` does not exist in 4.14**
  (BTF arrived in 5.2), and `CONFIG_NET_ACT_BPF` and `CONFIG_BPF_STREAM_PARSER`
  are unset. Modern `netbpfload`/`bpfloader` requires BPF features and program
  types that a 4.14 kernel may not provide.
- Next investigation is host-side and costs no slot cycle: identify which
  bpfloader binary the build ships, which `.o` programs it loads, and which of
  them 4.14 cannot support. Do not add another init marker build for this.
- Device state after the run: both slots were re-armed by Motorola ABL's
  "No bootable A/B slot. Failed to boot Linux, falling back to fastboot"
  fallback. Verified bootloader state afterwards was current slot A, A bootable
  with 5 retries, B bootable with 7 retries, neither slot successful,
  `securestate: flashing_unlocked`. Nothing was wiped. Recovery on slot A boots
  with ADB after accepting the authorization prompt; metadata was mounted
  read-only, only the exact stage path was read, and it was unmounted
  immediately.

## 2026-07-26 Root cause of the bpfloader bootloop: kernel 4.14 vs Android 16 BPF

Host-side source analysis only. No device commands were run. Nothing below has
been proven by a boot yet.

- The `bpfloader` service init starts is **not** `/system/bin/bpfloader`. The
  platform script
  `packages/modules/Connectivity/bpf/loader/netbpfload.rc:12` defines
  `service bpfloader /system/bin/false`, and the Tethering APEX's
  `netbpfload.35rc:3` overrides it with
  `/apex/com.android.tethering/bin/netbpfload` (`override` at
  `netbpfload.35rc:69`). That service carries
  `reboot_on_failure reboot,bpfloader-failed` (`netbpfload.35rc:68`), so any
  non-zero exit from `netbpfload` reboots the device immediately, which matches
  the observed 2-3 s loop.
- `netbpfload` computes `api_level_full` from `ro.build.version.sdk_full`
  (`36.1` in the built `system/build.prop`) and from the `# 2025 4 36 1 0 #`
  header of `/system/etc/init/netbpfload.rc`, giving `3610`
  (`packages/modules/Connectivity/bpf/headers/include/bpf/BpfUtils.h:45-76`).
  So `isAtLeastV`, `isAtLeast25Q2` and `isAtLeast25Q4` are all true.
- **Root cause:**
  `packages/modules/Connectivity/bpf/loader/NetBpfLoad.cpp:1620-1625`
  `if (isAtLeastV && !isAtLeastKernelVersion(4, 19)) { ALOGE("Android V requires kernel 4.19."); return 5; }`
  The device kernel is 4.14.336, so `netbpfload` exits 5 before loading anything.
  The very next gate, `NetBpfLoad.cpp:1627-1632`, requires kernel 5.4 for 25Q2+.
- Android's minimum kernel per release: 4.9 for S/T, **4.14 for U (LineageOS 21)**,
  **4.19 for V (LineageOS 22)**, **5.4 for 25Q2 / Android 16 (LineageOS 23)**.
  LineageOS 21 is the newest branch a stock 4.14 kernel satisfies unmodified.
- LineageOS's sanctioned answer is `ro.bpf.kver_override`, present in all three
  loaders in this checkout:
  `packages/modules/Connectivity/bpf/headers/include/bpf/KernelUtils.h:31-42`
  (LineageOS commit `75e4580fc6`, "bpf: Allow overriding kernel version",
  tested on "sm8150 device based on 4.14 kernel with 5.4 bpf backported"),
  `packages/modules/UprobeStats/src/bpf/headers/include/bpf/KernelUtils.h:30-45`,
  and `system/bpf/loader/bpfloader.rs` `kernel_version()`.
  LineageOS **abandoned** the alternative of relaxing the loader's checks
  (Gerrit topic `legacy-bpf-compat`, changes 433516/433517 and the
  `android_system_bpf` 4.9-T series, all ABANDONED on `lineage-23.0`).
- The override is a claim about backported kernel features, not a bypass. Both
  LineageOS 4.14 devices that ship it also ship a full BPF backport:
  - `LineageOS/android_kernel_xiaomi_sm6125` `lineage-23.2` is 4.14.357-openela
    and now contains `kernel/bpf/btf.c`, `ringbuf.c`, `bpf_local_storage.c`,
    `bpf_inode_storage.c`, `trampoline.c`, `bpf_struct_ops.c`, `bpf_iter.c`,
    `cpumap.c`, `queue_stack_maps.c`, `sysfs_btf.c` and more. Its device tree
    `android_device_xiaomi_sm6125-common/lineage-23.2/product.prop` sets
    `ro.bpf.kver_override=5.10.239` (`5.4.299` on `lineage-23.0`).
  - `LineageOS/android_kernel_oneplus_sm8150` `lineage-23.2` is the same shape
    (4.14.357-openela, 120 commits touching `kernel/bpf/btf.c` alone);
    `android_device_oneplus_sm8150-common/lineage-23.2/product.prop` also sets
    `ro.bpf.kver_override=5.10.239`.
  - `git compare lineage-22.2...lineage-23.2` on the sm6125 kernel is **3090
    commits ahead**, overwhelmingly upstream BPF backports.
- `kernel/motorola/sm6150` at 4.14.336 has none of it. `kernel/bpf/` holds only
  the stock 4.14 set (no `btf.c`, no `ringbuf.c`); `include/linux/btf.h` does not
  exist; `include/uapi/linux/bpf.h` `enum bpf_cmd` stops at
  `BPF_OBJ_GET_INFO_BY_FD` (no `BPF_BTF_LOAD`); `enum bpf_map_type` stops at
  `BPF_MAP_TYPE_SOCKMAP` (no `DEVMAP_HASH`); `bpf_attr` has no `map_name` or
  `prog_name`. The stale `reference/sm6125-lineage-22.2` branch fetched into this
  repo is from before the backport and must not be used as the reference.
- **Setting `ro.bpf.kver_override` alone on this kernel would not fix the boot;
  it would only move the failure.** With the minimum viable value of 5.4:
  - `NetBpfLoad.cpp:826-846` then takes the `isAtLeastKernelVersion(4, 19)` BTF
    path and calls `btf__load_into_kernel()`, i.e. `BPF_BTF_LOAD`, which does not
    exist before 4.18;
  - `sanitizeMapType()` (`NetBpfLoad.cpp:808-818`) stops rewriting
    `BPF_MAP_TYPE_DEVMAP_HASH` to `HASH` at 5.4, so `tether_dev_map`
    (`bpf/progs/offload.c:791`) would be created with a map type the kernel does
    not have;
  - the 5.4 variants of the netd and offload programs would be selected and use
    `skb->gso_segs`, `skb->gso_size`, `skb->sk` and `bpf_sk_fullsock()`
    (`bpf/progs/netd.c:186-199`, `bpf/progs/offload.c:187-193`), none of which
    exist in 4.14.
  Each of those is another guaranteed non-zero exit and another reboot.
- Cheap device-side confirmation available next time the phone is in recovery
  with `/metadata` mounted read-only: `system/core/init/reboot.cpp:96-106`
  persists the reboot reason to `LAST_REBOOT_REASON_FILE`, which
  `system/core/libcutils/include/cutils/android_reboot.h:33-34` defines as
  `/metadata/bootstat/persist.sys.boot.reason`. If that file names
  `bpfloader-failed`, the diagnosis is confirmed end to end.
- Two honest options, both requiring the user's decision:
  1. Port the BPF backport from `LineageOS/android_kernel_xiaomi_sm6125`
     `lineage-23.2` (closest analogue: also Qualcomm msm-4.14) into
     `kernel/motorola/sm6150`, then set `ro.bpf.kver_override` to match. Bring the
     kernel to 4.14.357-openela first to cut conflicts. Large kernel project,
     only verifiable by booting hardware.
  2. Retarget to LineageOS 21 (Android 14), the newest branch whose BPF loader
     accepts an unmodified 4.14 kernel, and revisit 23.2 after the backport.

## 2026-07-27 CONFIRMED END TO END: `reboot,bpfloader-failed`

- Read-only from recovery on slot A, `/metadata/bootstat/persist.sys.boot.reason`
  contains exactly `reboot,bpfloader-failed`, and
  `/metadata/vold/bootloop-stage` still contains `bpfloader-start`. Metadata was
  mounted read-only, only those two exact paths were read, and it was unmounted
  immediately.
- `reboot,bpfloader-failed` is the literal string from
  `packages/modules/Connectivity/bpf/loader/netbpfload.35rc:68`
  (`reboot_on_failure reboot,bpfloader-failed`). The bootloop cause is proven,
  not inferred.
- Independently verified in this checkout:
  - `netbpfload.35rc:3` sets `service bpfloader /apex/com.android.tethering/bin/netbpfload`
    with `override` at `:69`, so `exec_start bpfloader` runs the APEX loader, not
    `/system/bin/bpfloader`;
  - `NetBpfLoad.cpp` returns 5 when `isAtLeastV && !isAtLeastKernelVersion(4, 19)`,
    and 6 when `isAtLeast25Q2 && !isAtLeastKernelVersion(5, 4)`;
  - `out/target/product/odessa/obj/KERNEL_OBJ/include/generated/utsrelease.h`
    is `"4.14.336-perf+"`;
  - `ro.bpf.kver_override` exists in both
    `packages/modules/Connectivity/bpf/headers/include/bpf/KernelUtils.h:38-40`
    and `system/bpf/loader/bpfloader.rs:429`;
  - the kernel lacks `kernel/bpf/btf.c`, `kernel/bpf/ringbuf.c` and
    `include/linux/btf.h`, and its `uapi/linux/bpf.h` has zero occurrences of
    `BPF_BTF_LOAD` or `BPF_MAP_TYPE_DEVMAP_HASH`.
- Android kernel minimums: 4.14 for Android 14 (LineageOS 21), 4.19 for Android
  15 (LineageOS 22), 5.4 for Android 16 / 25Q2 (LineageOS 23). **LineageOS 21 is
  the newest branch an unmodified 4.14 kernel satisfies.**
- `ro.bpf.kver_override` alone is NOT a fix and must not be shipped alone. It is
  a claim that BPF features were backported. Setting it only advances the failure:
  at >= 4.19 the loader takes the BTF path (`btf__load_into_kernel()` ->
  `BPF_BTF_LOAD`, absent before 4.18); at >= 5.4 `sanitizeMapType()` stops
  rewriting `BPF_MAP_TYPE_DEVMAP_HASH`; and the 5.4 program variants reference
  `skb->gso_segs`, `skb->gso_size`, `skb->sk` and `bpf_sk_fullsock()`, none of
  which exist in 4.14.
- LineageOS abandoned the "relax the loader" approach: Gerrit topic
  `legacy-bpf-compat` (changes 433516/433517) is ABANDONED on `lineage-23.0`.
- Working precedent for 4.14 on LineageOS 23.2, both Qualcomm msm-4.14:
  `LineageOS/android_kernel_xiaomi_sm6125` and
  `LineageOS/android_kernel_oneplus_sm8150`, both at 4.14.357-openela with real
  BPF backports (`btf.c`, `ringbuf.c`, `bpf_local_storage.c`, `trampoline.c`,
  `bpf_struct_ops.c`, `bpf_iter.c`) and `ro.bpf.kver_override=5.10.239` in their
  device trees. The sm6125 `lineage-22.2...lineage-23.2` delta is ~3090 commits,
  overwhelmingly upstream BPF backports. The `reference/sm6125-lineage-22.2`
  branch already present in the local kernel repo predates the backport and is
  stale for this purpose.
- Do not mark the bpfloader service non-critical: netd depends on the pinned
  programs, so netd would crashloop and take system_server with it. The
  `reboot_on_failure` exists because that failure is unrecoverable.
- `CONFIG_BPF_UNPRIV_DEFAULT_OFF` is not set in the built kernel config. If a BPF
  backport is undertaken, enable it then; 4.14's verifier lags badly on
  Spectre-class hardening.

## 2026-07-27 BPF backport scoping result: the port target is nearly pristine

Host-only measurement, no builds, no device contact. Reference fetched as a
blob-less partial clone into the existing kernel repo:
`refs/remotes/reference/sm6125-lineage-23.2` from
`https://github.com/LineageOS/android_kernel_xiaomi_sm6125.git`.

- `reference/sm6125-lineage-22.2` is 4.14.356-openela-rc1 and has **none** of
  `kernel/bpf/btf.c`, `ringbuf.c`, `bpf_local_storage.c`, `trampoline.c`,
  `bpf_struct_ops.c`, `bpf_iter.c`, `include/linux/btf.h`.
- `reference/sm6125-lineage-23.2` is 4.14.357-openela and has all of them.
- 22.2 is a **strict ancestor** of 23.2 (0 commits the other way), so the
  backport is exactly the 22.2 -> 23.2 delta on one tree.
- Whole delta: 3084 non-merge commits, 1605 files, +144,402 / -35,999.
- BPF-core subset: 1592 non-merge commits, 69-70 files,
  **+56,087 / -9,887**. Of those 70 files, **29 already exist in
  `kernel/motorola/sm6150` and 41 are new files** (new files cannot conflict).
- **The decisive number:** our kernel's BPF area differs from sm6125's
  *pre-backport* state by only **171 insertions / 52 deletions across 12 files**
  (`arch/arm64/net/bpf_jit_comp.c`, `include/linux/bpf.h`,
  `include/uapi/linux/bpf.h`, `kernel/bpf/{arraymap,core,hashtab,lpm_trie,
  map_in_map,stackmap,syscall}.c`, `kernel/bpf/map_in_map.h`,
  `net/core/filter.c`) — despite 22,748 commits in ours not in theirs and 3,844
  in theirs not in ours. `include/linux/filter.h` and `include/linux/bpf-cgroup.h`
  are byte-identical to the reference. BPF is core kernel code that vendor trees
  barely touch, so the conflict surface is far smaller than the raw commit count
  suggests.
- Honest caveats on these numbers:
  - The 1592/3084 split is approximate. Individual files carry mixed changes, so
    a per-file diffstat of e.g. `net/core/dev.c` (+905/-174) or
    `security/security.c` (+720/-107) is mostly the 356->357 stable bump and LSM
    work, not BPF.
  - `git rev-list` pathspec counts require `--full-history`; without it git's
    history simplification reports 0 for paths introduced through merges.
  - It is not yet established whether the BPF series depends on the
    4.14.356/357 stable level. Our kernel is at 4.14.336.
- Conclusion: feasible, and materially smaller than the raw "3090 commits"
  figure implies. Not yet started; awaiting the user's go-ahead.
- If undertaken: set `ro.bpf.kver_override` to match what is actually backported
  (sm6125 and sm8150 both use `5.10.239`), and enable
  `CONFIG_BPF_UNPRIV_DEFAULT_OFF`, which is currently unset.

## 2026-07-27 stable-level question settled: no full 336->357 bump needed for BPF

Host-only, no builds, no device contact, no tree modified.

- The BPF-path delta 22.2 -> 23.2 was generated (71 files, 74,243 patch lines)
  and tested with `git apply --check` against `kernel/motorola/sm6150` HEAD.
  It fails on exactly **10 files**: `include/linux/bpf.h`,
  `include/uapi/linux/bpf.h`, `kernel/bpf/{arraymap,core,hashtab,map_in_map,
  stackmap,syscall}.c`, `kernel/bpf/map_in_map.h`, `net/core/filter.c`.
  These are the same files as the known 171/52 divergence; nothing new failed.
- Inspecting that divergence shows it is a **BPF baseline gap, not Motorola
  vendor divergence**. The reference tree has and ours lacks:
  `map_fd_put_ptr(struct bpf_map *, void *, bool need_defer)`,
  `char name[BPF_OBJ_NAME_LEN]` in `struct bpf_map`, `load_time` + `name` in
  `struct bpf_prog_aux`, and the `lpm_trie` `prefixlen > max_prefixlen` bounds
  check. One is an explicit Android backport commit in the reference tree:
  `6b3a3a549ab1 BACKPORT: bpf: Use char in prog and map name`.
- Verified feature presence:
  - ours (4.14.336): `BPF_OBJ_NAME_LEN`, `need_defer`, `BPF_BTF_LOAD`,
    `BPF_MAP_TYPE_DEVMAP_HASH`, `bpf_sk_fullsock` all **absent**;
  - reference pre-backport (4.14.356, lineage-22.2): `BPF_OBJ_NAME_LEN`
    **present** in 3 files; `BPF_BTF_LOAD` and `BPF_MAP_TYPE_DEVMAP_HASH` still
    absent (those arrive in 23.2).
- **Answer: a full 4.14.336 -> 4.14.357 stable bump is NOT a prerequisite for
  the BPF work.** The BPF-relevant portion of that stable gap is only
  ~171 insertions / 52 deletions across 12 files. Close that small baseline gap
  first, then the 23.2 backport applies to the same shape of tree the reference
  had.
- Recommended order if the port proceeds: (1) close the ~220-line BPF baseline
  gap in the 12 files; (2) apply the 22.2 -> 23.2 BPF delta (69-71 files,
  +56,087 / -9,887, of which 41 files are new and cannot conflict); (3) set
  `ro.bpf.kver_override` to match and enable `CONFIG_BPF_UNPRIV_DEFAULT_OFF`;
  (4) build kernel/boot/dtbo; (5) hardware boot test.
- Remaining unquantified risk: only the BPF pathspec was apply-tested. The
  backport commits also touch `net/core/dev.c`, `net/core/sock.c`,
  `security/security.c`, `include/linux/lsm_hooks.h`, `init/Kconfig` and others
  where the reference's diffs are dominated by non-BPF work. Integration effort
  outside the BPF pathspec is real and not yet measured.

## 2026-07-27 BPF backport attempt: partial, does NOT build yet

Branch `wip/bpf-backport-4.14.336` in `kernel/motorola/sm6150`, 13 commits ahead
of `lineage-23.2`, working tree clean, `git diff --check` clean. `lineage-23.2`
is untouched. The uncommitted diagnostics in `system/core` (9 files),
`system/sepolicy` (1) and `device/motorola/sm6150-common` (2) are intact.

- **Baseline gap (the 171/52 divergence): CLOSED and verified.** 8 of 9 commits
  cherry-picked with `-x` from `reference/sm6125-lineage-22.2`. Four items could
  not be cherry-picked because they reached the reference through squashed
  stable-merge imports between 4.14.337 and .356 and the local
  `android-common/deprecated/android-4.14-stable` ref stops at .336; those 7
  files were taken verbatim from the reference. After this, the 22.2 -> 23.2
  BPF-path delta applied with **zero conflicts**.
- **Technique: path-scoped tree import, not a 1592-commit cherry-pick.**
  Justified because the delta applied conflict-free (a cherry-pick series would
  produce a byte-identical tree), intermediate states are not meaningfully
  bisectable (every one is a 4.14 kernel the loader still rejects), and each
  commit carries non-BPF hunks that would conflict against 22,748 commits of
  Motorola divergence.
- The 5.4-not-5.10 scope update did **not** cause a trim: `verifier.c`,
  `syscall.c` and `btf.c` are monolithic 5.10 files and "trimming to 5.4" would
  mean hand-writing a different verifier. The 5.10 shape is a superset. The
  update did stop the import of `net/xdp/`, `net/bpfilter/`, `bpf-lirc`,
  `tcp_bpf.c`, `preload/` and `tools/`.
- `CONFIG_BPF_UNPRIV_DEFAULT_OFF=y` added to
  `arch/arm64/configs/vendor/odessa_defconfig` (line 219) and confirmed in the
  generated `.config`.

### Build status: FAILS. 26 of 32 `kernel/bpf` objects compile.

Compiling: `core syscall verifier inode helpers tnum btf hashtab arraymap
percpu_freelist bpf_lru_list lpm_trie map_in_map local_storage queue_stack_maps
ringbuf disasm dispatcher trampoline bpf_local_storage cgroup bpf_iter map_iter
task_iter prog_iter bpf_struct_ops`.

Failing: `devmap.c` (**required** - `tether_dev_map` is `DEVMAP_HASH` with no
`min_kver`; needs 5.x XDP infra: bulk `ndo_xdp_xmit`, `xdp_bulkq` in
`struct net_device`, 4-arg `hlist_for_each_entry_rcu`, `__list_del_clearprev`),
plus `cpumap.c`, `offload.c`, `net_namespace.c`, `stackmap.c`,
`reuseport_array.c`. The latter four are small; `cpumap`/`offload` are not
required. **`devmap.c` is the real remaining blocker.** Beyond `kernel/bpf`,
`net/core/filter.c`, `kernel/trace/bpf_trace.c`, `security/bpf/` and the
whole-kernel link have never been exercised.

### Independently verified by the main agent

- The reference tree `sm6125-lineage-23.2` has a **genuine defect**: its
  `include/linux/vmalloc.h` defines `VM_LOWMEM 0x00000100` (line 24) **and**
  `VM_FLUSH_RESET_PERMS 0x00000100` (line 29) - the same bit. Copying it would
  corrupt Qualcomm VM_LOWMEM tracking on every JIT allocation. The port
  correctly did not copy it and made `set_vm_flush_reset_perms()` a documented
  no-op. Do not "fix" this by taking the reference's header.
- Import faithfulness: `include/linux/bpf.h`, `include/uapi/linux/bpf.h`,
  `include/linux/btf.h`, `include/linux/filter.h` and `net/core/filter.c` are
  **byte-identical** to the reference. `kernel/bpf` differs by 967/945 across 20
  files, which is the deliberate 4.14 adaptation.
- The flagged context-offset risk is substantially mitigated by design:
  `bpf_convert_ctx_access()` uses `bpf_target_off(struct sk_buff, ...)`, which
  recomputes offsets from this tree's own struct definitions rather than
  hardcoding them (53 such uses). Residual risk is limited to fields whose type
  or bitfield packing differs between trees, most of which would fail to
  compile. This is mitigation, not proof.

### Documented functional gaps (deliberate, not hidden stubs)

`perf_event_bpf_event()`/`perf_event_ksymbol()` are no-ops (perf shows
unresolved JIT addresses); `register/modify/unregister_ftrace_direct()` return
`-ENODEV` so BPF trampolines cannot attach; `bpf_xdp_link_attach()` returns
`-EOPNOTSUPP` (XDP still attaches the 5.4 way via `dev_change_xdp_fd()`);
`call_rcu_tasks_trace()` maps to `call_rcu()`; `populate_bpffs()` is a no-op.

### Unproven

Everything past compilation: the whole-kernel link, whether the 5.10 verifier
correctly verifies programs against 4.14 `struct sk_buff`/`struct sock` layouts,
and whether the device boots. **Do not set `ro.bpf.kver_override` until the
kernel links and the context-access offsets are checked.**

## 2026-07-27 kernel strategy research: what xiaomi_sm6150 did, and why 5.10/6.x is not a path

Host-only research, no builds, no device contact, no tree modified.

### What `LineageOS/android_kernel_xiaomi_sm6150` did (verified)

- Branches: 17.1, 20, 21, 22.1, 22.2, 23.0, 23.1, 23.2. `lineage-22.2` is
  **4.14.356-openela-rc1** and has no BPF backport (same as sm6125 22.2).
  `lineage-23.2` (tip `e03e5ba22586be70673afb5d3c3f70510524e658`, updated
  2026-07-04) is **4.14.357-openela** with the full 5.10-era BPF backport:
  `btf.c` (147 KB, kflag-era), `ringbuf.c`, `trampoline.c`, `bpf_struct_ops.c`,
  `bpf_iter.c`, `bpf_local_storage.c`, `bpf_inode_storage.c`, `local_storage.c`,
  `cpumap.c`, **`devmap.c`**, `queue_stack_maps.c`, `sysfs_btf.c`,
  `reuseport_array.c`, `net_namespace.c`, `offload.c`, `task/prog/map_iter.c`,
  and a 379 KB `verifier.c`.
- **Every file in its `kernel/bpf/` is byte-identical (same git blob SHA) to
  `reference/sm6125-lineage-23.2`** — verified locally with `git ls-tree`
  against the GitHub API blob IDs. The backport is one coordinated LineageOS
  msm-4.14 effort shared across xiaomi sm6125, xiaomi sm6150, and oneplus
  sm8150. Our sm6125 reference is therefore interchangeable with xiaomi sm6150
  for the BPF core; no second fetch is needed for `kernel/bpf/` itself.
- `LineageOS/android_device_xiaomi_sm6150-common/lineage-23.2/product.prop`
  sets `ro.bpf.kver_override=5.10.239`, identical to sm6125/sm8150.
- This is the **same SoC family as odessa**: the xiaomi sm6150 platform covers
  tucana/toco (SM7150-AB Snapdragon 730G, Adreno 618) and davinci (SD730).
  The LineageOS wiki lists **tucana as officially supported on LineageOS 23.2
  (Android 16), kernel 4.14** (previously 22.2 and 23.0). So the
  4.14+OpenELA+BPF-backport path is officially shipped and hardware-validated
  on the same silicon odessa uses.
- They did **not** upgrade to 5.10 or 6.x.

### OpenELA facts

- OpenELA `kernel-lts` `linux-4.14.y` continues upstream 4.14 after its Jan
  2024 EOL at 4.14.336, following upstream stable rules; current releases are
  4.14.356/357-openela (2026). Tags carry the `-openela` suffix.
- **OpenELA alone does not fix the bootloop.** 4.14.357-openela still lacks
  BTF/DEVMAP_HASH/ringbuf; it only extends the stable patch level. The working
  recipe is OpenELA **plus** the BPF backport **plus** `ro.bpf.kver_override`.
  Taking our tree from 4.14.336 to 4.14.357-openela is optional for the BPF
  work (MEMORY 2026-07-27 proved the BPF-relevant stable gap is ~171/52 lines,
  already closed in `wip/bpf-backport-4.14.336`), but worthwhile for security
  and for matching the reference trees' baseline.

### Why 5.10/6.x rebase is rejected for this device

- No msm-5.4/5.10/6.x BSP exists for SM6150/SM7150: Qualcomm never shipped one
  for this platform (first msm-5.4 was SM8350/lahaina); no LineageOS, Xiaomi,
  or Motorola 5.x tree exists for it. A rebase would mean porting the entire
  vendor stack (sdmmagpie DT, KGSL/Adreno 618, camera CAMX/CHI-CDK ioctls,
  audio/display techpacks, modem/IPA, qcacld WLAN, fingerprint, touchscreen,
  Motorola drivers) with no base tree and no precedent on any commercial
  msm-4.14 device.
- Odessa's Android-10-generation (API 29) vendor blobs are built against the
  4.14 kernel UAPI; a major-version jump risks silent ABI breakage that cannot
  be fixed without blob sources. Every LineageOS msm-4.14 platform chose
  backport over rebase for this reason.
- VINTF does not require a newer kernel: the build is already COMPATIBLE at
  FCM 6 with 4.14.336 (proven 2026-07-18). AOSP's android-common table lists
  android12-5.10 through android16-6.12 as Android-16-compatible ACK branches;
  the **only** component forcing a kernel change on odessa is the BPF loader's
  feature set.
- The only real SM7150 6.x work is `sm7150-mainline` (postmarketOS, now
  6.18-era) and LineageOS's experimental `android_device_xiaomi_mi7150-mainline`
  (U-Boot boot stack, permissive SELinux, no Android vendor drivers). It is a
  separate architecture, not a vendor-kernel rebase; keep it as research input
  only, per the standing decision.
- Android 16's launch GKI is 6.12; 5.10 remains supported only as an older
  upgrade branch. Neither changes the conclusion.

### Decision-relevant conclusion

Continue `wip/bpf-backport-4.14.336` (Option A). The remaining `devmap.c`
build blocker is solved in both reference trees: their `devmap.c` builds
because the reference delta also carries the 5.x XDP infrastructure
(`net/core/dev.c`, `include/linux/netdevice.h` — the "outside the BPF
pathspec" integration flagged 2026-07-27). Port that XDP-infra portion next.
If the backport ultimately fails, the fallback is LineageOS 21 (Android 14),
the newest branch an unmodified 4.14 kernel satisfies — not a 5.10/6.x rebase.
