# Kernel Bisection: Recovery-Only Slot-B Test

Use this procedure for the next Android-common Linux `4.14.284` boundary
candidate after the `4.14.282` Recovery pass and `4.14.286` Recovery failure.
It tests only whether the candidate
kernel can start the known Lineage Recovery image. It does **not** test
Android, install an OTA, flash a ROM, copy firmware, or modify dynamic
partitions.

## Fixed test model

- Known good: TequilaOS on slot A with Linux `4.14.190-Amber`.
- Current result: `4.14.282-perf+` reached Lineage Recovery visually; the
  package-verified `4.14.286` candidate returned to bootloader before Recovery.
- Candidate under test: a recovery image whose kernel release is exactly
  `4.14.284-perf+`.
- Allowed slot-B writes: `recovery_b`, `dtbo_b`, and `vbmeta_b` only.
- Never write: slot-A partitions, `boot_b`, logical partitions, `super`,
  low-level firmware, identity/calibration partitions, or user data.

Slot B is a disposable diagnostic slot. Slot A is the recovery path. The
bootloader may mark B unbootable after a failed attempt; that is expected and
is not a reason to alter any other partition.

## Artifact gate

Do not start the phone procedure until a host-only build has produced a
complete candidate directory. Substitute its actual path below for
`$CANDIDATE`; do not guess or use mutable files under `out/`.

```zsh
# HOST ONLY
export CANDIDATE="$PWD/lineageos/.downloads/diagnostic-recovery-4.14.284-spf-off-rng-fix-YYYYMMDD"
test -f "$CANDIDATE/SOURCE-PROVENANCE.md" \
  -a -f "$CANDIDATE/SHA256SUMS.txt" \
  -a -f "$CANDIDATE/recovery.img" \
  -a -f "$CANDIDATE/dtbo.img" \
  -a -f "$CANDIDATE/vbmeta.img" || exit 1
(cd "$CANDIDATE" && sha256sum --check SHA256SUMS.txt)
```

Expected result: every listed file reports `OK`. Stop if any file is missing
or a hash differs.

Before proceeding, review `SOURCE-PROVENANCE.md` and confirm all of the
following:

- The source boundary is the authoritative Android-common `4.14.284`
  milestone, not a later stable file borrowed to make compilation succeed.
- Any Motorola compatibility adaptation is documented and uses only code valid
  at or before that boundary.
- Speculative page fault remains disabled and the Qualcomm early-RNG correction
  is recorded if it is part of the candidate.
- The recovery ramdisk, embedded base DTB, embedded recovery DTBO, header v2
  metadata, command line, and external `dtbo.img` match the established
  Lineage diagnostic template, except for the kernel-dependent AVB changes.
- AVB verification passed for `recovery.img`, `dtbo.img`, and top-level
  `vbmeta.img` with the candidate's exact artifacts.

## Build Each Stable Boundary

This is a **HOST ONLY** procedure. Build every midpoint in a separate Git
worktree from the same Motorola parent. Do not merge a candidate into the
normal `lineage-23.2` branch, and do not build a later candidate on top of an
earlier candidate. That would make the bisection result ambiguous.

The known parent is
`92a96be148a072185131f60977af463c918b58cd` (`4.14.190-perf+`). The
authoritative upstream history is Android Common Kernel's
`deprecated/android-4.14-stable` branch. The final known merge is
`70f404ff7c1f`; it exists only as a resolution reference, not as a source of
files to copy into an earlier boundary.

Start from the primary kernel checkout and replace only the version and worktree
path for each attempt:

```zsh
# HOST ONLY: run from lineageos/kernel/motorola/sm6150.
export VERSION=4.14.284
export BASE=92a96be148a072185131f60977af463c918b58cd
export WORKTREE="/tmp/opencode/sm6150-${VERSION}-bisect"

git status --short
git fetch --no-tags https://android.googlesource.com/kernel/common \
  refs/heads/deprecated/android-4.14-stable:refs/remotes/android-common/deprecated/android-4.14-stable
git log --format='%H %s' --all \
  --grep="^Merge ${VERSION} into android-4.14-stable$" -1
git worktree add --detach "$WORKTREE" "$BASE"
```

Expected result: the first command has no output, the log command prints one
authoritative merge commit for the requested version, and the worktree is
checked out at the Motorola parent. If the version search returns zero or more
than one result, stop and record the ambiguity; do not choose a commit by
date, tag name, or approximate version.

Set `UPSTREAM` to the full hash printed by `git log`, then begin the merge in
the disposable worktree:

```zsh
# HOST ONLY: run from "$WORKTREE" only.
export UPSTREAM=REPLACE_WITH_THE_FULL_HASH_FROM_THE_PREVIOUS_COMMAND
git merge --no-ff --no-commit "$UPSTREAM"
git status --short
```

