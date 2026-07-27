#!/usr/bin/env bash
# Watch what the phone exposes over USB, printing one timestamped line per change.
#
# HOST ONLY. Sends nothing to the phone; it only polls the host's USB device
# list and the adb/fastboot device lists.
#
# Why not just `adb devices`: adb only sees a device once adbd is up and the
# ADB interface is exposed. Polling lsusb also catches an enumeration that
# never reaches adbd, which is exactly the distinction we need when diagnosing
# a boot that dies before `on boot`. 22b8 is Motorola (bootloader / MBM),
# 18d1 is Google (the AOSP adb/fastbootd gadget).
#
# Usage: tools/watch-usb.sh [logfile]
# Stop with Ctrl-C.

set -u
log=${1:-usb-watch-$(date +%Y%m%d-%H%M%S).log}
prev=""

printf 'Watching USB. Logging to %s\nStop with Ctrl-C.\n\n' "$log"

while true; do
    usb=$(lsusb 2>/dev/null | grep -Ei '22b8:|18d1:' | sed 's/^.*ID /ID /' | paste -sd'; ' -)
    adb=$(adb devices 2>/dev/null | awk 'NR>1 && NF {print $2}' | paste -sd',' -)
    fb=$(fastboot devices 2>/dev/null | awk 'NF {print $2}' | paste -sd',' -)

    cur="usb=[${usb:-none}] adb=[${adb:-none}] fastboot=[${fb:-none}]"
    if [ "$cur" != "$prev" ]; then
        printf '%s  %s\n' "$(date +%H:%M:%S)" "$cur" | tee -a "$log"
        prev=$cur
    fi
    sleep 0.3
done
