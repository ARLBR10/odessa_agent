# TequilaOS Hardware Baseline

Reference build: `tequila-uno-20240117-0816-UNOFFICIAL-odessa`, Android 14.

Record results on the currently installed ROM before replacing it. Use `PASS`, `FAIL`, `PARTIAL`, `LIKELY`, `UNTESTED`, or `NOT PRESENT`; add exact reproduction steps for every failure. `LIKELY` means the user recalls that the test previously worked but could not repeat it at this checkpoint; it is not a validated pass. Do not include phone numbers, account names, Wi-Fi credentials, Bluetooth addresses, IMEI/MEID, serial numbers, or other personal data.

| Area | Test | Result | Notes/log reference |
| --- | --- | --- | --- |
| Boot | Cold boot reaches lock screen | PASS | User-confirmed on TequilaOS |
| Boot | Warm reboot completes | PASS | Recovery returned to Android; `sys.boot_completed=1` |
| Power | Shutdown completes | PASS | User-confirmed on TequilaOS |
| Power | Charging while Android is off | PASS | User-confirmed on TequilaOS |
| Storage | PIN/password unlock after reboot | PASS | User-confirmed on TequilaOS |
| Storage | File-based encryption reported active | PASS | Verified by read-only properties on 2026-07-12 |
| Slots | Active slot and A/B state reported correctly | PASS | `_a` active during 2026-07-12 inventory |
| Cellular | SIM detected | PASS | User-confirmed on TequilaOS |
| Cellular | Incoming and outgoing voice calls | LIKELY | A normal call worked previously; user recalls both directions working but could not retest them at this checkpoint |
| Cellular | Incoming and outgoing SMS | LIKELY | User recalls send and receive working but could not retest them at this checkpoint |
| Cellular | Mobile data | PASS | User-confirmed on TequilaOS |
| Cellular | Airplane mode restores service afterward | LIKELY | User recalls this working but could not retest it at this checkpoint |
| Cellular | VoLTE/IMS registration | UNTESTED | Record carrier and observed state only |
| Wi-Fi | 2.4 GHz association and Internet | PASS | User-confirmed on TequilaOS |
| Wi-Fi | 5 GHz association and Internet | PASS | User-confirmed on TequilaOS |
| Wi-Fi | Hotspot with a client device | PASS | User-confirmed on TequilaOS |
| Bluetooth | Pairing and reconnect | PASS | User-confirmed on TequilaOS |
| Bluetooth | Media audio | PASS | User-confirmed on TequilaOS |
| Bluetooth | Call audio and microphone | LIKELY | User recalls this working but could not retest it at this checkpoint |
| NFC | Tag detection/payment-app NFC availability | PASS | Tag detection user-confirmed; payment behavior not tested |
| USB | Charging | PASS | Verified while connected this session |
| USB | ADB authorization and reconnect | PASS | Authorized ADB worked before and after mode changes |
| USB | File transfer/MTP | UNTESTED | |
| USB | USB tethering | UNTESTED | |
| Audio | Earpiece | PASS | User-confirmed during a normal call |
| Audio | Loudspeaker | PASS | User-confirmed on TequilaOS |
| Audio | Main microphone | PASS | User-confirmed directly and during a normal call |
| Audio | Secondary/noise-cancel microphone | UNTESTED | |
| Audio | Wired or USB audio | UNTESTED | |
| Haptics | Vibration and notification feedback | PASS | User-confirmed on TequilaOS |
| Camera | Main rear photo/video/focus/flash | PASS | Main camera photo and video user-confirmed; focus/flash not separately recorded |
| Camera | Other rear camera IDs and modes | FAIL | User reports only one rear camera worked |
| Camera | Front photo/video | PASS | User-confirmed on TequilaOS |
| Camera | Third-party Camera2 application | UNTESTED | |
| Location | GNSS cold fix | UNTESTED | GPS navigation works, but cold-fix timing was not measured |
| Location | GNSS warm fix | PASS | GPS navigation obtained a working location; detailed fix timing not measured |
| Biometrics | Fingerprint enroll/unlock/reboot persistence | PASS | Unlock and persistence across reboot user-confirmed |
| Sensors | Proximity during call | LIKELY | User recalls this working but could not retest it at this checkpoint |
| Sensors | Ambient light/adaptive brightness | UNTESTED | |
| Sensors | Accelerometer/rotation | PASS | Screen rotation user-confirmed |
| Sensors | Gyroscope | UNTESTED | |
| Sensors | Magnetometer/compass | UNTESTED | |
| Display | Brightness range and automatic brightness | PARTIAL | Manual brightness works; automatic brightness untested |
| Display | Touch, multitouch, and edge response | PASS | Touch and multitouch user-confirmed; edge response not separately measured |
| Display | Rotation and gestures | PARTIAL | Rotation works; gestures not separately tested |
| Suspend | Screen-off suspend and resume | PASS | User-confirmed on TequilaOS |
| Battery | Idle drain over a recorded interval | PARTIAL | User reports reasonable drain; no measured interval recorded |
| Thermal | Sustained load without shutdown | UNTESTED | |
| Charging | Charging rate and battery reporting | PASS | User reports normal charging rate and reporting |
| Recovery | Installed recovery boots | PASS | Custom recovery booted; ADB available after Enable ADB; no write operation performed |
| Fastbootd | Userspace fastboot is detected | PASS | `is-userspace: yes`; logical system/vendor/product visible |

Emergency-call behavior must eventually be validated before release, but do not place a live emergency call merely to populate this baseline. Verify the emergency dialer UI and arrange any live test only through an appropriate local non-emergency procedure.
