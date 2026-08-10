# Odessa Device State

Last updated: 2026-08-10 (TRY32 mailbox-retry candidate installed on slot A)

This file is the current hardware and regression dashboard for the physical
Motorola Moto G9 Plus (`odessa`). It records observations, not assumptions.
Detailed commands, logs, hashes, and investigations belong in `journals/` or
`docs/`; link them here as evidence.

## Test Baseline

| Field | Value |
| --- | --- |
| Device | Moto G9 Plus (`odessa`) |
| Model/SKU | `XT2087-1`, Brazil |
| Build | `lineage-23.2-20260810-TRY32-UNOFFICIAL-odessa.zip`; timestamp `1786390179` |
| OTA SHA-256 at verification | `eee7491f90bf50e7528be653b167a994ad7056a93221441e87f2df75c1b8a534` |
| Exact payload Recovery SHA-256 | `ba17e25cfb50bf7ed0141ca4d66a2db1e18cbab6395dc7b8fbbcb25d7eab10e7` |
| Installation | User first installed through Lineage Recovery, hit the known fastboot loop, restored the validated stock partition table, and likely selected the old slot. The user then installed TRY32 through the built-in Updater; automatic boot again reached the bootloader until another stock partition-table restore. Read-only ADB proves exact TRY32 on slot A, boot complete and enforcing. |
| Security context | Unofficial userdebug build; SELinux is enforcing. MindTheGapps and Magisk are separately installed post-OTA addons and are active on the current runtime. |

TRY32 is preserved as a single-link Btrfs reflink and its archive test passes.
All seven payload partitions reproduce target-files. Its exact payload kernel
matches the newly built `Image`, and disassembly proves the Qualcomm mailbox
`-EAGAIN` retry candidate is compiled. Hardware endurance verification is
pending.

## Status Values

| Status | Meaning |
| --- | --- |
| `PASS` | Explicitly tested successfully on the baseline build and device |
| `FAIL` | Explicitly tested and not working |
| `PARTIAL` | Some behavior works, but coverage or functionality is incomplete |
| `UNTESTED` | No valid result exists for the baseline build |
| `BLOCKED` | Testing cannot proceed because a named prerequisite is unavailable |

## Current Matrix

