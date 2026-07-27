# Handoff: the boot regression is bisected to one property

Date: 2026-07-25, evening

Read `MEMORY.md` first. This file supersedes `docs/handoff-20260725-bootloop.md`
for everything after the XBL fix. That file's bootloader analysis is still
correct and still worth reading; its "recommended next step" is what produced
the regression described here.

## The one-paragraph version

The bootloader problem stayed fixed all day: no degraded partition table, no
near-brick, installs complete with status 0 and slot switches work. Chasing the
zygote failure, I built an ADB-debuggable ROM so the device could be debugged
live. That build would not boot. Two rounds of image bisection reduced the
difference between a build that reaches the zygote handoff and one that does not
to **exactly one file and two lines**: `ro.adb.secure=0` plus the
`persist.sys.usb.config=adb` that Android's build system auto-adds because of it.
`ro.debuggable` is exonerated. Composing the USB gadget in full Android is what
breaks the boot on this device.

## What is proven

`out/host/linux-x86/bin/ota_extractor` was used to pull `system`, `vendor`,
`boot` and `dtbo` out of each OTA's `payload.bin`, and scratchpad `ext4ls.py`
walked each ext4 image with `debugfs -f` (one directory level per invocation, no
mounting, no root).

Comparing the **bisect build** against **TRY2**
(`lineage-23.2-20260724-GPTFIX-TRY2-UNOFFICIAL-odessa.zip`, the last build known
to reach the zygote handoff):

- `boot.img` byte-identical: `9edfc27c2a9472b9…`
- `dtbo.img` byte-identical: `8d80708752b4bcc2…`
- `system`: 7161 entries on both, **zero path differences**, zero mode or size
  differences except one file
- the one file is `/system/system_ext/etc/build.prop`, and its only functional
  change is:

```
- ro.adb.secure=1
+ ro.adb.secure=0
+ persist.sys.usb.config=adb      # Auto-added by post_process_props.py
```

`/system/build.prop` differs only in build timestamps.

`ro.adb.secure=0` does nothing at boot except waive ADB authentication. The
functional change is therefore `persist.sys.usb.config=adb`.

### Why that property is special on this device

`system/core/rootdir/init.usb.rc:109` is
`on boot && property:persist.sys.usb.config=*` -> `setprop sys.usb.config
${persist.sys.usb.config}`. `build/make/tools/post_process_props.py`
(`mangle_build_prop`) adds `persist.sys.usb.config=adb` **only when
`ro.adb.secure == "0"`**, and nothing else in the build sets it. LineageOS sets
`ro.adb.secure=1` for every variant except `eng` and except when
`WITH_ADB_INSECURE` is defined (`vendor/lineage/config/common.mk`).

So on every LineageOS build this project has ever produced, the property was
unset, the trigger never fired, `sys.usb.config` was never set, and **the USB
gadget was never composed in full Android**. The gadget *infrastructure* is
created in `on init` by `init.mmi.usb.rc` regardless; the only thing
`sys.usb.config=adb` adds is binding the controller
(`write /config/usb_gadget/g1/UDC ${sys.usb.controller}`).

This device has a long DWC3 failure history — see the 2026-07-22 entries in
`MEMORY.md` ending in `usb: dwc3: Restore Qualcomm gadget integration`, and the
current kernel HEAD `5be9b397181c usb: dwc3: Drop suspended-event path
incompatible with Qualcomm glue`. Recovery composes an adb gadget successfully on
this same kernel, so the failure is specific to the full-Android path, not to
DWC3 in general.

## Current device state

- Both slots now hold LineageOS. **There is no stock firmware on either slot.**
  The user accepted this explicitly. Recovery path is bootloader fastboot plus
  the official `RPAS31.Q2-59-17-4-3-9` package; from a degraded bootloader,
  `fastboot flash bootloader bootloader.img` (unsuffixed) restores the partition
  view without a full Rescue.
- The bisect OTA was sideloaded successfully (`Total xfer: 1.00x`) and the device
  now **bootloops roughly every 3 seconds**.
- The other slot holds TRY2, which bootloops but holds the logo much longer
  (~25 s of runtime was measured for the earlier debug build; TRY2 was described
  as "way longer" but was never timed — **get that number**).
- Bootloader health is good: `slot-count: 2`, `has-slot:boot: yes`,
  `securestate: flashing_unlocked`, battery ~4.4 V. Recovery boots and has ADB on
  both slots. `fastboot set_active a|b` re-arms either slot.
- `adb root` works in recovery on builds with `ro.debuggable=1`.

## Repository state

Committed and pushed:

- `hardware/qcom-caf/bootctrl` `6024c108fc43286e09b4d63b7c620ed8ef0a5903`,
  pushed to `https://github.com/ARLBR10/android_hardware_qcom_bootctrl.git`
  branch `lineage-23.2`. `manifests/odessa.xml` is pinned to it (tracked file is
  symlinked from `lineageos/.repo/local_manifests/odessa.xml`).

Committed, not pushed:

- `device/motorola/sm6150-common` `f64cb3e5` — the XBL soong config flag.

