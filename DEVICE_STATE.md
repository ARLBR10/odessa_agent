# Odessa Device State

Last updated: 2026-08-04 (TRY23 user testing)

This file is the current hardware and regression dashboard for the physical
Motorola Moto G9 Plus (`odessa`). It records observations, not assumptions.
Detailed commands, logs, hashes, and investigations belong in `journals/` or
`docs/`; link them here as evidence.

## Test Baseline

| Field | Value |
| --- | --- |
| Device | Moto G9 Plus (`odessa`) |
| Model/SKU | `XT2087-1`, Brazil |
| Build | `lineage-23.2-20260804-TRY23-UNOFFICIAL-odessa.zip` |
| OTA SHA-256 at verification | `7165120cfa144730deafe104432b03c47c222ca75c5f575bcca7650e00746309` |
| Exact payload Recovery SHA-256 | `2b80df2a644340dc9391b7237b849b36ea6f4daa793c8763591a5956f7f6a171` |
| Installation | User reports TRY23 update installed successfully |
| Security context | Unofficial userdebug build; final release security validation not complete |

The named TRY23 ZIP shares the mutable `lineage_odessa-ota.zip` inode. The hash
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
| Boot | Android reaches LineageOS UI | `PASS` | TRY18 reached Setup Wizard; user reports installed TRY23 works |
| Boot | BPF loader completes | `PASS` | Hardware markers reached `bpf-done`; see `MEMORY.md` |
| Recovery | RAM-boot exact Recovery | `PASS` | TRY23 exact payload Recovery booted |
| Recovery | Installed Recovery boot | `UNTESTED` | TRY23 was RAM-booted; installed-partition Recovery has not been separately reported |
| Update | A/B OTA installation | `PASS` | User reports TRY23 update installed successfully |
| Update | Automatic first boot after installation | `FAIL` | User reports stock partition-table flashing is still required before initial boot; `ODESSA-004` |
| Display | Panel output and boot animation | `PASS` | GPU/display path reached Setup Wizard and TRY23 UI |
| Graphics | Adreno acceleration initializes | `PASS` | TRY23 reaches rendered Android UI; ZAP fix was originally isolated in TRY15 |
| Input | Touchscreen in Recovery | `PASS` | TRY23 auto-loads modules; touch works without ADB commands |
| Input | Touchscreen in Android | `PASS` | User reports touch works after installing TRY23 |
| Input | Physical buttons | `PARTIAL` | Recovery navigation observed; full key/long-press matrix not run |
| Input | Vibration / haptics | `PASS` | User reports phone vibration works on TRY23 |
| Encryption | Fresh userdata encryption and unlock | `UNTESTED` | Must be tested on the current baseline |
| Update | Slot fallback and failed-update behavior | `UNTESTED` | Successful update alone does not validate fallback |
| Update | In-system updater flow | `UNTESTED` | Current update path details not fully recorded |
| Telephony | SIM detection | `UNTESTED` | |
| Telephony | Voice calls, incoming and outgoing | `UNTESTED` | Include proximity, earpiece, microphone, speaker, and hangup |
| Telephony | SMS/MMS | `UNTESTED` | |
| Telephony | Mobile data | `UNTESTED` | Test LTE attachment and data transfer |
| Telephony | Emergency calling | `UNTESTED` | Use a lawful non-disruptive validation plan; do not place test emergency calls casually |
| Connectivity | Wi-Fi | `FAIL` | User reports Wi-Fi does not work on TRY23; `ODESSA-001` |
| Connectivity | Bluetooth | `FAIL` | User reports Bluetooth does not work on TRY23; `ODESSA-002` |
| Connectivity | NFC | `UNTESTED` | Regional SKU support must be verified |
| Connectivity | USB data / ADB in Android | `UNTESTED` | Recovery ADB is separately proven |
| Audio | Speaker, earpiece, microphones, headset | `PARTIAL` | scrcpy audio capture throws `UnsupportedOperationException`; physical audio paths remain untested; `ODESSA-005` |
| Camera | Front camera preview and capture | `PASS` | User reports the front camera works on TRY23 |
| Camera | Primary rear camera preview and capture | `PASS` | User reports one rear camera works on TRY23 |
| Camera | Auxiliary rear cameras | `FAIL` | Additional rear cameras are missing from the camera interface; `ODESSA-006` |
| Camera | Camera flash | `PASS` | User reports flash works on TRY23 |
| Camera | Video recording and playback | `UNTESTED` | Test front/rear recording, audio, stabilization, and common resolutions |
| Sensors | Accelerometer, gyro, light, proximity, compass | `UNTESTED` | |
| Location | GNSS fix | `UNTESTED` | Test cold and warm fixes without leaking location data |
| Biometrics | Fingerprint enrollment and unlock | `FAIL` | Fingerprint controls are absent from Settings; sensor detection is unconfirmed; `ODESSA-003` |
| Power | Charging, battery reporting, thermal behavior | `UNTESTED` | Include powered-off charging and USB current behavior |
| Power | Suspend, wake, and overnight idle | `UNTESTED` | |
| Power | Screen sleep | `PASS` | User reports the display enters sleep on TRY23; wake and deep suspend remain separate tests |
| Media | Hardware video encode/decode | `UNTESTED` | |
| Security | SELinux enforcing with no broad bypass | `UNTESTED` | Userdebug observations do not establish release readiness |
| Security | Verified Boot and release signing | `UNTESTED` | Current artifacts use bring-up signing/security limitations |
| Optional | Google apps | `UNTESTED` | Keep separate from base-ROM support |
| Optional | Play Integrity / banking / DRM | `UNTESTED` | No claim permitted without exact-build testing |
| Optional | Magisk/root | `UNTESTED` | Keep separate from the unrooted base ROM |

