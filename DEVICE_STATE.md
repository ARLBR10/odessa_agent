# Odessa Device State

Last updated: 2026-08-05 (TRY25 auxiliary-camera APK test)

This file is the current hardware and regression dashboard for the physical
Motorola Moto G9 Plus (`odessa`). It records observations, not assumptions.
Detailed commands, logs, hashes, and investigations belong in `journals/` or
`docs/`; link them here as evidence.

## Test Baseline

| Field | Value |
| --- | --- |
| Device | Moto G9 Plus (`odessa`) |
| Model/SKU | `XT2087-1`, Brazil |
| Build | `lineage-23.2-20260805-TRY25-UNOFFICIAL-odessa.zip`; build timestamp `1785888497` |
| OTA SHA-256 at verification | `abbc875d67411b2b197b24392ec8ee939f4bf07c67d058c780090d3d8ce9b1ca` |
| Exact payload Recovery SHA-256 | Not reverified for TRY25 |
| Installation | User installed TRY25; Android is running from slot A with the exact build timestamp. A locally rebuilt Aperture APK (SHA-256 `c2403a3478c2a51198d5dec633c391baa40057e5927d910f4f59c553f9d46132`) is installed as a userdata system-app update for camera testing. |
| Security context | Unofficial userdebug build; rooted debugging was temporarily enabled for diagnosis and adbd was returned to non-root |

The named TRY25 ZIP shares the mutable `lineage_odessa-ota.zip` inode. The hash
above identifies the bytes verified before installation, but the filename is not
a preserved artifact and must not be trusted after another build.

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
| Boot | Android reaches LineageOS UI | `PASS` | TRY25 slot A reached Android and completed boot |
| Boot | BPF loader completes | `PASS` | TRY25 reached Android; earlier direct marker evidence is from the TRY11-era build |
| Recovery | RAM-boot exact Recovery | `UNTESTED` | Latest direct evidence is TRY23 |
| Recovery | Installed Recovery boot | `UNTESTED` | |
| Update | A/B OTA installation | `PASS` | User installed TRY25 and its exact timestamp is running from slot A |
| Update | Automatic first boot after installation | `UNTESTED` | Latest failure evidence is TRY24, when stock partition-table restoration returned to old slot A; `ODESSA-004` remains open |
| Display | Panel output and boot animation | `PASS` | TRY25 rendered Android UI |
| Graphics | Adreno acceleration initializes | `PASS` | TRY25 rendered Android UI; detailed GPU validation remains from TRY15 |
| Input | Touchscreen in Recovery | `UNTESTED` | Latest direct evidence is TRY23 |
| Input | Touchscreen in Android | `PASS` | User interacted with TRY25 Android and Wi-Fi controls |
| Input | Physical buttons | `UNTESTED` | Latest partial evidence is from an older build |
| Input | Vibration / haptics | `UNTESTED` | Latest direct evidence is TRY23 |
| Encryption | Fresh userdata encryption and unlock | `UNTESTED` | Must be tested on the current baseline |
| Update | Slot fallback and failed-update behavior | `UNTESTED` | Successful update alone does not validate fallback |
| Update | In-system updater flow | `UNTESTED` | Current update path details not fully recorded |
| Telephony | SIM detection | `UNTESTED` | |
| Telephony | Voice calls, incoming and outgoing | `UNTESTED` | Include proximity, earpiece, microphone, speaker, and hangup |
| Telephony | SMS/MMS | `UNTESTED` | |
| Telephony | Mobile data | `UNTESTED` | Test LTE attachment and data transfer |
| Telephony | Emergency calling | `UNTESTED` | Use a lawful non-disruptive validation plan; do not place test emergency calls casually |
| Connectivity | Wi-Fi | `PASS` | User reports Wi-Fi works on TRY25; ADB confirms `wlan0`, `p2p0`, and the required MSM WPSS/MPSS RFS trees |
| Connectivity | Bluetooth | `PASS` | User reports Bluetooth works on TRY25; `/vendor/bt_firmware` is mounted |
| Connectivity | NFC | `UNTESTED` | Regional SKU support must be verified |
| Connectivity | USB data / ADB in Android | `PASS` | Android ADB used to verify TRY25 |
| Audio | Speaker, earpiece, microphones, headset | `PARTIAL` | User reports audio works on TRY25 with `/vendor/dsp` mounted; exact speaker, earpiece, microphone, headset, call-audio, and scrcpy paths need separate tests; `ODESSA-005` |
| Camera | Front camera preview and capture | `UNTESTED` | Latest direct evidence is TRY23 |
| Camera | Primary rear camera preview and capture | `UNTESTED` | Latest direct evidence is TRY23 |
| Camera | Auxiliary rear cameras | `PARTIAL` | On TRY25 with the local Aperture update, the user hardware-tested working color ultrawide and macro selectors. The unfiltered test also exposed the monochrome depth sensor and two duplicate main-camera processing endpoints; the refined ID exclusions remain unbuilt and untested. `ODESSA-006` remains open. |
| Camera | Camera flash | `UNTESTED` | Latest direct evidence is TRY23 |
| Camera | Video recording and playback | `UNTESTED` | Test front/rear recording, audio, stabilization, and common resolutions |
| Sensors | Accelerometer, gyro, light, proximity, compass | `UNTESTED` | |
| Location | GNSS fix | `UNTESTED` | Test cold and warm fixes without leaking location data |
| Biometrics | Fingerprint enrollment and unlock | `UNTESTED` | Latest failure evidence is TRY23; `ODESSA-003` remains open |
| Power | Charging, battery reporting, thermal behavior | `UNTESTED` | Include powered-off charging and USB current behavior |
| Power | Suspend, wake, and overnight idle | `UNTESTED` | |
| Power | Screen sleep | `UNTESTED` | Latest direct evidence is TRY23 |
| Media | Hardware video encode/decode | `UNTESTED` | |
| Security | SELinux enforcing with no broad bypass | `UNTESTED` | Userdebug observations do not establish release readiness |
| Security | Verified Boot and release signing | `UNTESTED` | Current artifacts use bring-up signing/security limitations |
| Optional | Google apps | `UNTESTED` | Keep separate from base-ROM support |
| Optional | Play Integrity / banking / DRM | `UNTESTED` | No claim permitted without exact-build testing |
| Optional | Magisk/root | `UNTESTED` | Keep separate from the unrooted base ROM |