**Uncommitted, and both are temporary bring-up hacks that must be reverted:**

- `device/motorola/sm6150-common/properties.mk`: `zygote.critical_window.minute=10`
  commented out, so a failing zygote no longer reboots the device.
- `device/motorola/sm6150-common/common.mk`: `PRODUCT_NOT_DEBUGGABLE_IN_USERDEBUG := true`
  re-asserted at the top, to hold `ro.debuggable=0` while `WITH_ADB_INSECURE=true`
  supplies `ro.adb.secure=0`. **This is the bisect harness, not a fix.**

Builds require `WITH_ADB_INSECURE=true` in the environment to reproduce the
current artifacts. Without it you get a normal (non-debuggable) build.

## Recommended next steps

The goal has not changed: get a live `logcat`/`dmesg` off a failing boot. The new
constraint is that the obvious way to do that is itself what breaks the boot.

1. **Confirm the bisection on hardware by reverting only the USB property.**
   Build with neither `WITH_ADB_INSECURE` nor the `common.mk` line and verify the
   result boots like TRY2. That closes the loop; everything above is host-side
   image analysis.
2. **Then attack the real bug**, which is now well-scoped: DWC3 controller
   binding under full Android. Useful angles:
   - Compare what recovery does at `write .../g1/UDC` against what
     `init.mmi.usb.rc` does in full Android — recovery succeeds on this kernel.
   - Consider composing a minimal adb-only gadget in full Android rather than
     Motorola's fuller composition (two gadgets, diag FunctionFS, vendor USB HAL).
   - The kernel already carries local DWC3 changes; check whether
     `5be9b397181c` interacts with the full-Android path.
3. **Alternative observability that does not need USB**, since that path is now
   known-hostile: `androidboot.init_fatal_panic=true` on the kernel cmdline makes
   init panic instead of rebooting, which may populate the pstore dump zone.
   Untested — see the ramoops warning below.

## Eliminated. Do not redo these

- **Firmware/slot asymmetry.** The same build fails identically on both slots.
  `docs/firmware-slot-comparison-20260719.md`'s 16-of-19 differing firmware
  partitions are not the cause.
- **`super` / dynamic partitions.** From fastbootd: `is-logical:system_a|b: yes`,
  `partition-size:system_a` = `system_b` = `0xAA6D5000`, `vendor_b` `0x1FA42000`,
  `product_b` `0x4788B000`. Sizing and metadata are sane on both slots.
- **Virtual A/B / snapshot merge.** Not enabled (`misc_info.txt` has
  `ab_update=true`, `use_dynamic_partitions=true`, no `virtual_ab=true`).
- **Boot image, kernel, ramdisk, cmdline, DTBO.** All byte-identical between the
  working and failing builds.
- **`ro.debuggable`.** Exonerated by the second bisect round.
- **The UFS boot LUN.** `running-boot-lun: 3` was observed with a perfectly
  healthy bootloader. Closed.

## Methodology warnings that cost real time

- **Never compare loose `out/target/product/odessa/*.img` against
  payload-extracted images.** They are stale. This single mistake produced four
  separate false findings in one session: a "changed DTBO", "six missing audio
  HAL libraries", "45 missing vendor entries including every `/rfs/msm/…`
  directory", and "system is 1.76 GB smaller". All four evaporated under
  like-for-like comparison. `MEMORY.md` already warned about this on 2026-07-23
  and the warning was not heeded.
- **Let background extractions finish before stat-ing their output.** One false
  finding came from measuring a file mid-write.
- **Ramoops is unreliable on this device.** `console-ramoops-0` has never
  appeared in any capture. `pmsg-ramoops-0` survives but with heavy bit
  corruption, and a captured buffer may hold the *sideload's* logging rather than
  the boot's. `ramoops: attached 0xbf800@0xaf000000, ecc: 0/0` confirms the region
  is properly reserved, and `CONFIG_PSTORE_CONSOLE=y` is set, so the cause is
  unexplained. Do not build conclusions on pstore absence alone.
- **Get timings from the user with a stopwatch, and define the start point.**
  An eyeballed "about 7 loops in 55 seconds" implied ~8 s cycles and sent the
  investigation toward an early kernel panic; the real figure was ~28 s.
- `/proc/cmdline` on this device contains the serial, Wi-Fi MAC and Bluetooth
  MAC. Redact before sharing or recording.

## Open questions

- **Why did the bisect build's cycle drop to ~3 s** when it is *closer* to TRY2
  than the previous debug build (~28 s)? That is backwards and unexplained. It may
  be an artifact of two bad slots ping-ponging, or of ABL rejecting a slot
  outright. Re-measure carefully before trusting it.
- **TRY2 has never been timed.** Without that number it is unknown whether TRY2
  and the debug builds are two flavours of one late failure or two distinct bugs.
- **The original zygote failure is still unsolved.** TRY2 reaches the end of
  `post-fs-data` with working FBE, then dies at the zygote handoff with no
  `zygote`/`system_server`/`servicemanager` output. That remains the actual
  destination once a boot can be observed live.
