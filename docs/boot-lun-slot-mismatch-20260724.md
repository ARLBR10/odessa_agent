# UFS Boot LUN / GPT Slot Mismatch

Date: 2026-07-24

> **CORRECTED 2026-07-24, same day.** The central claim of this document — that
> `running-boot-lun: 2` against `current-slot: a` is a mismatch and the cause of
> the failure — is **wrong**. The healthy-state baseline was captured on a
> restored, booting stock device and reads:
>
> ```
> current-slot: a   running-bl-slot: _a/_a   running-boot-lun: 2   slot-count: 2
> ```
>
> `running-boot-lun: 2` is the **normal** value for this device on slot A, and it
> is identical in the healthy and failed states. The boot LUN is therefore not
> the discriminator, `set_boot_lun()` is not proven broken, and the "split boot
> chain" reading below is not supported.
>
> What actually differs between healthy and failed is only:
>
> | | healthy | failed |
> | --- | --- | --- |
> | `running-bl-slot` | `_a/_a` | `unknown/_a` |
> | `slot-count` | 2 | 1 |
> | `partition-size:boot_a` / `boot_b` / `super` | correct sizes | **empty** |
>
> MBM cannot read the partition table after a failed install, and consequently
> cannot identify its own bootloader slot. The remaining sections' *eliminations*
> are still valid and were verified against the sources and built binaries; the
> *conclusion* is not. See the "Current state" section at the end.

This is the first inspection of the phone in the **post-failure state**, before
any stock restore. Previous episodes were restored immediately, which destroyed
this evidence. It supersedes the earlier root-cause analyses.

## The observation

`fastboot getvar all` in Motorola AP Fastboot Flash Mode, immediately after the
failed boot, with nothing reflashed (identifiers redacted):

```
current-slot:      a
running-boot-lun:  2
running-bl-slot:   unknown/_a
slot-count:        1
slot-successful:_a / _b:   unknown
slot-unbootable:_a / _b:   unknown
slot-retry-count:_a / _b:  unknown
logical-block-size: 0x1000
storage-type:      UFS
ufs:               128GB SAMSUNG KM5V7001DM-B621 FV=0800 WB=0
hwrev:             PVT
verity-state:      enforcing (0)
securestate:       flashing_unlocked
```

`partition-size:boot_a`, `partition-size:boot_b`, and `partition-size:super`
return **empty**: MBM cannot enumerate the physical partition map.

The GPT slot attributes say the active slot is **A**. The UFS boot LUN is still
**B** (`BOOT_LUN_A_ID` is 1 and `BOOT_LUN_B_ID` is 2 in QTI `gpt-utils`). The
device booted its XBL from slot B while the GPT points every other partition at
slot A. MBM reports `running-bl-slot: unknown/_a`, degrades to `slot-count: 1`,
and stops enumerating partitions. That degraded view is exactly the "near-brick"
signature recorded on 2026-07-24 and in earlier episodes, and it is why the user
must reflash `gpt.bin` and the full stock package to recover.

## Why this is the failure

`hardware/qcom-caf/bootctrl/boot_control.cpp` `set_active_boot_slot()`:

1. Builds the A/B partition list, skipping `xbl`, `xbl_cfg`, `multiimgoem`, and
   `multiimgqti` when `gpt_utils_is_ufs_device()` is true.
2. Calls `boot_ctl_set_active_slot_for_partitions()`, which rewrites the GPT
   attribute bits. **This happens first and succeeded.**
3. Then, for UFS, calls `gpt_utils_set_xbl_boot_partition(NORMAL_BOOT)` for slot
   A or `(BACKUP_BOOT)` for slot B, which resolves the SCSI generic node and
   calls `set_boot_lun()`.
4. Returns `-1` if step 3 fails, otherwise 0.

`update_engine` logged no `SetActiveBootSlot` error, so the code believed step 3
succeeded. The bootloader says the boot LUN did not change. Steps 2 and 3 are not
atomic, so a step-3 failure — real or silent — always leaves the split boot chain
observed above.

