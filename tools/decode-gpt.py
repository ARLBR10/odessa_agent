#!/usr/bin/env python3
"""Decode and diff GPT captures made by tools/capture-gpt.sh.

HOST ONLY. Reads capture files produced on the phone; never touches a device.

The captures contain only GPT metadata. This tool validates both GPT copies
and prints the partition table with the Qualcomm A/B attribute byte decoded, so
a before/after pair can be compared byte-meaningfully instead of by eye.

Usage:
    tools/decode-gpt.py show <capture-dir>
    tools/decode-gpt.py diff <before-dir> <after-dir>
"""

import sys
import zlib
from pathlib import Path

# Offsets within the GPT header, from hardware/qcom-caf/bootctrl/gpt-utils.
HDR_SIG = 0
HDR_SIZE = 12
HDR_CRC = 16
HDR_CURRENT_LBA = 24
HDR_BACKUP_LBA = 32
HDR_PENTRIES_LBA = 72
HDR_PENTRY_COUNT = 80
HDR_PENTRY_SIZE = 84
HDR_PENTRY_CRC = 88

# Offsets within a partition entry.
E_TYPE_GUID = 0
E_UNIQUE_GUID = 16
E_FIRST_LBA = 32
E_LAST_LBA = 40
E_ATTR = 48
E_NAME = 56
E_NAME_SIZE = 72

# The Qualcomm A/B attribute byte sits at attribute offset + 6.
AB_BYTE = E_ATTR + 6
AB_ACTIVE = 0x1 << 2
AB_SUCCESSFUL = 0x1 << 6
AB_UNBOOTABLE = 0x1 << 7

SIGNATURE = b"EFI PART"


def u32(buf, off):
    return int.from_bytes(buf[off:off + 4], "little")


def u64(buf, off):
    return int.from_bytes(buf[off:off + 8], "little")


def decode_ab(byte):
    flags = []
    if byte & AB_ACTIVE:
        flags.append("active")
    if byte & AB_SUCCESSFUL:
        flags.append("successful")
    if byte & AB_UNBOOTABLE:
        flags.append("unbootable")
    # The low bits carry the retry/priority counter; 0x3F is the value the
    # driver writes when it makes a slot active, 0x00 when it deactivates one.
    retry = byte & 0x03
    if retry:
        flags.append(f"retry={retry}")
    return ",".join(flags) if flags else "-"


class Gpt:
    def __init__(self, path):
        self.path = path
        self.data = Path(path).read_bytes()
        self.lbs = None
        self.hdr_off = None
        self.error = None
        self.parts = []
        self.hdr_crc_ok = False
        self.pentry_crc_ok = False
        self._parse()

    def _find_header(self):
        # A head capture holds the header in the second block; a tail capture
        # holds it in the final block. Scan every block-aligned offset rather
        # than assuming, so an unexpected geometry is decoded instead of being
        # reported as unreadable.
        for lbs in (4096, 512):
            nblocks = len(self.data) // lbs
            if nblocks < 2:
                continue
            for idx in range(nblocks):
                off = idx * lbs
                if self.data[off:off + 8] == SIGNATURE:
                    return lbs, off, idx, nblocks
        return None, None, None, None

    def _parse(self):
        lbs, off, idx, nblocks = self._find_header()
        if off is None:
            self.error = "no GPT signature found"
            return
        self.lbs, self.hdr_off = lbs, off
        d = self.data

        hdr_size = u32(d, off + HDR_SIZE)
        if not 92 <= hdr_size <= lbs:
            self.error = f"implausible header size {hdr_size}"
            return

        stored_hdr_crc = u32(d, off + HDR_CRC)
        hdr = bytearray(d[off:off + hdr_size])
        hdr[HDR_CRC:HDR_CRC + 4] = b"\0\0\0\0"
        self.hdr_crc_ok = zlib.crc32(bytes(hdr)) == stored_hdr_crc

        current_lba = u64(d, off + HDR_CURRENT_LBA)
        pentries_lba = u64(d, off + HDR_PENTRIES_LBA)
        count = u32(d, off + HDR_PENTRY_COUNT)
        esize = u32(d, off + HDR_PENTRY_SIZE)
        stored_pentry_crc = u32(d, off + HDR_PENTRY_CRC)

        if count == 0 or esize < 128 or count * esize > 1 << 20:
            self.error = f"implausible entry array: count={count} size={esize}"
            return

        # Translate the absolute entry LBA into an offset inside this capture.
        file_start_lba = current_lba - idx
        rel = pentries_lba - file_start_lba
        earr_off = rel * lbs
        earr_len = count * esize
        if rel < 0 or earr_off + earr_len > len(d):
            self.error = (
                f"entry array at LBA {pentries_lba} is outside the captured "
                f"region (capture starts at LBA {file_start_lba})"
            )
            return

        earr = d[earr_off:earr_off + earr_len]
        self.pentry_crc_ok = zlib.crc32(earr) == stored_pentry_crc

        for i in range(count):
            e = earr[i * esize:(i + 1) * esize]
            first = u64(e, E_FIRST_LBA)
            last = u64(e, E_LAST_LBA)
            if first == 0 and last == 0:
                continue
            name = e[E_NAME:E_NAME + E_NAME_SIZE].decode("utf-16-le", "replace")
            name = name.split("\x00")[0]
            self.parts.append({
                "index": i,
                "name": name,
                "type_guid": e[E_TYPE_GUID:E_UNIQUE_GUID],
                "unique_guid": e[E_UNIQUE_GUID:E_FIRST_LBA],
                "first": first,
                "last": last,
                "attr": u64(e, E_ATTR),
                "ab": e[AB_BYTE],
            })