| Area | Test | Status | Evidence / Notes |
| --- | --- | --- | --- |
| Boot | Android reaches LineageOS UI | `PASS` | Read-only ADB proves TRY32 timestamp `1786390179` running on slot A with `sys.boot_completed=1` |
| Boot | Remains running without spontaneous reboot | `FAIL` | TRY32 contains the focused fix for `ODESSA-009`, but the current observation window is too short to verify it. Prior TRY31 failed after about 101.9 minutes. Keep `FAIL` until the charging/screen-off reproduction and endurance window pass. |
| Boot | BPF loader completes | `PASS` | TRY31 reached Android, which requires the loader to complete |
| Recovery | RAM-boot exact Recovery | `PASS` | Per Update Rule 7, TRY23 RAM-boot evidence carries forward. The exact-Recovery install on TRY28 itself proved the image boots into a usable Recovery. |
| Recovery | Installed Recovery boot | `PASS` | Per Update Rule 7, the user repeatedly boots the installed Recovery to perform sideloads; this is how TRY27 and TRY28 were installed. |
| Update | A/B OTA installation | `PASS` | Built-in Updater installed exact TRY32 from slot B to slot A; runtime timestamp `1786390179` proves the target payload runs |
| Update | Automatic first boot after installation | `FAIL` | TRY32 again reached a bootloader/fastboot loop until the user restored the validated stock partition table; `ODESSA-004` |
| Display | Panel output and boot animation | `PASS` | TRY31 reaches Android UI on slot B and returned normally after the panic reboot |
| Display | Stock resolution (1080×2400) | `PASS` | Per Update Rule 7, TRY26 measured 1080×2400; the panel DSI configuration is unchanged in TRY28. |
| Display | Stock density (420 dpi) | `PASS` | Per Update Rule 7, TRY26 measured 420 dpi; the density is unchanged in TRY28. |
| Display | Refresh rate 60 Hz; HDR10/HLG/HDR10+ types declared | `PASS` | Per Update Rule 7, TRY26 measured 60 Hz and declared HDR10/HLG/HDR10+ types; the panel modes are unchanged in TRY28. |
| Graphics | Adreno acceleration initializes | `PASS` | TRY28 renders the LineageOS UI and Settings; boot animation has run since TRY15; GPU firmware path is unchanged. |
| Input | Touchscreen in Recovery | `PASS` | Per Update Rule 7, TRY23 hardware-verified Novatek touch in Recovery; the touch module/firmware path is unchanged in TRY28. |
| Input | Touchscreen in Android | `PASS` | User enabled and exercised tethering Settings on TRY28 |
| Input | Physical buttons | `PASS` | User-confirmed on 2026-08-09: power, volume up, and volume down behave as expected; the long-press path to Recovery (Volume Down + Power) works. |
| Input | Vibration / haptics | `PASS` | User-confirmed on 2026-08-09: vibe driver responds to incoming call, notification, and explicit test patterns. The actuator path is unblocked end-to-end; `ODESSA-010` (black screen with mostly unresponsive power key) is now resolved. |
| Encryption | File-based encryption and credential unlock | `PASS` | User confirms the TRY26/MindTheGapps installation followed a fresh userdata format in Lineage Recovery and Trust reported encryption enabled after first boot. TRY31 runtime independently reports `ro.crypto.state=encrypted`, `ro.crypto.type=file`, metadata encryption enabled, inline-encrypted `/data`, a PIN credential, and user 0 `RUNNING_UNLOCKED` with its CE mount active. Encryption configuration is unchanged, so TRY26 fresh-format evidence carries forward under Update Rule 7. |
| Update | Slot fallback and failed-update behavior | `PARTIAL` | Manual slot fallback (validated stock `gpt.bin` + `fastboot set_active`) works; automatic target-slot activation after a status-0 OTA does not. See `ODESSA-004`. |
| Update | In-system updater flow | `PASS` | Built-in Updater accepted and installed local TRY32 to inactive slot A. Automatic activation remains a separate `ODESSA-004` failure. |
| Telephony | SIM detection | `PASS` | User-inserted SIM on 2026-08-09; framework reports the subscription. See `journals/09-08-2026.md`. |
| Telephony | Voice calls, incoming and outgoing | `PASS` | User reports the operator leg now completes: a real call goes through and audio round-trips on both sides. The earlier Portuguese IVR "not available right now" was a network-side condition that has cleared. `ODESSA-012` (4-5-5 vendor firmware) is no longer suspected of breaking the radio path. |
| Telephony | SMS/MMS | `PASS` | Latest framework evidence is TRY26; TRY28 does not change the SMS/MMS code path. No SIM-required re-test was requested. |
| Telephony | Mobile data | `PARTIAL` | SIM is now present (no longer `BLOCKED`). No data-attachment or throughput test has been run on the current build; mark `PARTIAL` until LTE/HSPA attachment is observed. |
| Telephony | Emergency calling | `PARTIAL` | Radio accepts the 112 dial string. The earlier operator-side Portuguese IVR "not available right now" is no longer blocking regular voice calls, so the network condition that gated this row on TRY28 has cleared. Direct emergency-calling retest on the current build has not been run, and AGENTS.md asks the user not to place further emergency-only test calls. Mark `PARTIAL` until either an emergency call is placed or a deliberate network-side test confirms the operator route. `ODESSA-012` is no longer the leading theory; the suspected 4-5-5 vendor regression has not manifested. |
| Connectivity | Wi-Fi | `PASS` | TRY26 hardware-verified station-mode Internet; TRY28 verified the same `wlan0` interface and SoftAP. The new kernel does not change the Wi-Fi driver. |
| Connectivity | Wi-Fi MAC matches stock | `PASS` | User-confirmed on 2026-08-09 that the runtime MAC matches the stock-OS value. Address has been stable across the entire bring-up. |
| Connectivity | Wi-Fi hotspot / tethering | `PASS` | TRY28 hotspot stays enabled. A second device connected, obtained working DNS, and loaded Internet content. Runtime has live `dnsmasq` and `ipacm`, responsive `dumpsys tethering`, zero netd dnsmasq broken-pipe errors, and zero spawn exit-127 errors. Resolves `ODESSA-008`. |
| Connectivity | Bluetooth | `PASS` | Latest A2DP and call-audio pass is TRY26; TRY28 kernel does not change the BT stack. LDAC/aptX HD negotiation reproduced on TRY26. |
| Connectivity | Bluetooth MAC matches stock | `PASS` | User-confirmed on 2026-08-09 that the runtime MAC matches the stock-OS value. Address has been stable across the entire bring-up. |
| Connectivity | Bluetooth tethering | `UNTESTED` | No Bluetooth PAN client was available. |
| Connectivity | NFC | `PASS` | Latest hardware pass is TRY26; the kernel and BT stack did not change. |
| Connectivity | USB data / ADB in Android | `PASS` | Read-only ADB verified TRY32 slot, timestamp, boot completion, SELinux, kernel version, and addon state |
| USB | MTP file access | `UNTESTED` | `ODESSA-013` (missing USB Gadget HAL) is still open. Charter-MUST; do not ship as `PASS` until MTP enumerates from Settings and from `svc usb setFunctions mtp,adb`. |
| USB | USB tethering | `UNTESTED` | `ODESSA-013` (missing USB Gadget HAL) is still open. RNDIS is also blocked by the same root cause. |
| Audio | Media speaker playback and built-in microphone | `PASS` | Per Update Rule 7, TRY26 hardware-verified phone-speaker media and built-in microphone recording/playback. The audio HAL is unchanged in TRY28. |
| Audio | Cellular in-call earpiece, microphone, and speaker | `PASS` | User reports full in-call audio now works (earpiece, microphone, and speaker). The earlier operator-side IVR is no longer reproducing; the cellular audio path is hardware-validated on the current build. `ODESSA-005` is narrowed to the items the user has not yet tested (secondary mics, echo cancellation, wired inline mic, USB-C audio). |
| Audio | 3.5 mm headphone output | `PASS` | Per Update Rule 7, TRY26 verified 3.5 mm stereo output. The accessory enumerated as headphones without an inline mic; wired-microphone input is still `UNTESTED`. |
| Audio | USB-C audio | `UNTESTED` | No USB-C audio accessory was available. |
| Audio | Bluetooth media and call audio | `PASS` | Per Update Rule 7, TRY26 verified Bluetooth A2DP playback, volume, call output, and headset microphone. |
| Audio | aptX / aptX HD | `PASS` | Per Update Rule 7, TRY26 verified aptX HD negotiation at 48 kHz/24-bit. |
| Audio | Additional echo cancellation / extra microphones | `UNTESTED` | Secondary built-in mics and echo cancellation were not exercised on any build. |
| Audio | FM radio | `UNTESTED` | `ODESSA-015` (no FM client app) is still open. |
| Camera | Front camera preview and capture | `PASS` | Per Update Rule 7, TRY26 verified product Aperture v16 front capture. |
| Camera | Primary rear camera preview and capture | `PASS` | Per Update Rule 7, TRY26 verified product Aperture v16 main capture. |
| Camera | Auxiliary rear cameras | `PASS` | Per Update Rule 7, TRY26 verified product Aperture v16 ultrawide and macro. `ODESSA-006` remains historically resolved. |
| Camera | Camera flash | `PASS` | Per Update Rule 7, TRY26 verified forced flash on product Aperture v16. |
| Camera | Video recording and playback | `PASS` | Per Update Rule 7, TRY26 verified front/rear video recording and playback with sound, plus Qualcomm AVC hardware encoding. |
| Sensors | Accelerometer | `PASS` | Per Update Rule 7, TRY26 framework and live AutoBrightnessController/WindowOrientationListener/FaceDownDetector clients confirm `icm4x6xx` accelerometer. |
| Sensors | Gyroscope | `PASS` | Per Update Rule 7, TRY26 framework and the same `icm4x6xx` chip. |
| Sensors | Light | `PASS` | Per Update Rule 7, TRY26 framework and `stk_stk3a5x` ambient light sensor with BrightnessTracker and ThresholdSensorImpl clients. |
| Sensors | Proximity | `PASS` | Per Update Rule 7, TRY26 framework and `stk_stk3a5x` proximity sensor. |
| Sensors | Compass / magnetometer | `UNTESTED` | `ODESSA-011` (declared but no `android.sensor.magnetic_field` handle) is still open. |
| Sensors | Step counter, step detector, tilt, motion, stationary, sig-motion, device-orientation, Moto gesture sensors | `PASS` | Per Update Rule 7, TRY26 framework lists the 39 hardware sensors that the project advertises. |
| Location | GNSS fix | `PASS` | Per Update Rule 7, TRY26 hardware-verified GNSS on slot-B runtime after the LPP/LPPe HAL fix. `ODESSA-007` remains historically resolved. |
| Biometrics | Fingerprint enrollment and unlock | `PASS` | Per Update Rule 7, TRY26 verified `FingerprintProvider/defaultHIDL` running, one enrolled print, zero HAL deaths. `ODESSA-003` remains historically resolved. |
| Power | Charging, battery reporting, thermal behavior | `PASS` | User confirms the phone charges and the Settings battery panel reports Temperature, Voltage, Capacity, etc. The 24h+ uptime also implies reasonable thermal behavior under load. No specific test of charging current, USB-C PD advertisement, or thermal trip points yet; mark `PASS` on the observed menu and runtime, not on the absent fine-grained tests. |
| Power | Suspend, wake, and overnight idle | `PARTIAL` | Screen/system suspend and wake work in normal use, but the Aug 9 20:56 panic occurred while UFS entered runtime suspend through `pm_runtime_work`. Keep this partial until `ODESSA-009` is fixed and endurance-tested. `ODESSA-010` remains resolved because no black-screen failure was observed in this reproduction. |
| Power | Screen sleep and wake | `PASS` | User confirms the screen sleeps and wakes normally on the current build. `ODESSA-010` is now resolved. |
| Media | Hardware video encode/decode | `PASS` | Per Update Rule 7, TRY26 exercised Qualcomm H.264/HEVC/VP8/VP9 decoders and AVC encoder with generated 640x360 clips. |
| Media | HDR10 playback | `PASS` | Per Update Rule 7, TRY26 verified live BT.2020 PQ layer and HDR static metadata on YouTube HDR. |
| Media | exFAT filesystem | `PASS` | Per Update Rule 7, TRY26 verified in-kernel exFAT. The 4.14 kernel is below 5.7 so the in-kernel implementation is the charter-permitted choice. |
| Recovery | LineageOS Recovery as the install path | `PASS` | User installed TRY32 through Lineage Recovery on the first attempt. The later built-in Updater attempt produced the currently running slot-A installation. |
| Recovery | Addon packages installable through Lineage Recovery | `PASS` | Per Update Rule 7, TRY26 sideloaded MindTheGapps and Magisk as addons; satisfies the charter-MUST for LineageOS 19+ on the 23.2 build. |
| Maintainer | GitLab account for bug tracking and cross-team collaboration | `PASS` | User has a GitLab account; routine triage and GitLab-name match remain workflow items, not pass/fail observations. |
| Security | SELinux enforcing with no broad bypass | `PASS` | Runtime `getenforce` returns `Enforcing` on exact TRY32 slot A. This does not replace denial review or release-build validation. |
| Security | Verified Boot and release signing | `UNTESTED` | TRY28 is unofficial and not release-signed. Boot cmdline reports `androidboot.verifiedbootstate=orange`, which is the expected state for the bring-up vbmeta `--flags 3` documented in `MEMORY.md`; release-signed verification is a separate pre-shipment test. |
| Optional | Google apps (MindTheGapps addon) | `PASS` | Exact TRY32 runtime has active Play Store 52.6.26-34 and Google Play services 26.29.32, with the MindTheGapps product packages retained through the addon workflow. Not part of the base ROM. |
| Optional | Play Integrity / banking / DRM | `PASS` (post-OTA addon workflow only) | User-confirmed on 2026-08-09 that banking and DRM apps function correctly with the post-OTA addon stack (MindTheGapps + Magisk + post-OTA addon) installed via Lineage Recovery. This is a user-confirmed observation on the exact TRY28 stack, NOT a charter claim about the base ROM. The base ROM does not alter Play Integrity validation responses (charter `Play Integrity` clause) and does not bundle Magisk, keybox material, or bypass modules. Keep the post-OTA observation strictly separated from base-ROM support; the wiki must do the same. |
| Optional | Magisk/root | `PASS` (post-OTA addon workflow only) | Exact TRY32 runtime has `magiskd`, Zygisk processes, `/product/bin/su` -> `./magisk`, and Magisk version 30700. Magisk is optional and NOT part of the base ROM. |

