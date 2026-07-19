# Motorola RPAS31.Q2-59-17-4-3-9 Firmware Validation

Validated HOST ONLY on 2026-07-19. No `adb`, `fastboot`, flashing, device access, or Android source change was performed.

## Package identity

- Path: `downloads/ODESSA_RETAIL_RPAS31.Q2_59_17_4_3_9_subsidy_DEFAULT_regulatory_DEFAULT_CFC.xml`
- Product: `odessa_retail`
- Build: `RPAS31.Q2-59-17-4-3-9`, Android 11, build hash `412e48`
- Build date: 2022-08-18
- Fingerprint: `motorola/odessa_retail/odessa:11/RPAS31.Q2-59-17-4-3-9/412e48:user/release-keys`
- Bootloader: `MBM-3.0-odessa_retail-ce4c20166-220818`
- Baseband: `M7150_22.31.04.72R`
- FSG: `FSG-6150-07.72`
- Provenance: Motorola Software Fix automatically identified the connected phone and selected this exact package. The IMEI and serial number were not recorded.

All 19 payload MD5 values matched `flashfile.xml`, including all nine `super.img_sparsechunk.0` through `.8` files.

Independent SHA-256 values:

```text
ae59d68b7718c5615ad3812b26362649575fcf8c510b4c8639ad20aec194a0fc  BTFM.bin
b0767f5619f7a6af4b0a3bfa9f25cdf7ace98f1e35a7135173f0bd418c9fd9da  boot.img
317db9709d718b177d25624552976c41f8f096bb7408b2ca00e29d7b620c0b54  bootloader.img
32b5f820436092acbc37309ff9f0759b2c059fde8bbdda92d71c7b24cbb9f1fa  dspso.bin
103e607548fd29c6007f8740a2bc2a706acec04df12f489e83f5a10a3b73939e  dtbo.img
100509d3831affc40434ce4876fe979cbd8b91c3c9b0d793eb4a01fd2414b505  gpt.bin
7828af7d30ffa190c4f718241c5deff549e81b6be928ccc3c2e285652446faef  logo.bin
1dd89227f0614a761199153b3ac4658a685974a2dac26c87561b5a74f2cbf580  radio.img
f37be67b4460f10d58255cf7e90f61c3c831f855212574e713931465a6dba6f5  recovery.img
5b04d61697dda3ec505e967b978b4712c458680e8d9ff58bc647726501233e97  super.img_sparsechunk.0
37c2a79b86e99b7fd9ef7b173c04603708649fcd51b853ee4405f77a6f833750  super.img_sparsechunk.1
0a42f2a067c0b6f180cbfe500b912520f13a403290bcf9811dfe2cb3296c069a  super.img_sparsechunk.2
505ee9169115b8d8392a9df4efbdb0d11e9ded34898c4bd81b203205777ab531  super.img_sparsechunk.3
73bf15dddf8d221b6b7ef00f3d2f90f20bedc0c5e7fdfef9b256ec3c19d396fa  super.img_sparsechunk.4
2c26b177c54d3d7d6404d3c6d7b8810c14e4a937c7d0cac37c3318bf7a056732  super.img_sparsechunk.5
bd2f380e156d452f04370c24480f99181618cbd0dbea1abe2015daf2f2bbf597  super.img_sparsechunk.6
f73314c4ecd75e63641beaff72860c0d11c12244b1da95f0a363cdd2b047c663  super.img_sparsechunk.7
ccaad539b4444734970077593882a73757acd4c7da08c51702cba8475fd93615  super.img_sparsechunk.8
4e5eb4caab36a3b5b4027dcebf0e5ed5e7fb2986f7c2f2a65aa7aa86cc5c85e0  vbmeta.img
```

## Host tools and reconstruction

The checkout already contained `simg2img` and `avbtool`. The focused host tools were built successfully without rebuilding the ROM:

```sh
source build/envsetup.sh
lunch lineage_odessa-bp4a-userdebug
m -j8 lpunpack lpdump
```

Each sparse chunk describes the complete 9,730,785,280-byte output address space, with data in different ranges. They were therefore overlaid in manifest order by one multi-input `simg2img` invocation, not independently expanded and concatenated:

```sh
PKG=/mnt/lineageos_drive/android/odessa/downloads/ODESSA_RETAIL_RPAS31.Q2_59_17_4_3_9_subsidy_DEFAULT_regulatory_DEFAULT_CFC.xml
TMP=/mnt/lineageos_drive/android/odessa/.local/firmware-vbmeta-rpas31
lineageos/out/host/linux-x86/bin/simg2img \
  "$PKG"/super.img_sparsechunk.{0..8} \
  "$TMP/super.raw"
```

The reconstructed raw image was 9,730,785,280 bytes. Its SHA-256 was `3701414cd149639d6e66089cee83ce20f5245797b63c71b3fd6e25513f82609e`.

## Dynamic metadata

Commands:

```sh
lineageos/out/host/linux-x86/bin/lpdump --slot=0 "$TMP/super.raw"
lineageos/out/host/linux-x86/bin/lpdump --slot=1 "$TMP/super.raw"
```

Slots 0 and 1 reported identical metadata:

- Metadata version: 10.0
- Metadata size: 744 bytes
- Metadata maximum size: 65,536 bytes
- Metadata slot count: 3
- Header flags: none
- Block device: `super`, 9,730,785,280 bytes, first sector 2048
- `mot_dp_group_a`: maximum 4,861,198,336 bytes
- `mot_dp_group_b`: maximum 4,861,198,336 bytes
- All six logical partitions are read-only.

