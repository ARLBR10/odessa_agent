# AVB vbmeta Flags Boot Failure

Date: 2026-07-24

Symptom: a LineageOS 23.2 A/B OTA installs and verifies completely, reports
`Install completed with status 0`, switches slots, and then the Motorola
bootloader refuses to boot with `No valid operating system could be found` and
`OS Fingerprint: N/A`. The failure is immediate; there is no boot animation and
no repeated attempt.

## What was installed

- OTA: `lineageos/out/target/product/odessa/lineage-23.2-20260724-UNOFFICIAL-odessa.zip`
- Size: 1,028,460,442 bytes
- SHA-256: `4e4944d0f69480e47b46fffcb7e645a4654e4553e04bd63709116802c89f428a`
- Metadata: `ota-type=AB`, `pre-device=odessa`, `post-sdk-level=36`,
  `post-security-patch-level=2026-07-01`,
  `post-build=motorola/odessa_retail/odessa:11/RPAS31.Q2-59-17-4-5-5/af8e3:user/release-keys`

The user wiped before installing, sideloaded from Lineage Recovery running on
slot B, declined the recovery prompt about an additional package, and pulled
`/tmp/recovery.log` before rebooting.

## The install itself succeeded

From the pulled recovery log (untracked project-root `recovery.log`, 1331
lines, captured 2026-07-24 15:46; it contains device identifiers and must not be
committed or shared unredacted):

- `Using AIDL version of IBootControl`; `Loaded boot control hal.`
- `source_slot: B`, `target_slot: A`, `switch_slot_on_reboot: true`
- Dynamic partition metadata created from slot B and copied to slot A in `super`
- `boot_a`, `dtbo_a`, `recovery_a`, and `vbmeta_a` all hash-verified
- `DownloadAction`, `FilesystemVerifierAction`, and `PostinstallRunnerAction` all
  finished with `ErrorCode::kSuccess`
- `Update successfully applied, waiting to reboot.`
- `Install completed with status 0.`

There is **no** `SetActiveBootSlot` error line. update_engine logs that call only
on failure, so its absence means the slot activation succeeded.

This closes the failure class recorded in "2026-07-24 OTA slot-activation
failure and UFS BSG fix" and "2026-07-24 install failure root cause: UFS BSG vs
sg boot-LUN transport". The AIDL BootControl migration and the
`USE_BSG_FRAMEWORK := false` transport fix work. Payload application,
verification, dynamic partitions, postinstall, and slot activation are all
proven on hardware.

The nonfatal `otapreopt_script: Error: boot-complete not detected.` and
`Skip FinishedSnapshotWrites() because /metadata is not mounted` messages are
expected for a recovery sideload and are unrelated.

## Firmware slot asymmetry is not the cause

The open gate in `docs/first-install-checkpoint.md` and
`docs/firmware-slot-comparison-20260719.md` was that low-level firmware differs
between slots and the OTA does not ship it. That hypothesis is now eliminated by
direct experiment.

The user set slot B active and flashed the official
`ODESSA_RETAIL_RPAS31.Q2-59-17-4-3-9` package, then explicitly flashed
`bootloader`, `radio`, `bluetooth`, `dsp`, and `logo` to the `_b` suffixed
partitions. Slot B then booted stock Android 11. The subsequent OTA targeted
slot A, which also held freshly flashed stock firmware, and failed identically
and immediately.

Fresh, current, self-consistent low-level firmware on the target slot does not
change the symptom.

## Motorola MBM slot-suffix quirk

The user observed that unsuffixed `fastboot flash <partition>` commands from
Motorola `AP Fastboot Flash Mode (Secure)` wrote to the `_a` partitions even
while slot B was the active slot. Both the stock `flashfile.xml` and
`servicefile.xml` for this package use only unsuffixed partition names, so a
stock restore refreshes one slot only, and not necessarily the active one.

Consequence: never assume a stock restore updated the slot you selected. Flash
explicit `_a`/`_b` suffixes when a specific slot is required, and re-verify.

## Root cause candidate: vbmeta AVB flags

`No valid operating system could be found` with `OS Fingerprint: N/A` means ABL
rejected the slot before reading the fingerprint, which is stored as an AVB
property descriptor inside `vbmeta`.

HOST ONLY `avbtool info_image` comparison:

| Image | Public key (sha1) | Algorithm | Flags | Rollback index |
| --- | --- | --- | --- | --- |
| Stock `RPAS31.Q2-59-17-4-3-9` (boots) | `fd29248b78aa9d6427e8f569eda90be62b9fa0ee` (Motorola) | SHA256_RSA2048 | 0 | 16 |
| Tequila/Pixys, proven to boot Android on this phone | `2597c218aae470a130f61162feaae70afd97f011` (AOSP test) | SHA256_RSA4096 | **3** | 0 |
| LineageOS 23.2 build (fails) | `2597c218aae470a130f61162feaae70afd97f011` (AOSP test) | SHA256_RSA4096 | **0** | 0 |

