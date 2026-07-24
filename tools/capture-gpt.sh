#!/system/bin/sh
# Capture GPT metadata from every whole-disk block device.
#
# READ ONLY. This script never writes to a block device. It reads only the
# GPT regions: the protective MBR, the primary GPT header and partition entry
# array at the start of each disk, and the backup entry array and header at the
# end. That is partition metadata only - names, type/unique GUIDs, start/end
# LBAs, and attribute flags, including the A/B priority, tries-remaining,
# successful, and unbootable bits this project needs to compare.
#
# It does not read partition payload, user data, or any identity, calibration,
# DRM, or attestation partition content.
#
# Usage, from Lineage Recovery with root ADB:
#   adb push tools/capture-gpt.sh /tmp/capture-gpt.sh
#   adb shell sh /tmp/capture-gpt.sh <label>
#   adb pull /tmp/gptcap-<label>
#
# Run it once before sideloading and once after the install completes but
# BEFORE rebooting, then diff the two captures on the host.

LABEL="${1:-unlabeled}"
OUT="/tmp/gptcap-${LABEL}"

# A standard 128-entry x 128-byte partition array is 16384 bytes. How many
# logical blocks that spans depends on the device: four blocks at 4 KiB, but
# thirty-two at 512 bytes. The capture sizes are derived per device below rather
# than fixed, and are kept tight so the capture stays inside GPT structures:
#   head = protective MBR + primary header + primary entry array
#   tail = backup entry array + backup header
# Nothing beyond that is read, so no partition payload is captured.
ARRAY_BYTES=16384

rm -rf "$OUT"
mkdir -p "$OUT" || exit 1

echo "capture label : $LABEL"
echo "captured at   : $(date 2>/dev/null)"
echo

for sysdev in /sys/class/block/sd?; do
    [ -e "$sysdev" ] || continue
    name=$(basename "$sysdev")
    dev="/dev/block/$name"
    [ -b "$dev" ] || continue

    sectors=$(cat "$sysdev/size" 2>/dev/null)
    lbs=$(cat "$sysdev/queue/logical_block_size" 2>/dev/null)
    [ -n "$sectors" ] && [ "$sectors" -gt 0 ] || continue
    [ -n "$lbs" ] && [ "$lbs" -gt 0 ] || lbs=512

    # /sys/class/block/*/size is always in 512-byte units regardless of the
    # device's logical block size.
    total=$(( sectors * 512 / lbs ))

    arr_blocks=$(( (ARRAY_BYTES + lbs - 1) / lbs ))
    head_count=$(( 2 + arr_blocks ))
    tail_count=$(( 1 + arr_blocks ))
    [ "$total" -gt $(( head_count + tail_count )) ] || continue

    dd if="$dev" of="$OUT/$name.head" bs="$lbs" count="$head_count" 2>/dev/null
    dd if="$dev" of="$OUT/$name.tail" bs="$lbs" count="$tail_count" \
        skip=$(( total - tail_count )) 2>/dev/null

    echo "$name  logical_block_size=$lbs  blocks=$total  bytes=$(( sectors * 512 ))" \
         "head=$head_count tail=$tail_count"
done

echo
echo "--- /proc/partitions ---"
cat /proc/partitions 2>/dev/null

echo
echo "--- by-name symlinks ---"
ls -l /dev/block/bootdevice/by-name 2>/dev/null

echo
echo "--- capture checksums ---"
sha256sum "$OUT"/* 2>/dev/null
