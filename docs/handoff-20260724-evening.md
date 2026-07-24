# Handoff: A/B install succeeds, device still will not boot

Date: 2026-07-24, end of session

Read this with `docs/xbl-unbootable-root-cause-20260724.md`. Read `MEMORY.md`
first as always.

## Where things stand in one paragraph

The LineageOS 23.2 A/B OTA installs perfectly and the slot switch is now
correct, but the Motorola bootloader still refuses to boot the newly activated
slot with `No valid operating system could be found` and `OS Fingerprint: N/A`.
One real bug was found and fixed this session. It was not the whole story.

## What was fixed and verified this session

`update_slot_attribute()` in the QTI boot control marked the target slot's
`xbl`, `xbl_config`, `multiimgoem`, and `multiimgqti` **unbootable** and never
cleared them, because it lacked the UFS boot-LUN exclusion that
`set_active_boot_slot()` has. Fixed in
`ARLBR10/android_hardware_qcom_bootctrl` at
`6863795de5ec856c98244b1e5c3a4cd1f1b9be1c`, pinned in `manifests/odessa.xml`.

Verified on hardware by GPT capture before and after the install. The
post-fix diff is exactly what it should be:

```
xbl_a, xbl_config_a, multiimgoem_a, multiimgqti_a   unchanged (0x04 active)
xbl_b, xbl_config_b, multiimgoem_b, multiimgqti_b   unchanged (0x00)
slot A partitions   0x04 (active)  -> 0x40 (successful)
slot B partitions   0x00 (-)       -> 0x3f (active, retry=3)
Install completed with status 0
```

No GPT corruption at any point: all primary and backup header and entry-array
CRCs valid, no partition name or LBA range ever changed.

## The current open question

After a successful install to slot B the XBL attribute state is:

| partition | attribute |
| --- | --- |
| `xbl_a` | `0x04` active |
| `xbl_b` | `0x00` neither active nor unbootable |

Everything else points at slot B, but the *first image the SoC loads* is still
flagged active on slot A. The fix deliberately stops touching these, on the
upstream premise that the UFS boot LUN selects them and their GPT attributes are
irrelevant. **That premise has not been confirmed for this bootloader.**

Leading hypothesis for the next session: MBM does consult the XBL attribute
bits, and the active bit must move to `xbl_b` — that is, upstream's blanket
"skip on UFS" is wrong for this device, and the correct behaviour is to swap
active/inactive on the XBL pair while never marking either unbootable.

### A second, unexplained observation

Bootloader `getvar` on a **healthy** stock device on slot A reports
`running-boot-lun: 2`. In `gpt-utils`, `BOOT_LUN_A_ID` is 1 and `BOOT_LUN_B_ID`
is 2, and `set_active_boot_slot()` requests `NORMAL_BOOT` (LUN 1) for slot A.
The healthy observed value does not match what the code would set for slot A.
The semantics of `running-boot-lun` were never confirmed, and the value was
identical (`2`) in healthy and failed states, so it has not been shown to matter
— but the mismatch is unexplained and worth resolving before assuming the boot
LUN path is correct.

## Hypotheses already tested and disproven — do not revisit

Each was disproven by direct hardware experiment, not reasoning:

1. **Low-level firmware slot asymmetry.** Stock firmware was flashed to the
   target slot with explicit `_b` suffixes and it booted stock Android 11. The
   subsequent install failed identically. Not the cause. `copy-partitions`
   remains prohibited.
2. **AVB vbmeta flags.** `--flags 3` was restored, confirmed present in the
   built vbmeta, and the failure was unchanged. Not the cause. The flag is kept
   only because it matches upstream sm6150-common.
3. **UFS boot LUN / GPT slot mismatch.** Based on `running-boot-lun: 2` against
   `current-slot: a`. The healthy baseline shows `2` as well. Wrong; corrected
   in place at the top of `docs/boot-lun-slot-mismatch-20260724.md`.
4. **GPT corruption.** Measured directly. All CRCs valid, layout untouched.
5. **BSG versus sg transport, `_GENERIC_KERNEL_HEADERS`, `is_ufs`, kernel
   `WRITE_ATTR` support.** All checked against sources and built binaries.

## Process lessons that cost real hardware cycles

- **There are two copies of the boot-control logic in
  `hardware/qcom-caf/bootctrl`.** `boot_control.cpp` backs the legacy HIDL
  module and is **not compiled** for this product.
  `1.1/libboot_control_qti/libboot_control_qti.cpp` is what the AIDL service
  builds. A fix was applied to the wrong one and two installs were wasted.
  Before trusting that any source change is under test, confirm the file appears
  in `out/soong/build.lineage_odessa.incremental.ninja` and that its object
  exists in the module's intermediates.
- **Do not use build timestamps to identify which recovery is running.**
  `ro.build.date.utc` is identical in old and new `recovery.img` because
  `out/build_date.txt` is not regenerated per incremental build. Compare
  `adb shell sha256sum /system/bin/hw/android.hardware.boot-service.qti.recovery`
  against the same path unpacked from the image being flashed.
- **The boot-control HAL that writes GPT attributes during a sideload is the one
  in the running recovery**, not the one in the OTA payload. Any boot-control
  change must be flashed as a new `recovery` and booted before the install meant
  to test it.
- **Capture the GPT before rebooting.** `tools/capture-gpt.sh` and
  `tools/decode-gpt.py` make the slot-attribute outcome visible while the phone
  is still in recovery, so a bad result costs no reflash. Use them every time.
- Three confident root causes were wrong before measurement settled it. Prefer a
  measurement over a fourth theory.

## Device and recovery procedure

The phone is a Moto G9 Plus `odessa`, `XT2087-1`, bootloader unlocked, UFS with
4096-byte logical blocks. Partition-to-LUN map: `sdc` = `xbl_a`/`xbl_config_a`;
`sdd` = `xbl_b`/`xbl_config_b`; `sde` = slot A; `sdf` = slot B; `sdb` = `super`
and `userdata`; `sda` = small misc.

The user recovers from every failed install with the official
`ODESSA_RETAIL_RPAS31.Q2-59-17-4-3-9` package flashed manually from
`flashfile.xml`. This works reliably and is their established path. Note that
Motorola MBM writes **unsuffixed** `fastboot flash` to the `_a` partitions
regardless of the active slot, so a stock restore refreshes one slot only, and
not necessarily the selected one. Use explicit suffixes when a specific slot
matters.

## Suggested next steps

1. Confirm whether MBM consults XBL attribute bits. The cheapest test is to
   make the XBL pair swap active/inactive with the slot, rebuild the recovery,
   flash it, install, and check the capture before rebooting.
2. If that boots, decide whether the change belongs upstream or as a
   device-specific quirk, and record the reasoning.
3. If it does not boot, the next unexplored evidence is `/sys/fs/pstore/` read
   from recovery after a failed attempt, to establish whether any kernel ever
   ran. Nothing so far proves the failure is not simply that this ROM has never
   booted Android on this hardware; recovery boot is proven, Android boot is
   not.

## State of the repositories

All five project repos plus the new bootctrl fork are committed and pushed.
`manifests/odessa.xml` pins the fork. The uncommitted-changes list is empty
except for untracked local capture artifacts, which are gitignored.