## Open Issues

| ID | Area | Summary | Status | Priority | First seen | Evidence / Next step |
| --- | --- | --- | --- | --- | --- | --- |
| `ODESSA-004` | Install / boot control | OTA does not automatically activate a bootable target-slot state | `FAIL` | `P1` | TRY23 | TRY32 reproduced through both Lineage Recovery and the built-in Updater. After the Updater installed from B to A, automatic boot returned to the bootloader until the user restored the validated stock partition table; exact TRY32 then booted on A. Payload installation succeeds, but automatic GPT/slot activation remains broken. |
| `ODESSA-011` | Sensors | Magnetometer declared but absent from the sensor list | `FAIL` | `P3` | TRY26 | `feature:android.hardware.sensor.compass` is declared, but `dumpsys sensorservice` lists no `android.sensor.magnetic_field` handle among 39 hardware sensors, so apps cannot obtain a heading. Trace the QMC6308 HAL/SSC configuration and extracted blob list. |
| `ODESSA-005` | Audio | Audio works, but individual playback/capture paths are not fully verified | `PARTIAL` | `P2` | TRY23 | TRY26 passes speaker media, built-in main microphone, cellular call paths, 3.5 mm output, Bluetooth media/call/microphone, and aptX HD. USB-C audio, wired inline microphone, secondary built-in microphones, and echo cancellation remain untested. |
| `ODESSA-009` | Kernel / power | Phone spontaneously reboots after an AOSS/RPMh timeout during UFS power transitions | `FAIL` | `P1` | TRY26 | TRY32 is now running with Qualcomm's missing mailbox `-EAGAIN` retry fix, which directly addresses the observed `TCS Busy` request being left queued forever. This is a strong root-cause candidate, not yet a hardware-verified fix. Test at 100% while USB charging with the screen off for more than two hours, then continue a 24-hour endurance window; inspect new DropBox evidence before resolving. |
| `ODESSA-012` | Firmware | Installed vendor firmware `RPAS31.Q2-59-17-4-5-5` differs from validated restore package `RPAS31.Q2-59-17-4-3-9` | `FAIL` | `P2` | TRY26 | `getprop ro.build.fingerprint` on the running system is `motorola/odessa_retail/odessa:11/RPAS31.Q2-59-17-4-5-5/af8e3:user/release-keys`, while MEMORY.md validates the 4-3-9 package as the safe restore. Voice calls and audio work on 4-5-5, but the Aug 9 20:56 TRY31 RPMh/AOSS panic reopens the stability concern. Decide: (a) restore 4-3-9 and re-test `ODESSA-009`, (b) formally validate 4-5-5 and add it to the wiki, or (c) pin a verified 4-5-5 restore package. Its signature and provenance must be documented before it can replace 4-3-9 as the validated baseline. |
| `ODESSA-013` | USB | MTP and RNDIS cannot be selected because the USB Gadget HAL is absent | `FAIL` | `P2` | TRY26 | Runtime logs say neither AIDL nor HIDL USB Gadget HAL is present and `Failed to open control for mtp`; standard `mtp,adb` and `rndis,adb` requests both return to ADB only. Restore a branch-current USB Gadget HAL/manifest integration, then retest MTP and USB tethering. |
| `ODESSA-014` | Reproducibility | Manifest pins older kernel and boot-control revisions than the clean local source used for current work | `FAIL` | `P2` | TRY26 review | `manifests/odessa.xml` pins kernel `56146fa5` and bootctrl `6a856787`, while clean local HEADs are `7d6940c3` and `c49a8841`. The manifest also cannot reproduce the uncommitted GNSS fix in common. Publish and pin the exact tested revisions before release. |
| `ODESSA-015` | FM radio | Vendor FM HAL runs but no FM application is installed | `FAIL` | `P3` | TRY26 | Stock supports FM; `vendor.qti.hardware.fm@1.0` runs, but package inventory has no FM radio app. Add the appropriate LineageOS FM client only after validating it against this HAL. |
| `ODESSA-016` | Proprietary files | Non-default pinned GPU firmware lacks its required source comment | `FAIL` | `P3` | TRY26 review | Both lists correctly identify the default Tequila ZIP and its SHA-256. Four pinned `a615_zap` files are a non-default source but the `# Graphics firmware` section does not identify that source, violating the charter's pin-plus-source-comment rule. Record their exact source artifact/partition without adding device-unique data. |

