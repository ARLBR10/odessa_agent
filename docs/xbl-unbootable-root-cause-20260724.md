# Root Cause: slot activation marks the target slot's XBL unbootable

Date: 2026-07-24

Status: **root cause proven by before/after measurement on hardware.** This
supersedes every earlier root-cause claim for the "No valid operating system
could be found" failure.

## Method

`tools/capture-gpt.sh` was run from Lineage Recovery immediately before
sideloading and again immediately after the install reported
`Install completed with status 0`, without rebooting in between. Both captures
were decoded and diffed on the host with `tools/decode-gpt.py`.

The install ran with source slot A and target slot B.

## Finding

The GPT is **not** corrupted. Every primary and backup header CRC and every
partition entry array CRC is valid in both captures, on every LUN, and no
partition name, start LBA, or end LBA changed. Only attribute bytes changed.

The device's A/B partitions are split across LUNs:

| LUN | contents |
| --- | --- |
| `sdc` | `xbl_a`, `xbl_config_a` |
| `sdd` | `xbl_b`, `xbl_config_b` |
| `sde` | slot A: `boot_a`, `recovery_a`, `dtbo_a`, `vbmeta_a`, `modem_a`, firmware |
| `sdf` | slot B equivalents |
| `sdb` | `super`, `userdata` |
| `sda` | small misc partitions |

The decisive change:

```
sdd  xbl_b          ab 0x00 (-) -> 0x80 (unbootable)
sdd  xbl_config_b   ab 0x00 (-) -> 0x80 (unbootable)
sdf  multiimgoem_b  ab 0x00 (-) -> 0x80 (unbootable)
sdf  multiimgqti_b  ab 0x00 (-) -> 0x80 (unbootable)
```

while every other slot-B partition was correctly activated:

```
sdf  boot_b, recovery_b, dtbo_b, vbmeta_b, abl_b, tz_b, hyp_b, ...
                        ab 0x00 (-) -> 0x3f (active, retry=3)
```

and slot A was correctly deactivated (`0x44 active,successful -> 0x40
successful`). `xbl_a` was left at `0x44 active,successful` and untouched.

So after a fully successful install the phone is told to boot slot B, while
slot B's XBL — the very first image the SoC loads — is flagged **unbootable**,
and slot A's XBL is still flagged active. The bootloader refuses the
contradiction, reports `No valid operating system could be found` with
`OS Fingerprint: N/A`, and collapses to the degraded `slot-count: 1` view with
no enumerable partition map.

## Why it happens

`hardware/qcom-caf/bootctrl/boot_control.cpp` has two functions that write A/B
attributes, and only one of them excludes the UFS boot-LUN partitions.

- `set_active_boot_slot()` iterates `AB_PTN_LIST` and **skips** `xbl`,
  `xbl_config`, `multiimgoem`, and `multiimgqti` when
  `gpt_utils_is_ufs_device()` is true, with the comment "handled differrently
  for ufs devices so ignore them". Slot selection for those is done by
  `gpt_utils_set_xbl_boot_partition()` switching the UFS boot LUN.
- `update_slot_attribute()` iterates the same `AB_PTN_LIST` with **no such
  exclusion**.

`update_engine` calls `IBootControl::setSlotAsUnbootable(target)` at the start
of an install — the recovery log line is `Marking new slot as unbootable` — and
that reaches `update_slot_attribute(slot, ATTR_UNBOOTABLE)`, which marks *every*
slot-B partition unbootable including `xbl_b`. At the end of the install,
`setActiveBootSlot(target)` activates the slot but deliberately skips those four
partitions, so the unbootable bit set at the start is **never cleared**.

The two functions disagree, and the asymmetry strands the target slot.

## This explains every prior observation

- The failure is immediate with no boot animation: the rejection happens in the
  bootloader, before any kernel runs.
- `OS Fingerprint: N/A`: the bootloader never got far enough to read it.
- Reflashing `gpt.bin` "fixes" it, because that resets all attribute bytes.
- It is independent of firmware slot synchronisation, AVB vbmeta flags, and the
  UFS boot LUN — all three were separately disproven, and none of them are
  involved.
