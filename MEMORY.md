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