## Eliminated during this investigation

All checked on the host against the exact sources and the exact built binaries:

- **BSG versus sg transport.** The sg implementation is compiled in. The built
  `android.hardware.boot-service.qti.recovery` contains
  `%s: UFS query ioctl failed(%s)` and `/sys/block/%s/device/scsi_generic`, and
  contains no `ufs-bsg` strings. `QTI_GPT_UTILS.USE_BSG_FRAMEWORK := false` is
  in effect.
- **The `_GENERIC_KERNEL_HEADERS` stub.** `recovery-ufs-bsg.cpp` contains a
  `#else return 0;` branch that would make `set_boot_lun()` a silent no-op
  returning success. `_GENERIC_KERNEL_HEADERS` appears **zero** times in
  `out/soong/build.lineage_odessa.incremental.ninja`, and the real ioctl strings
  are present in the binary, so this branch is not compiled. It remains a trap
  worth re-checking if build flags change.
- **`is_ufs` being false.** `gpt_utils_is_ufs_device()` tests `ro.boot.bootdevice`
  for a `.ufshc` suffix. The recovery log shows
  `ro.boot.bootdevice=1d84000.ufshc`, so the UFS branch does run.
- **Kernel support for the write.** `drivers/scsi/ufs/ufshcd.c` registers
  `.ioctl = ufshcd_ioctl`, handles `UFS_IOCTL_QUERY`, and
  `ufshcd_query_ioctl()` accepts `UPIU_QUERY_OPCODE_WRITE_ATTR` with
  `QUERY_ATTR_IDN_BOOT_LU_EN`, validating `att` against
  `QUERY_ATTR_IDN_BOOT_LU_EN_MAX`. The userspace side memsets the request and
  writes `buffer[0] = boot_lun_id`, which the kernel reads back as a
  little-endian `u32`. The contract is consistent.
- **vbmeta AVB flags.** See `docs/avb-vbmeta-flags-boot-failure-20260724.md`;
  disproven by direct experiment.
- **Low-level firmware slot asymmetry.** Disproven by direct experiment; the
  target slot held freshly flashed stock firmware.

## Corrections to earlier records

- The 2026-07-24 entry "install failure root cause: UFS BSG vs sg boot-LUN
  transport" concluded that compiling the sg transport would fix slot
  activation. It did not. The sg transport is confirmed active in the binary and
  the boot LUN still does not change. That entry's *diagnosis* of BSG being
  unusable on this kernel stands; its *conclusion* that this was the whole
  install failure does not.
- The earlier statement that the AIDL BootControl migration plus BSG=false
  "validated" slot activation is wrong. What is validated is that the call now
  returns success. Success is not the same as the boot LUN changing.

## The one remaining gap

There is **no healthy-state baseline** for `running-boot-lun` and
`running-bl-slot`. Without it, the possibility that `running-boot-lun: 2` is
normal on this device cannot be formally excluded, even though
`running-bl-slot: unknown/_a` and the degraded partition map strongly indicate a
detected inconsistency.

Closing that gap is zero-risk and must be done before any further code change:

1. Restore stock by the user's established flashfile procedure.
2. Let stock Android boot and confirm it is healthy.
3. Reboot to the bootloader and run `fastboot getvar all`.
4. Record `running-boot-lun`, `running-bl-slot`, `slot-count`, and
   `current-slot` for a known-good slot-A device.

Expected if the diagnosis is correct: `running-boot-lun: 1`,
`running-bl-slot: _a/_a`, `slot-count: 2`.

## Notes for whatever comes next

- This 4.14 tree exposes no UFS sysfs attribute for the boot LUN; there is no
  `ufs-sysfs.c` and no `boot_lun` symbol in `drivers/scsi/ufs/*.c`. Reading the
  attribute at runtime requires a small `UPIU_QUERY_OPCODE_READ_ATTR` helper,
  which the kernel does support. That would let the boot LUN be observed
  directly before and after a slot switch instead of inferred from the
  bootloader.
