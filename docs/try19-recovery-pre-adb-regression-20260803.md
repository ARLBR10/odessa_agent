# TRY19 Recovery Pre-ADB Regression

Date: 2026-08-03

## Executive summary

TRY18 was the first Odessa build to reach the visible LineageOS setup wizard.
Its remaining immediately visible defect was that touchscreen input did not work
in either Android or Lineage Recovery.

Runtime inspection of TRY18 Recovery showed that no loadable kernel modules were
present or loaded there. The touchscreen modules and firmware existed only in
the vendor image, while Recovery left `/vendor` empty. TRY19 attempted to fix
that packaging gap by placing the shared sensor dependency, both supported
touchscreen modules, and both variants' firmware into the Recovery ramdisk and
loading the modules from `/lib/modules/modules.load`.

TRY19 no longer reaches Recovery. A normal Recovery request returns to the
bootloader before ADB becomes available. RAM-booting the exact payload-extracted
TRY19 recovery with `fastboot boot` has the same result. This isolates the
regression to the TRY19 recovery image or its early runtime behavior rather than
the installed GPT selection alone.

TRY20 retained the packaged modules and firmware but reduced automatic loading
to only `sensors_class`. It also returns to the bootloader before Recovery ADB,
including when RAM-booted. Therefore it is not yet proven that the Novatek or
Focaltech touchscreen module itself causes the failure. Remaining candidates
include `sensors_class` loading, another consequence of adding `/lib/modules`,
or a recovery image/layout sensitivity caused by the enlarged ramdisk.

## Successful TRY18 baseline

TRY18 OTA:

- Filename at verification time:
  `lineage-23.2-20260802-TRY18-UNOFFICIAL-odessa.zip`
- Size: 1,027,921,315 bytes
- Verified SHA-256 at that time:
  `7bb7d5681027b869aa4f65b91681986677d3fa03e07c81e71972f17cef9eadba`
- Exact payload recovery SHA-256:
  `a03c5601c840a011a84d6d73cf5297ad8fb32b0feda2eafeebce96b3ef461ff9`
- Recovery ramdisk size reported by `unpack_bootimg`: 16,381,451 bytes
- Build incremental: `1785709822`

TRY18 removed the generic
`vendor.lineage.livedisplay-service.sdm` package after hardware logs proved that
neither `IDisplayModes/default` nor `IPictureAdjustment/default` registered on
this device. TRY18 then reached **Welcome to LineageOS**, proving the earlier
SystemServer watchdog loop was resolved.

TRY18 Recovery A also booted and provided ADB. Touch did not work there. Read-only
runtime inspection showed:

- `/proc/modules` was empty.
- `/proc/bus/input/devices` contained only `qpnp_pon` and `gpio-keys`.
- `/sys/class/touchscreen` was absent.
- SPI device `spi2.0` existed but no touchscreen SPI driver was registered.
- Dmesg reported `Unable to open /lib/modules, skipping module loading.`
- Recovery's `/vendor` directory was empty.
- The exact device-tree selection was Novatek:
  - `OF_FULLNAME=/soc/spi@0xa80000/novatek@0`
  - `OF_COMPATIBLE_0=novatek,NVT-ts-spi`
  - `MODALIAS=spi:NVT-ts-spi`

The build output already placed these files in the Android vendor image:

- `/vendor/lib/modules/sensors_class.ko`
- `/vendor/lib/modules/nova_0flash_mmi.ko`
- `/vendor/lib/modules/focaltech_0flash_mmi.ko`
- `/vendor/firmware/novatek_ts_fw.bin`
- `/vendor/firmware/novatek_ts_mp.bin`
- Focaltech firmware and pramboot files

Both touch modules depend on `sensors_class.ko`. Android's Motorola init overlay
also explicitly requests both drivers during `early-init`. Android runtime logs
were unavailable because the successful boot did not expose USB and the bounded
diagnostic is copied only on zygote restart. The Android module-load failure is
therefore not yet independently explained.

## Source changes from TRY18 to TRY19