| Logical partition | Size (bytes) | Extent |
| --- | ---: | --- |
| `system_a` | 1,390,448,640 | 2,715,720 sectors at super sector 2,048 |
| `vendor_a` | 594,247,680 | 1,160,640 sectors at super sector 3,051,520 |
| `product_a` | 2,354,642,944 | 4,598,912 sectors at super sector 4,212,736 |
| `system_b` | 169,820,160 | 331,680 sectors at super sector 2,719,744 |
| `vendor_b` | 0 | no extents |
| `product_b` | 0 | no extents |

Group A uses 4,339,339,264 bytes and has 521,859,072 bytes free. Group B uses 169,820,160 bytes and has 4,691,378,176 bytes free.

The metadata count of three is on-disk metadata-copy capacity. This build of `lpdump` accepts only A/B selectors 0 and 1; `--slot=2` correctly failed its `slot_number == 0 || slot_number == 1` check and is not a missing logical slot.

The required logical images were extracted with:

```sh
lineageos/out/host/linux-x86/bin/lpunpack \
  -p system_a -p vendor_a -p product_a \
  "$TMP/super.raw" \
  "$TMP/extracted"
```

Extracted image SHA-256 values:

```text
1c0e38c88c376b428c9a2b41094e3aac6f0aedcfed8041915b29a1a64f40cc15  product_a.img
166498958ba0966a9407f29474c7af27fb7dad3e96ae15cfcb75eef815f73dfd  system_a.img
9cafe9d88554881276c54c85e0f54e2928d4a5cbdf66859ba0eaa56188e9ca78  vendor_a.img
```

## AVB verification

A temporary directory contained `vbmeta.img`, `boot.img`, `dtbo.img`, `recovery.img`, and symlinks from the extracted `_a` images to `product.img`, `system.img`, and `vendor.img`. The exact verification command was:

```sh
lineageos/out/host/linux-x86/bin/avbtool verify_image --image vbmeta.img
```

Result: complete success.

```text
vbmeta: Successfully verified SHA256_RSA2048 vbmeta struct in vbmeta.img
boot: Successfully verified sha256 hash of boot.img for image of 16216064 bytes
dtbo: Successfully verified sha256 hash of dtbo.img for image of 800340 bytes
recovery: Successfully verified sha256 hash of recovery.img for image of 28266496 bytes
product: Successfully verified sha256 hashtree of product.img for image of 2317398016 bytes
system: Successfully verified sha256 hashtree of system.img for image of 1368424448 bytes
vendor: Successfully verified sha256 hashtree of vendor.img for image of 584785920 bytes
```

Top-level vbmeta details:

- Algorithm: SHA256/RSA-2048
- Embedded public-key SHA-1: `fd29248b78aa9d6427e8f569eda90be62b9fa0ee`
- Rollback index: 16 at location 0
- Flags: 0
- AVB release string: `avbtool 1.1.0`
- Product, system, and vendor use SHA-256 dm-verity version 1 hashtrees with 4,096-byte data/hash blocks and two FEC roots.
- Root digests: product `43b2412fc6dae035e457c24499636edfb4f92f86d2edb6b263831cd651f9603a`; system `ecf82be8d8058db19a3712ae0c59da59b810496cc55f050eee63209f9f08bfa4`; vendor `8d7618a7e6a7d305a9681572818cd2a317069a5d20fe673b183afc11358af66c`.
- AVB properties report Android 11 and security patch `2022-09-01`.
- The product fingerprint AVB property says `user/test-keys`, while the package identity and the other partition fingerprints say `user/release-keys`. This metadata inconsistency does not affect the successful signature or hashtree verification but should remain recorded.
- The package information file says A/B updates and full Treble are disabled, but its physical A/B firmware set and liblp A/B dynamic-partition metadata directly contradict those generator fields. Treat those two information-file fields as unreliable rather than as partition-layout evidence.

## Connected-phone comparison

Compared with the previously collected read-only inventory in `docs/phase-0-inventory.md`:

- Physical `super` size matches exactly: 9,730,785,280 bytes.
- Package metadata version 10.0, metadata slot count 3, no header flags, and the six A/B logical partition names match.
- Package group B maximum exactly matches the phone's `mot_dp_group_b`: 4,861,198,336 bytes.
- The phone's group A maximum is 4,864,868,352 bytes, 3,670,016 bytes larger than the package's group A.
- Package `system_a`, `vendor_a`, and `product_a` sizes exactly equal the phone's current `system_b`, `vendor_b`, and `product_b` sizes.
- The phone's current slot-A logical images are smaller than the package `_a` images by 60,538,880 bytes for system, 552,960 bytes for vendor, and 378,777,600 bytes for product.
- Package `_b` contains only a 169,820,160-byte `system_b` and empty vendor/product, whereas the connected phone has all three `_b` images populated. This is expected to differ after dynamic-partition updates/custom-ROM installation and is not evidence that the reconstructed package is inconsistent internally.
- The package baseband equals the phone's reported baseband. The package bootloader identifier is dated 2022-08-18, while the connected phone reported `...-220629`. The installed recovery reports the later Motorola build `RPAS31.Q2-59-17-4-5-5`, and the running Tequila vendor security patch is `2023-01-01`, later than this package's AVB patch `2022-09-01`.

## Cleanup

After successful verification, the generated raw `super` and extracted product/system/vendor images were deleted. The downloaded firmware package and checkout build outputs were retained. All five Android project source repositories remained clean.

No verification blocker remains for this package's vbmeta signature, standalone image hashes, or product/system/vendor hashtrees. Because Motorola Software Fix automatically identified the connected phone and selected this package, it is accepted as the exact-device official stock recovery package. This does not make preemptive flashing appropriate; use it only through the documented recovery procedure when restoration is required.