- Manual `fastboot set_active` to repair the mismatch remains prohibited by
  `AGENTS.md` and by the earlier recorded decision, and has not been attempted.
  If it is ever reconsidered, it needs an explicit decision from the user, not an
  exploratory attempt.
- Do not re-run an OTA install until the boot LUN switch is either proven to work
  or replaced. Each attempt reproduces the split boot chain and forces a full
  stock reflash.

## Current state after the correction

Confirmed directly on the restored device in Motorola bootloader fastboot:

```
current-slot: a          running-bl-slot: _a/_a    running-boot-lun: 2
slot-count: 2            logical-block-size: 0x1000
partition-size:boot_a  0x0000000004000000
partition-size:boot_b  0x0000000004000000
partition-size:xbl_a   0x0000000000400000
partition-size:super   0x0000000244000000
```

So the failure signature reduces to one fact: **after a successful OTA install,
MBM can no longer read the partition table.** Everything else follows from that.

### What is still standing

- The install itself is complete and correct: all payload operations applied,
  every target partition hash-verified, `Install completed with status 0`.
- The slot-activation call returns success.
- The eliminations recorded above (BSG versus sg, `_GENERIC_KERNEL_HEADERS`,
  `is_ufs`, kernel `WRITE_ATTR` support, AVB flags, firmware slot asymmetry) all
  hold; they were verified against sources and built binaries, not inferred from
  the boot-LUN reading.

### The remaining suspect

`set_active_boot_slot()` calls `boot_ctl_set_active_slot_for_partitions()`,
which uses `gpt_disk_get_disk_info()`, `gpt_disk_update_crc()`, and
`gpt_disk_commit()`. `gpt_disk_commit()` rewrites **all four** GPT structures on
every call: primary header, primary partition entry array, secondary header, and
secondary partition entry array. Any offset or size error there corrupts the
partition table on both copies at once, which matches the observed symptom and
matches why recovery requires reflashing `gpt.bin`.

This device uses `logical-block-size: 0x1000` (4096 bytes). The code obtains the
block size via `ioctl(fd, BLKSSZGET, ...)` rather than assuming 512, so it is
block-size aware in principle. Whether every offset computation in
`gpt_get_header`, `gpt_set_header`, `gpt_get_pentry_arr`, and
`gpt_set_pentry_arr` is correct for 4 KiB logical blocks has **not** been
verified and must not be assumed either way.

**This is a suspect, not a conclusion.** Two confident root causes have already
been wrong today. The next step is measurement, not another code reading.

### Planned measurement

Isolate the single suspect operation, with no OTA involved, so the phone keeps
bootable stock on slot A throughout:

1. Build the AOSP `bootctl` tool (`system/extras/bootctl` exists in the tree). It
   drives the AIDL boot HAL that already runs in Lineage Recovery.
2. Flash Lineage Recovery to **both** slots with explicit `_a`/`_b` suffixes, so
   recovery stays reachable whichever slot ends up active.
3. From recovery ADB, capture the GPT **read only**: the header blocks and
   partition entry arrays of each `/dev/block/sd?`. This is partition metadata
   only — names, GUIDs, offsets, attributes — not user data, and no identity or
   calibration partition content.
4. Run `bootctl set-active-boot-slot <other>` and nothing else.
5. Capture the GPT again, then reboot to the bootloader and check whether MBM
   still enumerates partitions.
6. Diff the two captures on the host.

If the GPT is damaged by the slot switch alone, that is proof and the diff shows
exactly which bytes moved. If the GPT is intact, the corruption comes from
something else in the OTA and the search moves there.

Step 4 deliberately performs the suspected-destructive operation. It requires
explicit user approval. The fallback is the user's established flashfile restore.