A clean merge is uncommon. Resolve conflicts by preserving Motorola hardware
integration while applying only the upstream behavior present at `$UPSTREAM`.
For every resolution, record the conflicting paths, why the resolution is
needed, and the source commit(s) used. The following rules are mandatory:

- Do not copy a file, hunk, API, or conflict resolution from Linux `4.14.271`
  or later into the `4.14.270` candidate.
- Do not replace a difficult file wholesale with its `4.14.336` version.
- Keep Android-common `mm/memory.c` byte-identical at the requested boundary.
  The Motorola tree's separately advanced MM interfaces may require narrow,
  documented compatibility bridges elsewhere.
- Keep `CONFIG_SPECULATIVE_PAGE_FAULT=n`; it is an explicit bounded-candidate
  condition, not a workaround to conceal a result.
- Carry the Qualcomm early-RNG correction in the API form valid at this
  boundary and document it separately from upstream stable changes.
- Do not use automatic `rerere` results without reviewing their diff. A cached
  4.14.336 resolution can silently import behavior that does not exist yet.

Before resolving an intermediate version, validate the resolution method once
against the known final merge. In a separate disposable worktree from `$BASE`,
merge Android-common `014241ad77dda0eafbdf671d5b8e86917d8ec97e`, apply only
the reviewed final-merge resolutions, and require its staged tree to equal
`70f404ff7c1f^{tree}`. Do not continue if it differs. This proves that the
resolution recipe can reproduce the reviewed 4.14.336 integration before it is
adapted backward for an earlier API.

```zsh
# HOST ONLY: validation worktree; do not run this in the main kernel checkout.
export FINAL_UPSTREAM=014241ad77dda0eafbdf671d5b8e86917d8ec97e
export FINAL_MERGE=70f404ff7c1fb97460cef91e1f89d594a2959358
export FINAL_WORKTREE=/tmp/opencode/sm6150-4.14.336-replay
git worktree add --detach "$FINAL_WORKTREE" "$BASE"

# HOST ONLY: run from "$FINAL_WORKTREE". Resolve only the already reviewed
# final-merge conflicts, then compare the staged result to the known merge.
git merge --no-ff --no-commit "$FINAL_UPSTREAM"
git diff --cached --exit-code "$FINAL_MERGE"

# HOST ONLY: run from the main kernel checkout after the comparison succeeds.
git worktree remove "$FINAL_WORKTREE"
```

The comparison produces no output and exits zero only for an exact match. Do
not delete a worktree with `rm -rf`; use `git worktree remove` after preserving
the required logs.

After all conflicts are resolved, verify that the selected upstream
`mm/memory.c` was preserved and create a candidate-only commit:

```zsh
# HOST ONLY: run from "$WORKTREE" only.
git diff --cached --check
git show "$UPSTREAM:mm/memory.c" | sha256sum
git show :mm/memory.c | sha256sum
git commit -m "bisect: merge Android common ${VERSION} for odessa recovery test"
git rev-parse HEAD
git rev-parse HEAD^{tree}
```

The two `mm/memory.c` hashes must match. Save the candidate commit and tree
hash in `SOURCE-PROVENANCE.md`, along with the full upstream hash, parent hash,
all compatibility bridges, config changes, toolchain, build command, and build
log path. A build failure is a valid host-only result: document it and repair
only the boundary-valid interface skew before rebuilding. Never substitute a
later stable kernel merely to obtain an image.

Package only a successful candidate using the established one-variable recovery
composition: replace the recovery kernel payload, regenerate its AVB footer and
dependent diagnostic vbmeta, retain the established external DTBO and matching
boot/product/system/vendor control images, then verify AVB and component
equality. Place the complete output in the `$CANDIDATE` directory required by
the artifact gate above. Remove the disposable worktree only after its
provenance, source commit, logs, and artifact hashes have been retained under
ignored local diagnostics, using `git worktree remove "$WORKTREE"` from the
main kernel checkout.

## Preflight

These commands query the phone only. They must show product `odessa`, two
slots, unlocked flashing state, and active slot A. Ensure the battery is at
least 60%, use a stable USB connection, and keep the accepted Motorola Software
Fix Rescue route available. Do not proceed if Android on slot A is not fully
booted first.

```zsh
# READ ONLY: Android must be running on the known-good slot A.
adb wait-for-device
adb shell getprop ro.product.device
adb shell getprop ro.boot.slot_suffix
adb shell getprop sys.boot_completed
adb shell uname -r

# DESTRUCTIVE: reboots only; it does not write or erase a partition.
adb reboot bootloader

# READ ONLY: bootloader fastboot.
fastboot getvar product
fastboot getvar current-slot
fastboot getvar slot-count
fastboot getvar securestate
fastboot getvar battery-voltage
```