## Open Issues

| ID | Area | Summary | Status | Priority | First seen | Evidence / Next step |
| --- | --- | --- | --- | --- | --- | --- |
| `ODESSA-003` | Fingerprint | Fingerprint option is absent from Settings | `FAIL` | `P2` | TRY23 | User report. Determine installed sensor variant, kernel device/module state, HAL/service registration, VINTF, and framework feature declaration. |
| `ODESSA-004` | Install / boot control | Initial boot after installation requires manually flashing the stock partition table | `FAIL` | `P1` | TRY23 | User report. Preserve pre/post-install GPT captures and bootloader state; re-check target-slot boot attributes and the running Recovery boot-control HAL before any further partition-table operation. |
| `ODESSA-005` | Audio | Audio works, but individual playback/capture paths are not fully verified | `PARTIAL` | `P2` | TRY23 | User reports audio works on TRY25. Separately test speaker, earpiece, microphones, headset, call audio, and scrcpy capture before marking the area complete. |
| `ODESSA-006` | Camera | Auxiliary cameras need a curated Aperture selector | `PARTIAL` | `P2` | TRY23 | Enabling Aperture auxiliary cameras exposes working ultrawide ID `3` and macro ID `4`, but also monochrome depth ID `2` and duplicate main-camera processing IDs `6` and `7`. Candidate now ignores `2`, `6`, and `7`; rebuild and hardware-test that only main, ultrawide, and macro remain. |

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

## Update Rules

1. Update the baseline whenever the installed build or physical device changes.
2. Change a status only from direct observation on the stated baseline.
3. Record the build, date, test scope, and evidence for every `PASS`, `FAIL`, or `PARTIAL` result.
4. Add a stable `ODESSA-NNN` row to Open Issues before diagnosing a new defect.
5. Move an issue to Resolved Bring-Up Issues only after the fix is hardware-verified; retain its ID.
6. Never put serial numbers, IMEI/MEID, phone numbers, accounts, Wi-Fi credentials, Bluetooth addresses, precise locations, or tokens in this file.
