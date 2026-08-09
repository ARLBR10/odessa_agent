# Odessa Device State

Last updated: 2026-08-09 (TRY28 installed; hotspot and automatic first boot tested)

This file is the current hardware and regression dashboard for the physical
Motorola Moto G9 Plus (`odessa`). It records observations, not assumptions.
Detailed commands, logs, hashes, and investigations belong in `journals/` or
`docs/`; link them here as evidence.

## Test Baseline

| Field | Value |
| --- | --- |
| Device | Moto G9 Plus (`odessa`) |
| Model/SKU | `XT2087-1`, Brazil |
| Build | `lineage-23.2-20260809-TRY28-UNOFFICIAL-odessa.zip`; build timestamp `1786236578` |
| OTA SHA-256 at verification | `db2283135abbd5192047a05e469ec09911bb51c561b4d82214143257821a97a4` |
| Exact payload Recovery SHA-256 | `f35792aae2e495716688218f6c2d2c130eb901bd56706b5a522690dd739903dc` |
| Installation | With explicit user authorization, TRY28 was sideloaded from slot-B Lineage Recovery to target slot A. Recovery reported installation complete. The automatic boot then looped; the user flashed `gpt.bin` from the validated RPAS31.Q2-59-17-4-3-9 stock package, after which TRY28 booted successfully on slot A. |
| Security context | Unofficial userdebug build; SELinux is enforcing. Root/Magisk was not verified on TRY28; do not treat this as a rooted reproduction. |