Expected values include `odessa`, `_a`/`a`, `1`, a `4.14.190` kernel, slot
count `2`, and `securestate: flashing_unlocked`. `getvar` writes its result to
stderr on many fastboot versions. Stop on any mismatch or low battery.

## Install And Boot The Candidate

**DESTRUCTIVE:** this overwrites only `recovery_b`, `dtbo_b`, and `vbmeta_b`
and then marks slot B active. It does not intentionally erase data, but an
invalid image can bootloop and B can be marked unbootable. The recovery path is
to select slot A again in the rollback section; the Motorola Software Fix
Rescue procedure remains the full fallback.

Run this as one command group only after the preflight passed:

```zsh
# DESTRUCTIVE: explicit _b partition names prevent alias/active-slot mistakes.
fastboot flash dtbo_b "$CANDIDATE/dtbo.img" || exit 1
fastboot flash recovery_b "$CANDIDATE/recovery.img" || exit 1
fastboot flash vbmeta_b "$CANDIDATE/vbmeta.img" || exit 1
fastboot set_active b || exit 1
fastboot reboot recovery
```

Expected fastboot result: each flash ends with `OKAY`, `set_active` succeeds,
and the device reaches the purple Lineage Recovery UI. An unlocked-device
rollback-index warning for this diagnostic test vbmeta is expected. Do not
flash an unsuffixed partition name, and do not use `fastboot update`,
`fastboot boot`, `erase`, `format`, `dd`, sideload, or an OTA.

## Record The Result

Wait up to five minutes. Do not keep retrying an unresponsive device. A purple
Lineage Recovery screen is a booting result. Enable ADB in its menu, then run:

```zsh
# READ ONLY: run only after the candidate visibly reaches Lineage Recovery.
adb wait-for-device
adb shell getprop ro.product.device
adb shell getprop ro.boot.slot_suffix
adb shell uname -r
adb shell sha256sum /dev/block/by-name/recovery_b
adb shell sha256sum /dev/block/by-name/dtbo_b
adb shell sha256sum /dev/block/by-name/vbmeta_b
```

Record the exact output locally, redacting serial numbers and any unrelated
device properties. A fully verified passing candidate requires `odessa`, `_b`,
and `4.14.284-perf+`. Compare recovery and DTBO hashes to `SHA256SUMS.txt`.
`vbmeta_b` is a padded partition, so its whole-device hash will normally differ
from the small `vbmeta.img`; do not call that a mismatch.

Classify the test as follows:

| Observation | Bisection result |
| --- | --- |
| Purple Lineage Recovery and ADB report `4.14.284-perf+` | PASS: regression is in `4.14.285` through `4.14.286` inclusive. |
| Purple Lineage Recovery appears but no host USB device enumerates | VISUAL PASS for kernel-to-Recovery startup; record the USB failure separately, restore A, and do not claim image/slot verification. |
| Bootloop or bootloader return before Recovery UI | FAIL: regression is in `4.14.283` through `4.14.284` inclusive. |
| Any identity, slot, artifact-hash, or kernel-release mismatch | INVALID: restore A; do not use this result to narrow the range. |

## Immediate Rollback

Perform this after **every** result, including PASS. If the candidate reached
recovery, first reboot it to bootloader. If it failed and already returned to
bootloader, skip that first command. The remaining commands change only the
active-slot flag back to known-good A and reboot TequilaOS; they do not erase
data or overwrite an image.

```zsh
# DESTRUCTIVE: run this only when the candidate reached recovery and ADB works.
adb reboot bootloader

# DESTRUCTIVE: selects known-good slot A, then boots it.
# For a failed candidate, begin here after it returns to bootloader.
fastboot devices
fastboot set_active a
fastboot reboot

# READ ONLY: confirm the recovery path actually returned.
adb wait-for-device
adb shell getprop ro.product.device
adb shell getprop ro.boot.slot_suffix
adb shell getprop sys.boot_completed
adb shell uname -r
```

Expected result: `odessa`, `_a`, `1`, and the known-good `4.14.190-Amber`
kernel. If Android A does not boot, stop. Enter bootloader and use only the
reviewed Motorola Software Fix Rescue fallback in
`docs/stock-restore-rpas31-4-3-9.md`; do not experiment with manual stock
fastboot scripts.

## After The Test

Update `MEMORY.md` with the candidate's exact upstream commit, source commit,
artifact hashes, preflight facts, observed result, and successful slot-A
rollback. Keep raw recovery logs and any device identifiers in ignored local
artifacts only. The next midpoint is selected only after recording a valid
PASS or FAIL result.
