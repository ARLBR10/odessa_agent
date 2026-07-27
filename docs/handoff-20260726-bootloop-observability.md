# Handoff: original bootloop remains; retrieve TRY4 zygote log first

Date: 2026-07-26

Read `MEMORY.md` first. This handoff supersedes
`docs/handoff-20260725-usb-gadget.md` as the next-action guide. The XBL/GPT
boot-control fix remains correct and is not under investigation.

## One-paragraph state

The bootloader/partition-table failure is fixed and remains fixed: every OTA in
this session installed with status 0, switched slots, and left a healthy two-slot
partition view. USB was a separate debug-build regression, not the original
bootloop. An insecure build persisted `persist.sys.usb.config=adb` in encrypted
userdata; removing it from a later image did not clear the stored value. A
recovery factory reset removed it and restored the original long-logo failure.
Ramoops is conclusively unusable, and recovery cannot decrypt userdata. TRY4
therefore keeps normal `logcatd` output in `/data/misc/logd` and copies that file
to the exact unencrypted path `/metadata/vold/bootloop-logcat` whenever zygote
restarts. TRY4 just failed all seven retries on slot A and fell back to B. **The
next action is only to boot recovery B and retrieve that exact metadata file
before another Android boot.**

## Current phone state

Read-only bootloader values after the TRY4 test:

```text
product: odessa
current-slot: b
slot-count: 2
has-slot:boot: yes
slot-unbootable:a: yes
slot-retry-count:a: 0
slot-unbootable:b: no
slot-retry-count:b: 5
securestate: flashing_unlocked
battery-voltage: 4461
```

- The phone is in Motorola AP Fastboot.
- Slot A contains TRY4 and exhausted all seven retries.
- Slot B is the automatic fallback and consumed two retries after A failed.
- The user's visual estimate of three fast loops was not the complete A count;
  bootloader metadata is the stronger evidence.
- Both slots contain LineageOS-family diagnostic builds. There is no stock slot.
- The accepted restore path remains the official exact-device RPAS31 package.
- The bootloader partition view is healthy. Do not flash `gpt.bin`, synchronize
  firmware, or revisit XBL/boot-LUN/GPT theories.

The user explicitly authorized the agent to run routine `adb`, `fastboot`, and
focused `fastboot getvar` commands. Destructive operations still require the
normal warning/checkpoint.

## Immediate next action

Do not re-arm A, boot Android, build, flash loose images, or factory-reset.

1. From the current bootloader, run `fastboot reboot recovery`.
2. Ask the user to select **Advanced -> Enable ADB**.
3. Verify recovery B with `adb shell getprop ro.boot.slot_suffix`; expect `_b`.
4. Mount metadata read-only:

   ```sh
   adb shell mount -t ext4 -o ro /dev/block/by-name/metadata /metadata
   ```

5. Check only the exact diagnostic path; do not list `/metadata/vold`:

   ```sh
   adb shell ls -l /metadata/vold/bootloop-logcat
   ```

6. If present, pull only that file to an ignored artifact such as
   `lineageos/.downloads/bootloop-logcat-try4-20260726.txt`, hash it, then unmount
   `/metadata`. Treat it as sensitive: it may contain identifiers and must not be
   committed or quoted unredacted.
7. Analyze zygote/linker/init/SELinux/service failure lines first. Do not start a
   new hypothesis before reading this file.

If the file is absent, unmount metadata and stop. Do not stack another logging
mechanism immediately; first verify from the exact payload whether `logcatd`
started and whether zygote reached an `onrestart` action.

## What was proven this session

### USB was a persisted-state confounder

- TRY2's exact image properties were normal: `ro.debuggable=0`,
  `ro.adb.secure=1`, and no image default for `persist.sys.usb.config`.
- A direct 834-byte slot-B pmsg capture nevertheless contained identifiable
  `adbd`, authentication, and FunctionFS endpoint messages.
- Cause: the earlier insecure image had stored `persist.sys.usb.config=adb` in
  userdata. `persist.*` survives OTA image replacement.
- Recovery factory reset erased userdata and persistent properties. Afterward,
  the rapid USB-associated loop disappeared and the original long-logo failure
  returned.
- Do not investigate DWC3 as the original bootloop. The coherent Qualcomm DWC3
  recovery fix remains valid, but USB gadget composition was only a debug-build
  side regression.

### Ramoops cannot be trusted

- Recovery was confirmed to have neither `/data` nor `/metadata` mounted.
- SysRq was enabled and a deliberate recovery kernel panic was triggered.
- The phone warm-reset to bootloader, then immediate recovery showed an empty
  `/sys/fs/pstore`.
- This proves the dump zone does not retain even a known panic. Do not use pstore
  absence to infer boot stage, and do not add `androidboot.init_fatal_panic` in
  the hope of recovering a dump.