## Open Issues

| ID | Area | Summary | Status | Priority | First seen | Evidence / Next step |
| --- | --- | --- | --- | --- | --- | --- |
| `ODESSA-001` | Wi-Fi | Wi-Fi does not work | `FAIL` | `P2` | TRY23 | User report. Capture framework, HAL, kernel, firmware-loading, and module state before attributing it to the Xiaomi networking/BPF import. |
| `ODESSA-002` | Bluetooth | Bluetooth does not work | `FAIL` | `P2` | TRY23 | User report. Capture Bluetooth service/HAL state, UART transport, firmware, and kernel logs; investigate shared causes with Wi-Fi without assuming one. |
| `ODESSA-003` | Fingerprint | Fingerprint option is absent from Settings | `FAIL` | `P2` | TRY23 | User report. Determine installed sensor variant, kernel device/module state, HAL/service registration, VINTF, and framework feature declaration. |
| `ODESSA-004` | Install / boot control | Initial boot after installation requires manually flashing the stock partition table | `FAIL` | `P1` | TRY23 | User report. Preserve pre/post-install GPT captures and bootloader state; re-check target-slot boot attributes and the running Recovery boot-control HAL before any further partition-table operation. |
| `ODESSA-005` | Audio | scrcpy cannot create an `AudioRecord`; overall audio status unknown | `PARTIAL` | `P2` | TRY23 | Reported exception: `java.lang.UnsupportedOperationException: Cannot create AudioRecord`. Test local media playback/recording and calls separately, then collect AudioFlinger/audio HAL state and scrcpy version/options. |
| `ODESSA-006` | Camera | Only one rear camera is exposed; auxiliary rear cameras are missing | `FAIL` | `P2` | TRY23 | User report. Enumerate camera provider IDs and characteristics, compare physical sensor/module detection with the verified SKU, and inspect provider/HAL logs without assuming every lens has a separate public camera ID. |

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

## Update Rules

1. Update the baseline whenever the installed build or physical device changes.
2. Change a status only from direct observation on the stated baseline.
3. Record the build, date, test scope, and evidence for every `PASS`, `FAIL`, or `PARTIAL` result.
4. Add a stable `ODESSA-NNN` row to Open Issues before diagnosing a new defect.
5. Move an issue to Resolved Bring-Up Issues only after the fix is hardware-verified; retain its ID.
6. Never put serial numbers, IMEI/MEID, phone numbers, accounts, Wi-Fi credentials, Bluetooth addresses, precise locations, or tokens in this file.