TRY28 is preserved as a single-link Btrfs reflink. Archive and VINTF checks pass,
and all seven exact payload partitions reproduce target-files. Its payload kernel
contains the native and compat syscall 436 backport.

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
| Boot | Android reaches LineageOS UI | `PASS` | TRY28 booted on slot A; runtime timestamp `1786236578` and `sys.boot_completed=1` |
| Boot | Remains running without spontaneous reboot | `UNTESTED` | Four TRY26 panics had the same RPMh/AOSS timeout; no TRY28 endurance result yet. `ODESSA-009` |
| Boot | BPF loader completes | `PASS` | TRY28 reached Android, which requires the loader to complete |
| Recovery | RAM-boot exact Recovery | `UNTESTED` | Latest direct evidence is TRY23 |
| Recovery | Installed Recovery boot | `UNTESTED` | |
| Update | A/B OTA installation | `PASS` | TRY28 sideload completed to target slot A and exact timestamp `1786236578` now runs there |
| Update | Automatic first boot after installation | `FAIL` | TRY28 bootlooped until the user flashed the validated RPAS31.Q2-59-17-4-3-9 `gpt.bin`; `ODESSA-004` |
| Display | Panel output and boot animation | `PASS` | TRY28 reached Android UI and Settings after GPT restoration |
| Display | Stock resolution (1080×2400) | `UNTESTED` | Latest direct measurement is TRY26 |
| Display | Stock density (420 dpi) | `UNTESTED` | Latest direct measurement is TRY26 |
| Display | Refresh rate 60 Hz; HDR10/HLG/HDR10+ types declared | `UNTESTED` | Latest direct evidence is TRY26 |
| Graphics | Adreno acceleration initializes | `UNTESTED` | TRY28 renders UI, but detailed GPU validation was not repeated |
| Input | Touchscreen in Recovery | `UNTESTED` | Latest direct evidence is TRY23 |
| Input | Touchscreen in Android | `PASS` | User enabled and exercised tethering Settings on TRY28 |
| Input | Physical buttons | `UNTESTED` | Latest partial evidence is from an older build |
| Input | Vibration / haptics | `UNTESTED` | Latest partial evidence is TRY26. `ODESSA-010` |
| Encryption | File-based encryption and credential unlock | `UNTESTED` | Latest partial evidence is TRY26 |
| Update | Slot fallback and failed-update behavior | `UNTESTED` | Latest direct fallback evidence is from the TRY26 installation sequence |
| Update | In-system updater flow | `UNTESTED` | Current update path details not fully recorded |
| Telephony | SIM detection | `BLOCKED` | Both slots reported `ABSENT`; no SIM was available for insertion testing. |
| Telephony | Voice calls, incoming and outgoing | `UNTESTED` | Latest hardware pass is TRY26 |
| Telephony | SMS/MMS | `UNTESTED` | |
| Telephony | Mobile data | `BLOCKED` | Both SIM slots were absent on 2026-08-08. Test LTE attachment and data transfer when a SIM is available. |
| Telephony | Emergency calling | `BLOCKED` | No SIM and no lawful coordinated emergency-call test plan; do not place test emergency calls casually. |
| Connectivity | Wi-Fi | `UNTESTED` | Latest validated station-mode Internet pass is TRY26; TRY28 exercised SoftAP only |
| Connectivity | Wi-Fi MAC matches stock | `UNTESTED` | Runtime and boot-command-line Wi-Fi addresses agree with the previously recorded values, but no privacy-safe stock-OS capture exists for comparison. |
| Connectivity | Wi-Fi hotspot / tethering | `PASS` | TRY28 hotspot stays enabled. A second device connected, obtained working DNS, and loaded Internet content. Runtime has live `dnsmasq` and `ipacm`, responsive `dumpsys tethering`, zero netd dnsmasq broken-pipe errors, and zero spawn exit-127 errors. Resolves `ODESSA-008`. |
| Connectivity | Bluetooth | `UNTESTED` | Latest A2DP and call-audio pass is TRY26 |
| Connectivity | Bluetooth MAC matches stock | `UNTESTED` | Boot command line still carries the previously recorded Bluetooth address, but no privacy-safe stock-OS capture exists for comparison. |
| Connectivity | Bluetooth tethering | `UNTESTED` | No Bluetooth PAN client was available. |
| Connectivity | NFC | `UNTESTED` | Latest hardware pass is TRY26 |
| Connectivity | USB data / ADB in Android | `PASS` | Read-only ADB verified TRY28 slot, timestamp, boot completion, SELinux, services, and tethering behavior |
| USB | MTP file access | `UNTESTED` | Latest failure is TRY26; `ODESSA-013` remains open |
| USB | USB tethering | `UNTESTED` | Latest failure is TRY26; missing USB Gadget HAL issue `ODESSA-013` remains open |
| Audio | Media speaker playback and built-in microphone | `UNTESTED` | Latest hardware pass is TRY26 |
| Audio | Cellular in-call earpiece, microphone, and speaker | `UNTESTED` | Latest hardware pass is TRY26 |
| Audio | 3.5 mm headphone output | `UNTESTED` | Latest hardware pass is TRY26 |
| Audio | USB-C audio | `UNTESTED` | No USB-C audio accessory was available. |
| Audio | Bluetooth media and call audio | `UNTESTED` | Latest hardware pass is TRY26 |
| Audio | aptX / aptX HD | `UNTESTED` | Latest hardware pass is TRY26 |
| Audio | Additional echo cancellation / extra microphones | `UNTESTED` | Latest partial evidence is TRY26 |
| Audio | FM radio | `UNTESTED` | TRY26 lacked a client app; `ODESSA-015` remains open |
| Camera | Front camera preview and capture | `UNTESTED` | Latest hardware pass is TRY26 |
| Camera | Primary rear camera preview and capture | `UNTESTED` | Latest hardware pass is TRY26 |
| Camera | Auxiliary rear cameras | `UNTESTED` | Latest hardware pass is TRY26; `ODESSA-006` remains historically resolved |
| Camera | Camera flash | `UNTESTED` | Latest hardware pass is TRY26 |
| Camera | Video recording and playback | `UNTESTED` | Latest hardware pass is TRY26 |
| Sensors | Accelerometer | `UNTESTED` | Latest framework evidence is TRY26 |
| Sensors | Gyroscope | `UNTESTED` | Latest framework evidence is TRY26 |
| Sensors | Light | `UNTESTED` | Latest framework evidence is TRY26 |
| Sensors | Proximity | `UNTESTED` | Latest framework evidence is TRY26 |
| Sensors | Compass / magnetometer | `UNTESTED` | Latest failure is TRY26; `ODESSA-011` remains open |
| Sensors | Step counter, step detector, tilt, motion, stationary, sig-motion, device-orientation, Moto gesture sensors | `UNTESTED` | Latest framework evidence is TRY26 |
| Location | GNSS fix | `UNTESTED` | Latest hardware pass is TRY26; `ODESSA-007` remains historically resolved |
| Biometrics | Fingerprint enrollment and unlock | `UNTESTED` | Latest framework and hardware pass is TRY26; `ODESSA-003` remains historically resolved |
| Power | Charging, battery reporting, thermal behavior | `UNTESTED` | Include powered-off charging and USB current behavior |
| Power | Suspend, wake, and overnight idle | `UNTESTED` | TRY26 failed with RPMh/AOSS panics; no TRY28 endurance result yet. `ODESSA-009`, `ODESSA-010` |
| Power | Screen sleep and wake | `UNTESTED` | TRY26 failed; no TRY28 result yet. `ODESSA-010` |
| Media | Hardware video encode/decode | `UNTESTED` | Latest partial evidence is TRY26 |
| Media | HDR10 playback | `UNTESTED` | Latest hardware pass is TRY26 |
| Media | exFAT filesystem | `UNTESTED` | Latest hardware pass is TRY26 |
| Recovery | LineageOS Recovery as the install path | `PASS` | TRY28 was installed through Lineage Recovery; exact-Recovery isolation remains untested |
| Recovery | Addon packages installable through Lineage Recovery | `UNTESTED` | Latest addon pass is TRY26 |
| Maintainer | GitLab account for bug tracking and cross-team collaboration | `PASS` | User has a GitLab account; routine triage and GitLab-name match remain workflow items, not pass/fail observations. |
| Security | SELinux enforcing with no broad bypass | `PASS` | Runtime `getenforce` returned `Enforcing` on TRY28 on 2026-08-09. This does not replace denial review or release-build validation. |
| Security | Verified Boot and release signing | `UNTESTED` | TRY28 is unofficial and not release-signed; runtime boot-state evidence was not repeated |
| Optional | Google apps (MindTheGapps addon) | `UNTESTED` | Latest package inventory is TRY26 |
| Optional | Play Integrity / banking / DRM | `UNTESTED` | No claim permitted without exact-build testing |
| Optional | Magisk/root | `UNTESTED` | Not checked after TRY28 installation; root is optional and not part of the base ROM |