### Recovery cannot decrypt userdata

- Lineage Recovery has the correct metadata-encryption fstab but contains no
  `vold`, `vdc`, `keystore2`, or decrypted dm mapping.
- The saved known-working Pixys recovery was unpacked host-side and also has none
  of those executables.
- Correct decryption needs normal Android's vold/keystore2/Qualcomm Keymaster
  stack, Binder/init sequencing, libraries, linker namespaces, and policy. It is
  not a small recovery fstab fix.
- Raw userdata correctly fails the F2FS magic check because it is metadata
  encrypted. Never attempt to mount the raw userdata block as plaintext or copy
  metadata-encryption keys.

### TRY3 was rejected

- TRY3 relocated the active `logcatd` destination itself to `/metadata/logd` and
  added matching platform policy.
- It bootlooped rapidly, exhausted B, and never created `/metadata/logd`.
- Exact payload audit found boot, DTBO, and product byte-identical to TRY2;
  system/vendor/recovery policy and dependent vbmeta changed.
- All TRY3 `/metadata/logd` changes were reverted. `system/logging` and the
  touched platform file-context code are back to original bytes.

## TRY4 design and artifact

TRY4 is deliberately narrower than TRY3:

- Stock `logcatd` still writes `/data/misc/logd/logcat`.
- `persist.logd.logpersistd=logcatd` and `ro.logd.kernel=true` enable persistent
  all-buffer/kernel logging.
- Normal USB remains secure/non-debuggable; no `persist.sys.usb.config` image
  default is added.
- Zygote critical reboot remains disabled.
- `init.zygote64.rc` has one action:

  ```text
  onrestart copy /data/misc/logd/logcat /metadata/vold/bootloop-logcat
  ```

- Existing SELinux types are reused. Init gains read permission for
  `misc_logd_file` and create/write permission for `vold_metadata_file`.
- No new service, executable, domain, USB path, file type, recovery component,
  or crypto path was added.

Installable OTA:

```text
lineageos/out/target/product/odessa/
  lineage-23.2-20260726-BOOTLOOP-TRY4-UNOFFICIAL-odessa.zip
size: 1,028,459,562 bytes
SHA-256: b8ba2eda848e8bb6ac108f3ea372307564f50427415849126da602f343daa704
```

Exact payload extraction, not loose outputs, confirmed the installable ZIP
contains the zygote copy action and compiled SELinux permissions. Extracted
TRY4 system image SHA-256:

```text
8d0305bd177c0ce2336a912217a2bb636d3fa92b57deb5681673046d6ee4d7b6
```

Important provenance caveat: the mutable target-files ZIP still had TRY3's old
hash/timestamp while the installable TRY4 payload contained the intended TRY4
bytes. Do not use that stale target-files archive to regenerate or claim
reproducibility. Preserve and reason from the exact validated TRY4 OTA payload.
Before any future release build, regenerate a fresh target-files archive and
prove target-files-to-OTA identity.

TRY4 installation log:

```text
recovery-slotb-try4-20260726.log
SHA-256: 94ea4e77e7419d36d677275bca3fe1c299cdf6aa90a122d2885a5db9f6c87a84
source slot: B
target slot: A
DownloadAction: kSuccess
FilesystemVerifierAction: kSuccess
PostinstallRunnerAction: kSuccess
Install completed with status 0
```

The raw recovery log contains device information and must remain untracked.

## Repository state

Temporary uncommitted TRY4 changes:

- `device/motorola/sm6150-common/properties.mk`
- `system/core/rootdir/init.zygote64.rc`
- `system/sepolicy/private/init.te`

`git diff --check` passed in all three repositories before the build.

Do not commit TRY4 diagnostics. Remove them after the log is collected or the
diagnostic is abandoned. The production zygote critical-window property must
also be restored before release.

The outer project has pre-existing tracked/untracked session files. Do not clean,
revert, or commit them wholesale. `manifests/odessa.xml` contains the intentional
bootctrl fork pin from the XBL/GPT fix.

## Operational rules reinforced

- Do not ask for stopwatch timing. Slot retry metadata and exact logs are better
  evidence.
- Do not use `adb wait-for-device`; it hangs incorrectly in this setup. Issue
  bounded direct ADB queries after the user enables ADB.
- Do not manually flash loose `boot`, `dtbo`, `recovery`, `vbmeta`, or dynamic
  partition images. The user did this twice; failed logical resizes transferred
  no dynamic image data, and subsequent status-0 OTAs repaired the target slots.
- Do not compare loose `out/*.img` files with payload-extracted images.
- Do not build as the agent. Give the user commands; their terminal has the
  correctly configured sccache environment.
- Keep long build output redirected to ignored logs.
- Do not expose raw `/proc/cmdline`, recovery logs, pmsg, metadata keys, serials,
  MAC addresses, or other identifiers.