TRY19 added Recovery-only module packaging in
`device/motorola/odessa/BoardConfig.mk`:

```make
RECOVERY_KERNEL_MODULES := \
    drivers/sensors/sensors_class.ko \
    drivers/input/touchscreen/nova_0flash_mmi/nova_0flash_mmi.ko \
    drivers/input/touchscreen/focaltech_0flash_mmi/focaltech_0flash_mmi.ko

BOARD_RECOVERY_KERNEL_MODULES_LOAD := \
    sensors_class.ko \
    nova_0flash_mmi.ko \
    focaltech_0flash_mmi.ko
```

TRY19 also copied the firmware needed by both supported Odessa panel variants to
Recovery's `/vendor/firmware` in `device/motorola/odessa/device.mk`:

- `FT8006U_Pramboot.bin`
- `focaltech-txd-ft8756-06-0000-odessa.bin`
- `novatek_ts_fw.bin`
- `novatek_ts_mp.bin`

Recovery ueventd searches `/vendor/firmware`, so this destination was deliberate.
No kernel source, DTB, DTBO, boot image, or Android vendor module-load source was
changed between TRY18 and TRY19.

The exact TRY19 recovery ramdisk contained:

```text
/lib/modules/sensors_class.ko
/lib/modules/nova_0flash_mmi.ko
/lib/modules/focaltech_0flash_mmi.ko
/lib/modules/modules.alias
/lib/modules/modules.dep
/lib/modules/modules.load
/lib/modules/modules.softdep
/vendor/firmware/novatek_ts_fw.bin
/vendor/firmware/novatek_ts_mp.bin
/vendor/firmware/focaltech-txd-ft8756-06-0000-odessa.bin
/vendor/firmware/FT8006U_Pramboot.bin
```

TRY19 `modules.load` was:

```text
sensors_class
nova_0flash_mmi
focaltech_0flash_mmi
```

TRY19 `modules.dep` correctly represented both touch dependencies on
`sensors_class.ko`.

## TRY19 artifact verification

TRY19 OTA at verification/install time:

- Filename: `lineage-23.2-20260802-TRY19-UNOFFICIAL-odessa.zip`
- Size: 1,028,303,013 bytes
- SHA-256:
  `65159bc3ece4727cbba2dc59659692d8a59b2e9ab530d1bf96fef96cb34a83d0`
- Exact `payload.bin` size: 1,028,295,719 bytes
- Exact `payload.bin` SHA-256:
  `8b27737207a0221f30652e1ca158951c851173a376cdbd00e8e8747941355f35`
- Exact payload recovery SHA-256:
  `fa8b3d9684dadf6626254c02a01ab746dccd70e899d79f32b4a215bf6f479077`
- Recovery ramdisk size: 16,734,740 bytes
- Build incremental: `1785714291`

ZIP integrity passed. VINTF compatibility passed. Native payload extraction
completed all seven partitions. Boot, DTBO, recovery, vbmeta, and vendor matched
target-files byte-for-byte. Product and system matched after converting the
target-files sparse images to raw images.

The exact payload recovery contained the intended module and firmware files.
Module hashes were:

- `sensors_class.ko`:
  `eb8fea5538b6f9952d747aa3673073873b98d0019339e586b687c848c7d8f1cb`
- `nova_0flash_mmi.ko`:
  `2a6c99d3ff0ec781f486040f913eb54339107f66f9eaec415cb8091c9fb2a770`
- `focaltech_0flash_mmi.ko`:
  `09990c90be32faac400c50a6b75e450b5adc5a34bfafbff231af61531f8d1576`

## TRY19 installation and failure

The exact verified TRY19 OTA was sideloaded with explicit approval from TRY18
Recovery A to inactive slot B.

Update Engine evidence:

- Source slot: A
- Target slot: B
- Recovery install status: 0
- All seven installed partition hashes matched the exact payload.
- Postinstall succeeded.
- Update Engine reported `Update successfully applied, waiting to reboot.`

Immediate post-OTA GPT evidence was healthy and CRC-valid:

