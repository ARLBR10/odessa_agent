# Phase 0 Device Inventory

Collected read-only from the connected phone on 2026-07-18. No serial number, IMEI/MEID, phone number, account, network credential, Bluetooth address, token, partition content, or calibration content is recorded here.

## Android state

- Product/device: `odessa`
- Model: Motorola g(9) plus
- SKU: `XT2087-1`
- Android build: TequilaOS-derived Android 14, SDK 34
- Build fingerprint: `motorola/tequila_odessa/odessa:14/UQ1A.240105.004.A1/24010712:user/release-keys`
- Framework security patch: `2024-01-05`
- Vendor security patch: `2023-01-01`
- First API level: 29
- VNDK: 34
- Kernel: `4.14.190-Amber`
- Bootloader: `MBM-3.0-odessa_retail-e69c40c38d6-220629`
- Baseband: `M7150_22.31.04.72R` on both reported modem instances
- Active slot: `_a`
- Dynamic partitions: enabled
- Encryption: file-based encryption, state `encrypted`
- Android reported verified boot `green` and vbmeta device state `locked`; direct bootloader fastboot reported `securestate: flashing_unlocked`, which remains the authoritative unlock observation.
- Magisk overlays are present. TequilaOS remains a rooted behavioral reference only.

## Physical layout

The readable `/dev/block/by-name` map confirms A/B copies of bootloader, firmware, boot, DTBO, recovery, and vbmeta partitions, plus a shared dynamic `super` partition and `userdata`.

Observed A/B partition families:

`abl`, `aop`, `bluetooth`, `boot`, `cmnlib`, `cmnlib64`, `devcfg`, `dsp`, `dtbo`, `fsg`, `hyp`, `keymaster`, `logo`, `modem`, `multiimgoem`, `multiimgqti`, `prov`, `qupfw`, `recovery`, `storsec`, `tz`, `uefisecapp`, `vbmeta`, `xbl`, and `xbl_config`.

Observed shared partitions include:

`apdp`, `carrier`, `cid`, `ddr`, `devinfo`, `dhob`, `frp`, `fsc`, `hw`, `keystore`, `kpan`, `logfs`, `metadata`, `misc`, `modemst1`, `modemst2`, `persist`, `prodpersist`, `sp`, `spunvm`, `ssd`, `super`, `uefivarstore`, `userdata`, `utags`, and `utagsBackup`.

Identity/calibration-sensitive partitions including `persist`, `modemst1`, `modemst2`, `fsg`, `cid`, `utags`, and related storage were listed by name only. They were not read or copied.

Android SELinux/sysfs permissions prevented querying physical partition sizes. This was recorded rather than bypassed. Bootloader fastboot independently reported:

- `super`: `0x244000000`, 9,730,785,280 bytes
- Slot count: 2
- Current slot: `a`

## Dynamic partitions

`lpdump` succeeded without root. Metadata version is 10.0 with three metadata slots and no header flags.

| Logical partition | Size (bytes) |
| --- | ---: |
| `system_a` | 1,329,909,760 |
| `vendor_a` | 593,694,720 |
| `product_a` | 1,975,865,344 |
| `system_b` | 1,390,448,640 |
| `vendor_b` | 594,247,680 |
| `product_b` | 2,354,642,944 |

Metadata groups:

- `mot_dp_group_a`: maximum 4,864,868,352 bytes
- `mot_dp_group_b`: maximum 4,861,198,336 bytes

Fastbootd independently reported `system_a`, `vendor_a`, and `product_a` as logical and returned the same slot-A sizes.

## Boot modes

Bootloader fastboot:

- Product `odessa`
- Current slot `a`
- Slot count 2
- `is-userspace: no`
- `securestate: flashing_unlocked`
- Motorola does not implement the generic `getvar unlocked` variable.

Fastbootd:

- Product `odessa`
- Current slot `a`
- `is-userspace: yes`
- Logical system, vendor, and product partitions visible

Installed custom recovery:

- ADB state `recovery` after the recovery menu's Enable ADB action
- Device `odessa`, slot `_a`, dynamic partitions enabled
- Build fingerprint `motorola/odessa_retail/odessa:11/RPAS31.Q2-59-17-4-5-5/af8e3:user/release-keys`
- Display ID `TQ3A.230901.001`
- Kernel `4.14.190-perf+`
- No Lineage Recovery, TWRP, or OrangeFox version property was exposed
- Recovery returned to TequilaOS successfully; Android reported `sys.boot_completed=1`

## Remaining baseline work

Hardware feature declarations confirm camera, fingerprint, NFC, GNSS, cellular/IMS, Wi-Fi, Bluetooth, audio, and the expected sensor classes are advertised. Advertisement is not proof of function. Physical behavior remains to be recorded in `docs/tequilaos-hardware-baseline.md`.