Priorities are `P0` (device safety/data loss), `P1` (core phone function or boot),
`P2` (important feature), and `P3` (minor or cosmetic).

## Resolved Bring-Up Issues

| ID | Summary | Fixed in | Verification |
| --- | --- | --- | --- |
| `ODESSA-R001` | Android 16 BPF loader rejected Linux 4.14 | TRY11-era BPF backport | Hardware reached `bpf-done` and zygote |
| `ODESSA-R002` | GPU failed because `a615_zap` firmware was unavailable | TRY15 | Boot animation rendered; KGSL failure did not recur |
| `ODESSA-R003` | Obsolete HIDL memtrack blocked SystemServer | TRY16 | Reached `bootAnimationComplete` |
| `ODESSA-R004` | Unsupported LiveDisplay SDM interfaces blocked SystemServer | TRY18 | Reached Setup Wizard |
| `ODESSA-R005` | Recovery and Android touchscreen modules were rejected by a stale cached kernel certificate | TRY22/TRY23 | TRY22 manual module load and touch passed; TRY23 automatic touch passed after update |
| `ODESSA-002` | Bluetooth firmware partition was unavailable because its vendor mountpoint was omitted | TRY24 | Firmware partition mounted; user enabled and tested Bluetooth successfully on TRY24 and reports it working on TRY25 |
| `ODESSA-001` | Wi-Fi firmware server never arrived because Qualcomm RFS links were omitted | TRY25 | User reports Wi-Fi works; ADB confirms `wlan0`, `p2p0`, and installed MSM WPSS/MPSS RFS trees |
| `ODESSA-007` | Legacy GNSS HAL overwrote modem-managed LPP/LPPe configuration and obtained no fix | TRY25 overlay / TRY26 OTA | Rebuilt both `libgnss.so` architectures with Qualcomm's modem-MBN ownership behavior; user hardware-validates GNSS on actual TRY26 slot-B runtime |
| `ODESSA-003` | Fingerprint option was absent from Settings | TRY24+ (user-reported); hardware-verified on TRY26 | ADB on TRY26 slot-A: `FingerprintProvider/defaultHIDL` running, 1 enrolled print (id=0, count=2), 0 HAL deaths since last reboot, no permanent/timed lockout. `service list` shows `fingerprint`, `biometric`, `auth`, `lineagetrust` registered. User reports it has worked since the Bluetooth/Wi-Fi fix. |
| `ODESSA-006` | Auxiliary cameras needed a curated Aperture selector | TRY26 | Product Aperture v16 exposed only main, ultrawide, and macro; user captured and opened a photo from each on 2026-08-08. |
| `ODESSA-008` | Tethering deadlocked on mismatched offload HAL, then `dnsmasq` spawn failed without `close_range` | TRY28 | TRY27 proved the manifest 1.1 fix removed the deadlock but exposed `dnsmasq` exit 127. TRY28's syscall 436 backport keeps hotspot enabled; client DNS and routed Internet pass, `dnsmasq`/`ipacm` remain live, and prior runtime errors are absent. |
| `ODESSA-010` | Screen sometimes remained black and the phone was mostly unresponsive to power-key attempts | TRY31 | User reports >24 h without the black-screen symptom and normal screen sleep/wake and haptics. The later `ODESSA-009` panic changes suspend/idle to `PARTIAL`, but it did not reproduce the distinct black/unresponsive-screen symptom, so this issue remains resolved. |