- All slot-B non-boot partitions: `0x04`
- `boot_b`: `0x3f`
- All slot-A non-boot partitions: `0x00`
- `boot_a`: `0x3a`

Observed failure:

1. `adb reboot recovery` did not reach TRY19 Recovery B and returned to the
   bootloader.
2. The user flashed stock `gpt.bin`. Bootloader then reported slot B selected,
   both slots bootable, and retry count 7, but selecting/rebooting Recovery still
   returned to bootloader.
3. `fastboot reboot recovery` returned to bootloader.
4. `fastboot boot` of exact payload-extracted TRY19 recovery was accepted and
   printed `Booting OKAY`, but the phone returned to bootloader before Recovery
   ADB appeared.

The RAM-boot result is important: it bypasses normal recovery partition
selection and reproduces the failure with the exact verified image. The stock
GPT intervention complicates later slot evidence but does not explain the
RAM-boot failure.

## TRY20 isolation result

TRY20 retained all three modules and all four firmware files in Recovery but
changed `modules.load` to contain only:

```text
sensors_class
```

TRY20 was preserved on a distinct inode before verification:

- Filename: `lineage-23.2-20260803-TRY20-UNOFFICIAL-odessa.zip`
- Size: 1,028,302,945 bytes
- SHA-256:
  `5b17efc35a42d36b453300ca070998c5859e2fb8d7ef59b074428d571f2d5f83`
- Exact payload SHA-256:
  `d7cc086b534ae394a47e88dd94d7154544c612adcea7d02ad5a7ec3eb2362543`
- Exact payload recovery SHA-256:
  `0a99da4ba6ec263a0d55ee52b358aa15bb985f573c9a2dfc796fc5839856a993`
- Recovery ramdisk size: 16,734,738 bytes
- Build incremental: `1785717790`

TRY20 ZIP integrity, payload properties, all seven target partition comparisons,
module/firmware contents, and VINTF compatibility passed.

RAM-booting exact TRY20 recovery was accepted by fastboot but again returned to
the bootloader before ADB. Because neither touchscreen driver was automatically
loaded, TRY20 disproves the narrow theory that automatic Novatek/Focaltech probe
alone is required for the pre-ADB failure. It does not distinguish between:

- `sensors_class.ko` load failure;
- generic first-stage module-loading behavior after `/lib/modules` is added;
- recovery ramdisk size/layout sensitivity;
- another early failure not retained in available logs.

## Artifact preservation incident

The standard dated output names were hardlinks to the mutable
`lineage_odessa-ota.zip` inode. TRY16, TRY17, TRY18, and TRY19 filenames all shared
inode `38267682`; after TRY19 was built, every name contained TRY19 bytes.

Consequences:

- Recorded hashes and prior extracted evidence remain valid.
- The files named TRY16 through TRY18 are no longer their historical artifacts.
- A later attempt to extract known-good TRY18 actually extracted TRY19.
- This bootloader does not support `fastboot fetch`, so the known-good TRY18
  recovery could not be read back from slot A.

TRY20 was reflink-copied and atomically replaced after build. It now has a
distinct inode and link count 1, so future builds cannot mutate it.

Future artifacts must be checked with `stat` and preserved as distinct inodes
before relying on their filenames.

## Conclusions

Proven:

- TRY18 boots full Android to the LineageOS setup wizard.
- Touch does not work in TRY18 Recovery or Android.
- This phone uses the Novatek `NVT-ts-spi` touchscreen variant.
- TRY18 Recovery lacks touch modules because `/lib/modules` is absent and
  `/vendor` is empty.
- TRY19 correctly packages all intended modules and firmware.
- TRY19 and TRY20 exact recoveries return to bootloader before ADB when
  RAM-booted.
- TRY20 fails without automatically loading either touchscreen driver.

Not yet proven:

- Whether `sensors_class.ko` itself crashes during early loading.
- Whether an empty `modules.load` with the modules merely present boots.
- Whether the enlarged ramdisk crosses a Motorola MBM or kernel decompression
  sensitivity despite remaining within the 64 MiB recovery partition.