- Lineage Recovery booted fine in earlier tests: those slot switches were done
  with `fastboot set_active`, which the Motorola bootloader implements itself
  and which never marks an XBL unbootable.
- The earlier BSG `-2` failure also bricked the phone: `setSlotAsUnbootable` had
  already marked `xbl_b` unbootable, and `setActiveBootSlot` aborted before it
  could do anything else.

## Fix

`update_slot_attribute()` now applies the same UFS exclusion as
`set_active_boot_slot()`. The predicate is factored into one helper,
`ptn_selected_by_ufs_boot_lun()`, used by both, so they cannot drift apart
again.

## Residual uncertainty, stated deliberately

With this fix the target slot's `xbl_b` will be left at `0x00` — neither active
nor unbootable — while `xbl_a` stays `0x44 active,successful`, because the code
now never touches either. That matches the upstream premise that these
partitions are selected by the boot LUN and their GPT attributes are irrelevant.

It has **not** been proven that the Motorola bootloader agrees. If it also
requires the active bit to move to the booting slot's XBL, a further change to
swap those bits will be needed. What is certain is that `0x80 unbootable` on the
slot being activated is wrong under any interpretation, and this is the minimal
change consistent with upstream that removes it.

The next install will show which, and `tools/capture-gpt.sh` now makes that
observable instead of inferred.

## Repository placement problem

The fix lives in `hardware/qcom-caf/bootctrl`, which is an upstream LineageOS
repository (`LineageOS/android_hardware_qcom_bootctrl`, local head
`846dfb0`). It is **not** one of the five tracked project repositories and is
**not** pinned in `manifests/odessa.xml`, so a `repo sync` would discard it and
the build is not reproducible as things stand.

The change is committed locally in that repository and exported to
`patches/hardware-qcom-bootctrl/` in this project so it cannot be lost. Before
this is considered done it must be forked to the user's remote and pinned in
`manifests/odessa.xml`, the same way the kernel fork is handled.

## Trap: the same logic exists twice, and only one copy is compiled

The first fix was applied to `hardware/qcom-caf/bootctrl/boot_control.cpp` and
had **no effect on hardware**. Two installs were burned before this was caught.

That repository contains two copies of the same boot-control implementation:

| File | Built by | In this product's build graph |
| --- | --- | --- |
| `boot_control.cpp` | legacy HIDL `bootctrl_hal_defaults` module | **no** |
| `1.1/libboot_control_qti/libboot_control_qti.cpp` | `libboot_control_qti_defaults`, used by both `android.hardware.boot-service.qti` binaries | **yes** |

Proof from the generated build graph:

```
recovery service objects        : BootControl.o  libboot_control_qti.o  main.o
libboot_control_qti.cpp in ninja: 24 references
bootctrl/boot_control.cpp       :  0 references
```

Both files are now fixed, but only the second one matters for this product.

### How the wasted cycles were misdiagnosed

The running recovery was initially blamed, on the basis that
`ro.build.version.incremental` on the phone read `1784920145` while
`out/build_date.txt` had been refreshed to `1784930461`. That reasoning was
wrong: the rebuilt `recovery.img` also carries `ro.build.date.utc=1784920145`
internally, so the property never distinguished old from new. Do not use build
timestamps to identify which recovery is running.

### Reliable verification instead

Compare the hash of the boot-control service actually running on the phone with
the one inside the image about to be flashed:

```bash
# expected, from the image on the host
unpack recovery.img, then:
sha256sum system/bin/hw/android.hardware.boot-service.qti.recovery

# actual, from the phone in recovery
adb shell sha256sum /system/bin/hw/android.hardware.boot-service.qti.recovery
```

They must match before an install result means anything. For the build that
contained only the dead-code fix this hash was
`e79b61a8080011a8bb8960d2cdaa5215be55eb3b1117883ae01c3fbc68ce7c25`; a build
containing the real fix must differ from it.