def show(directory):
    files = sorted(Path(directory).glob("*.head")) + \
        sorted(Path(directory).glob("*.tail"))
    if not files:
        sys.exit(f"no capture files in {directory}")
    for f in files:
        g = Gpt(f)
        print(f"\n=== {f.name} ===")
        if g.error:
            print(f"  UNREADABLE: {g.error}")
            continue
        print(f"  logical block size : {g.lbs}")
        print(f"  header CRC         : {'OK' if g.hdr_crc_ok else 'BAD'}")
        print(f"  entry array CRC    : {'OK' if g.pentry_crc_ok else 'BAD'}")
        print(f"  partitions         : {len(g.parts)}")
        for p in g.parts:
            print(f"    {p['index']:3d} {p['name']:<20} "
                  f"{p['first']:>10}-{p['last']:<10} "
                  f"ab=0x{p['ab']:02x} {decode_ab(p['ab'])}")


def diff(before, after):
    b_files = {f.name: f for f in Path(before).glob("*.[ht]*")}
    a_files = {f.name: f for f in Path(after).glob("*.[ht]*")}
    names = sorted(set(b_files) | set(a_files))
    if not names:
        sys.exit("no capture files to compare")

    any_change = False
    for name in names:
        if name not in b_files or name not in a_files:
            print(f"\n=== {name} ===\n  present in only one capture")
            any_change = True
            continue

        gb, ga = Gpt(b_files[name]), Gpt(a_files[name])
        lines = []

        if gb.error or ga.error:
            lines.append(f"  parse: before={gb.error or 'ok'} "
                         f"after={ga.error or 'ok'}")
        if (gb.hdr_crc_ok, gb.pentry_crc_ok) != (ga.hdr_crc_ok, ga.pentry_crc_ok):
            lines.append(
                f"  CRC: header {gb.hdr_crc_ok}->{ga.hdr_crc_ok}, "
                f"entries {gb.pentry_crc_ok}->{ga.pentry_crc_ok}")
        elif not ga.hdr_crc_ok or not ga.pentry_crc_ok:
            lines.append(f"  CRC INVALID IN BOTH: header={ga.hdr_crc_ok} "
                         f"entries={ga.pentry_crc_ok}")

        bp = {p["index"]: p for p in gb.parts}
        ap = {p["index"]: p for p in ga.parts}
        for idx in sorted(set(bp) | set(ap)):
            x, y = bp.get(idx), ap.get(idx)
            if x is None:
                lines.append(f"  +{idx} {y['name']} added")
            elif y is None:
                lines.append(f"  -{idx} {x['name']} REMOVED")
            elif (x["name"], x["first"], x["last"]) != \
                    (y["name"], y["first"], y["last"]):
                lines.append(
                    f"  !{idx} layout changed: "
                    f"{x['name']} {x['first']}-{x['last']} -> "
                    f"{y['name']} {y['first']}-{y['last']}")
            else:
                if x["type_guid"] != y["type_guid"]:
                    lines.append(f"  !{idx} {x['name']} type GUID changed")
                if x["unique_guid"] != y["unique_guid"]:
                    lines.append(f"  !{idx} {x['name']} unique GUID changed")
                if x["ab"] != y["ab"]:
                    lines.append(
                        f"   {idx} {x['name']:<20} ab 0x{x['ab']:02x} "
                        f"({decode_ab(x['ab'])}) -> 0x{y['ab']:02x} "
                        f"({decode_ab(y['ab'])})")

        if lines:
            any_change = True
            print(f"\n=== {name} ===")
            print("\n".join(lines))

    if not any_change:
        print("No differences found in any captured GPT structure.")


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "show":
        show(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "diff":
        diff(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