The custom ROM that is known to boot Android on this exact hardware uses the
same AOSP test key this project uses, so the signing key is not the
discriminator. The discriminator is the vbmeta flags field. Flags `3` is
`AVB_VBMETA_IMAGE_FLAGS_VERIFICATION_DISABLED | HASHTREE_DISABLED`.

`device/motorola/sm6150-common` commit `31eea31c91705d042af7d74b460e872aebbf4067`
("sm6150-common: Remove stale legacy integration", 2026-07-16) deleted:

```make
BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --flags 3
```

That line was not stale local cruft. It is upstream LineageOS configuration for
this platform, introduced by the LineageOS Motorola SM6150 maintainer in
`8db0b6129ceb90f100aedcdd59f2a51816ea0d30` ("sm6150-common: Simplify AVB flag
logic"). Every hardware install attempt after `31eea31c` has failed in this
manner.

### Unresolved counter-evidence

Flags-0 test-key vbmeta images **did** boot Lineage Recovery repeatedly during
the kernel bisection work. Verified with `avbtool info_image`:
`diagnostic-recovery-4.14.310-boot-test-20260723/vbmeta.img` and
`diagnostic-recovery-4.14.190-20260719/vbmeta.img` both report `Flags: 0`.

So this bootloader tolerates a verification-enabled custom-key vbmeta on the
recovery boot path but apparently not on the normal boot path. The mechanism is
not proven from the host. The rollback index difference (0 against a stored 16,
which produced the expected `0 vs 16` warnings during earlier recovery flashes)
may also contribute. Treat the flags restoration as the leading hypothesis with
strong correlational and upstream-convention support, not as a proven cause,
until a build with flags 3 boots.

## Change applied

`device/motorola/sm6150-common/BoardConfigCommon.mk` restores
`BOARD_AVB_MAKE_VBMETA_IMAGE_ARGS += --flags 3` with a comment recording why.
The change is uncommitted pending a hardware result.

## Security consequence, recorded deliberately

Flags `3` requests that the bootloader skip vbmeta verification and that
dm-verity hashtrees be disabled. This is what official LineageOS sm6150 builds
ship, because the device offers no route to install a custom AVB key, and this
project's charter directs reuse of branch-current LineageOS conventions.

It is still a real reduction relative to stock. It must be carried into Phase 8
as an explicit, documented limitation of any release, and it must not be
described as verified boot. Do not extend it into SELinux permissive,
disabled encryption, or disabled update verification.

## Device state at the time of writing

Read-only Motorola bootloader fastboot queries after the user's stock restore:

- `product: odessa`, `securestate: flashing_unlocked`, `secure: yes`,
  `is-userspace: no`
- `slot-count: 2`, `current-slot: a`
- `boot_a/b`, `recovery_a/b`, `dtbo_a/b`, `xbl_a/b`, `modem_a/b` all enumerate
  with sizes; `super` is 0x244000000 and unslotted
- `slot-unbootable:a: no`, `slot-unbootable:b: no`,
  `slot-retry-count:a: 7`, `slot-retry-count:b: 0`, `slot-successful:b: no`
- `version-bootloader: MBM-3.0-odessa_retail-e69c40c38d6-22...`

This is a healthy bootloader view, unlike the 2026-07-24 near-brick state that
reported `slot-count: 1` and could not enumerate the physical partition map.

Querying `slot-successful:a` reset the USB fastboot session once
(`Status read failed (No such device)`); the device re-enumerated on its own.
Treat that specific variable as unreliable on this bootloader.

## Next steps

1. Rebuild target-files and the OTA with the restored flags. The user runs the
   build; sccache is configured in their shell.
2. Verify the regenerated vbmeta reports `Flags: 3` before flashing anything.
3. Keep a stock, bootable fallback slot. Slot B currently holds full stock
   firmware and booted Android 11.
4. Capture `/tmp/recovery.log` before rebooting, as was done here. It is what
   made this diagnosis possible.
5. If the boot still fails, the next evidence is `/sys/fs/pstore/` read from
   Lineage Recovery after the failed attempt, to separate an ABL-stage rejection
   from a kernel-stage failure.

## Result: hypothesis disproven

The user rebuilt with the restored flags. The regenerated vbmeta reports
`Flags: 3`, key `2597c218aae470a130f61162feaae70afd97f011`, SHA256_RSA4096,
matching the Tequila/Pixys configuration exactly. `dtbo`, `vbmeta`, and
`recovery` were flashed, `lineage-23.2-20260724-FLAGSFIX-UNOFFICIAL-odessa.zip`
was sideloaded, and the install again reported `Install completed with status 0`.

The boot failure is **unchanged**: `No valid operating system could be found`,
`OS Fingerprint: N/A`, immediate.

vbmeta AVB flags are therefore **not** the cause. The `--flags 3` restoration is
kept anyway because it matches upstream LineageOS sm6150-common and this device
cannot be given a custom AVB key, but it must not be described as a fix for this
failure.

The real cause is recorded in `docs/boot-lun-slot-mismatch-20260724.md`.