## Open Issues

| ID | Area | Summary | Status | Priority | First seen | Evidence / Next step |
| --- | --- | --- | --- | --- | --- | --- |
| `ODESSA-004` | Install / boot control | OTA does not automatically activate a bootable target-slot state | `FAIL` | `P1` | TRY23 | TRY28 sideloaded successfully from B to A but bootlooped until the user flashed `gpt.bin` from validated RPAS31.Q2-59-17-4-3-9; runtime then proved TRY28 timestamp `1786236578` on A. Preserve pre/post-OTA GPT captures and inspect the running Recovery boot-control HAL. |
| `ODESSA-011` | Sensors | Magnetometer declared but absent from the sensor list | `FAIL` | `P3` | TRY26 | `feature:android.hardware.sensor.compass` is declared, but `dumpsys sensorservice` lists no `android.sensor.magnetic_field` handle among 39 hardware sensors, so apps cannot obtain a heading. Trace the QMC6308 HAL/SSC configuration and extracted blob list. |
| `ODESSA-005` | Audio | Audio works, but individual playback/capture paths are not fully verified | `PARTIAL` | `P2` | TRY23 | TRY26 passes speaker media, built-in main microphone, cellular call paths, 3.5 mm output, Bluetooth media/call/microphone, and aptX HD. USB-C audio, wired inline microphone, secondary built-in microphones, and echo cancellation remain untested. |
| `ODESSA-009` | Kernel / power | Phone spontaneously reboots after an AOSS/RPMh timeout during UFS clock gating | `FAIL` | `P1` | TRY26 | Four `SYSTEM_LAST_KMSG` records from Aug 5-6 show `TCS Busy`, four 10-second RPMh response timeouts for address `0x50000`, then `BUG()` at `drivers/soc/qcom/rpmh.c:209`. Every initiating trace is `ufshcd_gate_work` -> `ufshcd_setup_clocks` -> `ufs_qcom_set_bus_vote` -> RPMh; the kernel then panics and reboots. Reproduce unrooted, compare power/RPMh/UFS behavior against the prior working kernel, and fix the lost AOSS response rather than merely removing `BUG()`. |
| `ODESSA-010` | Display / wake | Screen sometimes remains black and the phone is mostly unresponsive to power-key attempts | `FAIL` | `P1` | TRY26 | User report; the latest attempt produced haptic feedback but most did not. A live post-boot dump only showed a normal asleep/display-off policy and no SurfaceFlinger/GPU crash. The symptom may be the 40-50 second RPMh/AOSS stall preceding `ODESSA-009`, but that link is not yet proven. Capture immediate ADB state during an episode if the device remains reachable. |
| `ODESSA-012` | Firmware | Installed vendor firmware `RPAS31.Q2-59-17-4-5-5` differs from validated restore package `RPAS31.Q2-59-17-4-3-9` | `FAIL` | `P2` | TRY26 | `getprop ro.build.fingerprint` on the running system is `motorola/odessa_retail/odessa:11/RPAS31.Q2-59-17-4-5-5/af8e3:user/release-keys`, while MEMORY.md validates the 4-3-9 package as the safe restore. The 4-5-5 firmware was therefore acquired after the user-installed GApps/Magisk session; the RPMh/AOSS stall in `ODESSA-009` may be a 4-5-5 vendor regression. Charter requires asserting on known-working firmware. Decide: (a) restore 4-3-9 and re-validate, (b) re-run the bring-up validation suite on 4-5-5 and add it to the wiki, or (c) pin a new restore package. |
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

## Update Rules

1. Update the baseline whenever the installed build or physical device changes.
2. Change a status only from direct observation on the stated baseline.
3. Record the build, date, test scope, and evidence for every `PASS`, `FAIL`, or `PARTIAL` result.
4. Add a stable `ODESSA-NNN` row to Open Issues before diagnosing a new defect.
5. Move an issue to Resolved Bring-Up Issues only after the fix is hardware-verified; retain its ID.
6. Never put serial numbers, IMEI/MEID, phone numbers, accounts, Wi-Fi credentials, Bluetooth addresses, precise locations, or tokens in this file.