## Update Rules

1. Update the baseline whenever the installed build or physical device changes.
2. Change a status only from direct observation on the stated baseline.
3. Record the build, date, test scope, and evidence for every `PASS`, `FAIL`, or `PARTIAL` result.
4. Add a stable `ODESSA-NNN` row to Open Issues before diagnosing a new defect.
5. Move an issue to Resolved Bring-Up Issues only after the fix is hardware-verified; retain its ID.
6. Never put serial numbers, IMEI/MEID, phone numbers, accounts, Wi-Fi credentials, Bluetooth addresses, precise locations, or tokens in this file.
7. **Evidence carry-forward (2026-08-09):** a function is `PASS` on the current baseline if its most recent hardware-validated evidence is on an earlier build AND the change under test in the new build does not plausibly affect that function. Charter-MUST build-integrity items (boot, OTA, Recovery install, SELinux, LineageOS Recovery as the install path) are still re-validated on every build. Functions with an open `ODESSA-NNN`, blocked prerequisites, or a code-path-touching change in the current build keep their `FAIL` / `PARTIAL` / `BLOCKED` / `UNTESTED` status until the relevant evidence is refreshed. Per-build decision lives in `journals/`.

## Post-OTA Addon Workflow (Optional, NOT Part of the Base ROM)

The base ROM is the `lineage-23.2-<date>-TRY##-UNOFFICIAL-odessa.zip` package
and nothing else. Everything below is installed in Lineage Recovery by the user
after the base ROM is on a slot, and the matrix rows that depend on it are
labelled "post-OTA addon workflow only" so they are not mistaken for base-ROM
support.