- Why Android's existing vendor-side touch module load did not produce touch on
  TRY18.

## Recommended next isolation

Build a recovery-only diagnostic that keeps the module and firmware files but
uses an empty `BOARD_RECOVERY_KERNEL_MODULES_LOAD`. Preserve the artifact on a
distinct inode and RAM-boot its exact payload recovery.

- If it boots, manually insert `sensors_class.ko`, then
  `nova_0flash_mmi.ko`, capturing dmesg after each step. This isolates the exact
  crashing module without another partition write.
- If it still returns to bootloader, remove the packaged modules while retaining
  firmware, or vice versa, to distinguish ramdisk content/size from module-load
  execution.
- Do not sideload another full OTA until a diagnostic Recovery reaches ADB.
- Do not flash another stock GPT during this isolation; RAM boot does not require
  GPT repair.

## Post-report findings

The empty-load-list diagnostic is now prepared in Odessa `BoardConfig.mk`:
all three modules remain packaged, while
`BOARD_RECOVERY_KERNEL_MODULES_LOAD :=` is explicitly empty. The Lineage build
helper should therefore create a zero-byte `/lib/modules/modules.load` without
removing the modules or dependency metadata.

TRY21 is now artifact-verified. Its exact payload Recovery SHA-256 is
`ff352b4f294a8c902c118a954365ffd32ff0767455bd54f24b7abbd824402aac`;
native payload extraction matches target-files byte-for-byte. The exact ramdisk
contains all three modules and valid dependency metadata, with a zero-byte
`modules.load`. ZIP integrity, payload property hashes, and standalone VINTF
checking pass. The named TRY21 ZIP still shares the mutable OTA output inode and
is not preserved across another build.

Hardware RAM-boot of exact TRY21 succeeds and reaches ADB. Manual insertion of
`sensors_class.ko` fails with `Required key not available`; kernel dmesg reports
`PKCS#7 signature not signed with a trusted key`. Thus TRY19/20 were not touch
driver crashes: first-stage init treated a rejected listed module as fatal.

The module is signed by the current KERNEL_OBJ generated key, but the runtime
kernel contains an older generated key. `certs/system_certificates.S` embeds the
certificate through `.incbin`, whose bytes were absent from the sccache key. A
stale cached `system_certificates.o` therefore produced the mismatched trust
store. Kernel `certs/Makefile` now adds the generated certificate SHA-256 to the
assembly command key. This retains `CONFIG_MODULE_SIG_FORCE=y`; it does not
weaken module authentication. TRY22 hardware confirms the fix: its runtime key
matches the current certificate and both `sensors_class.ko` and
`nova_0flash_mmi.ko` insert successfully.

The extracted `novatek_ts_fw.bin` and `novatek_ts_mp.bin` are byte-identical
139,264-byte files, both with SHA-256
`d9d1f5e88dc0fa90fdd64437e39adac7bf72ad70a8335e339cdb325cec2dab38`.
`file(1)` misleadingly classified them as aria2 control records. TRY22 hardware
disproved the resulting invalid-firmware hypothesis: the Novatek driver parsed
the runtime file into 15 partitions, downloaded it successfully in 84 ms, and
read firmware version 3 / PID `601F`. It registers IRQ 249, input `event2`, and
`/sys/class/touchscreen/NVT-ts`. The identical runtime/MP payloads remain a
provenance oddity but are not the active touch blocker; final UI touch validation
subsequently passed. Recovery touch worked normally after manually inserting
`sensors_class.ko` and `nova_0flash_mmi.ko` on TRY22.

TRY22 intentionally used an empty `modules.load`, so the working touch state did
not persist across reboot. The next candidate restores automatic Recovery loading
in dependency order: `sensors_class`, Novatek, then Focaltech. Both touch variants
remain packaged for regional Odessa hardware. Android's existing vendor init
scripts already request the same dependency and touch modules; the corrected
kernel certificate is therefore expected to fix Android touch as well.

No broad SELinux bypass, permissive mode, verified-boot weakening, raw partition
write, or identity/calibration partition access is justified by this failure.
