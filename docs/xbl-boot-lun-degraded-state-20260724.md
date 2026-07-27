# The degraded state measured: ABL boots `xbl_b` and enumerates no partitions

Date: 2026-07-24, night

This supersedes the framing in `docs/handoff-20260724-evening.md`. That handoff's
leading hypothesis was that MBM reads the XBL GPT attribute bits. The measurement
below shows the relevant variable is not the attribute bits but **which physical
XBL the SoC boots**, and that the OTA install moves it.

## Method

The phone was left in the post-failed-install state and queried with bootloader
`fastboot getvar` only. No partition was written, erased, or booted. Device-unique
values (USB serial, `uid`, `battid`, `pcb-part-no`) were deliberately not recorded.

## What the degraded state actually is

ABL is alive and correct for this device — it answers fastboot, drives the
display, and reports `MBM-3.0-odessa_retail-e69c40c38d6-220818`, which is the
RPAS31 bootloader. What it does not have is a partition table.

```
slot-count: 1                       has-slot:boot: no
current-slot: b                     slot-suffixes: not found
running-bl-slot: unknown/_b         slot-successful:_a / _b: unknown
running-boot-lun: 3                 slot-unbootable:_a / _b: unknown
securestate: flashing_unlocked      slot-retry-count:_a / _b: unknown
logical-block-size: 0x1000          is-userspace: no
```

Every `partition-size:` query returns empty — `boot`, `boot_a`, `boot_b`,
`recovery`, `super`, `userdata`, `modem`, `abl`, `gpt`, `partition`, and even
`xbl`, `xbl_a`, `xbl_b`. Zero partitions are enumerated.

So `Invalid partition name boot_a` on a flash attempt is not a slot-suffix
problem. ABL has no storage view at all. This is also why the Motorola Rescue
still works: `flashfile.xml` uses only unsuffixed partition names, which MBM
special-cases.

## `running-boot-lun` resolved

| state | `current-slot` | `running-boot-lun` |
| --- | --- | --- |
| healthy, restored stock | `a` | **2** |
| post-failed-install | `b` | **3** |

LUN 2 is `sdc` = `xbl_a`/`xbl_config_a`; LUN 3 is `sdd` = `xbl_b`/`xbl_config_b`.
`running-boot-lun` therefore reports the **UFS LUN index**, not `bBootLunEn`, and
the A/B mapping is exactly as expected.

Two consequences:

1. The "unexplained `running-boot-lun: 2` on a healthy slot-A device" recorded in
   `docs/handoff-20260724-evening.md` and `MEMORY.md` is **not an anomaly**. Close
   that question.
2. `set_boot_lun()` **works**. The install genuinely moved the SoC's XBL source
   from `xbl_a` to `xbl_b`. It is not silently failing, and the BSG-versus-sg
   transport work was not wasted — it just was not the bug either.

## Why every slot-B test passed and every OTA failed

Every kernel-bisection and recovery test on slot B used `fastboot set_active b`.
MBM implements that itself and evidently flips **GPT attributes only**, leaving
the boot LUN at 2. Those tests therefore kept booting the known-good `xbl_a` the
whole time, which is why the whole 4.14.190 → 4.14.336 bisection validated
cleanly on slot B.

The A/B OTA path is the only thing that has ever called
`gpt_utils_set_xbl_boot_partition()` and moved the SoC onto `xbl_b`. Every one of
those attempts died. One path works, the other does not, and that is the
difference between them.

**Booting from `xbl_b` is the failure.** The XBL-unbootable fix in
`ARLBR10/android_hardware_qcom_bootctrl` `6863795d` remains a real bug fix that is
confirmed working on hardware; it simply was not this bug.

## Why `xbl_b` may never have been refreshed

`bootloader.img` in the official RPAS31 package is a `SINGLE_N_LONELY` container.
Its recipe (`bootloader.default.xml`) flashes fourteen **unsuffixed** partitions:

```
cmnlib  cmnlib64  keymaster  hyp  tz  devcfg  storsec
uefisecapp  prov  aop  abl  qupfw  xbl_config  xbl
```

Combined with the recorded Motorola quirk that unsuffixed `fastboot flash` writes
to `_a` regardless of the active slot, **every stock restore performed in this
project refreshed slot A's low-level firmware and never touched slot B's.** The
2026-07-19 read-only comparison already found `xbl` and `xbl_config` differing
between the slots.

## The two remaining candidates

**(A) `xbl_b` / `xbl_config_b` content is stale or bad.** Supported by the
restore-path analysis above and the 2026-07-19 hash difference.

**(B) Switching the boot LUN at all is wrong on this device.** MBM's own
`set_active` does not do it; LineageOS OTAs never update `xbl`; pinning the SoC to
`xbl_a` permanently would be harmless.

These are separable by a free, read-only measurement on a freshly restored device
— see "Next steps" in `MEMORY.md`. Do not guess between them; three confident root
causes have already been wrong in this investigation.