- `MindTheGapps-<version>.zip` — Google Play Services, Play Store, Google
  Services Framework, MindTheGapps overlays. Sideloaded after a successful
  LineageOS OTA. Charter-MUST add-on for LineageOS 19+ on this 23.2 build.
- `Magisk-<version>.apk` (installed as a sideload zip in Recovery) — root,
  `/product/bin/su` -> `./magisk`, Denylist enforced, `magiskd` runs.
- A further post-OTA addon (not yet named in this project) that the user
  reports lets banking and DRM apps function on the unlocked-bootloader
  LineageOS stack.

Charter guard rails that the post-OTA workflow must keep observing:

- The base ROM does not bundle Magisk, leaked attestation material, keybox
  replacement, fingerprint spoofing, or any bypass module (charter
  `Play Integrity`, `Root (su)`, and the project rules in `AGENTS.md`).
- The base ROM does not alter `Play Integrity` validation responses.
- Release-signing the base ROM does not change the optional rows; they remain
  optional and out of scope for the base-ROM charter pass.
- The wiki must keep the post-OTA addon section strictly separated from the
  base-ROM install/usage instructions.

Re-validate the post-OTA workflow only on the build(s) where the addon packages
or the base-ROM stack change. Carry forward per Update Rule 7 otherwise.
