# Odessa BPF Backport Bootloop: Root Cause and Handoff

Date: 2026-07-30

## Scope

This report covers the Linux 5.10 BPF backport on Motorola Odessa's OpenELA
4.14.357 kernel, the pre-Recovery bootloop investigation, the verified fix, and
the state immediately after the first full Android 16 OTA sideload.

The current device symptom after the OTA reboot is a very fast reboot cycle.
The user suspects another partition-table/slot-selection failure. That has not
been measured and must not yet be called GPT corruption.

## Starting evidence

- `df9da243d122` was the exact last backport commit known to boot Recovery.
- Completed backport `295fa6418564` built but bootlooped before Recovery.
- Intermediate commits did not provide useful buildable bisection points:
  `37e035f8c918` and `eb0458ea6a0f` did not produce a complete kernel;
  `8c13ed9d15ab` was the first later commit that linked.
- The hardware oracle was a newly built Recovery image. These failures occurred
  before Recovery, not at Android's later `netbpfload` service.

## Isolation results

Each candidate was based on completed backport `295fa6418564` and tested through
Recovery B.

| Candidate | Result | Conclusion |
| --- | --- | --- |
| Disable unconditional XDP RX-queue registration | Bootloop | XDP RX-queue setup was not sufficient to cause the failure. |
| Disable `CONFIG_BPF_EVENTS` init paths | Bootloop | BPF trace/perf-event support was not sufficient to cause the failure. |
| Disable eBPF syscall, cgroup/classifier, events, and JIT | Booted | Imported networking/core code could boot. |
| Restore full eBPF core/events, keep JIT disabled | Booted | Verifier, maps, BTF, cgroup/classifier, and BPF events could boot. |
| Compile JIT, keep `BPF_JIT_ALWAYS_ON=n` | Booted | JIT source and dedicated virtual region were safe while JIT execution remained default-off. |
| Restore production JIT config with Kconfig fix | Booted | Root fix hardware-confirmed. |

The no-JIT builds also exposed two real completeness gaps that normal production
configuration had hidden:

- `include/linux/compiler.h` lacked `__annotate_jump_table`.
- `include/linux/filter.h` lacked a no-JIT `bpf_jit_blinding_enabled()` stub.

Both were fixed. They do not alter the production JIT-enabled path.

## Root cause

The imported 5.10 `kernel/bpf/core.c` initializes:

```c
int bpf_jit_enable __read_mostly =
    IS_BUILTIN(CONFIG_BPF_JIT_DEFAULT_ON);
```

The Odessa backport omitted all three pieces that make this true on ARM64:

- `ARCH_WANT_DEFAULT_BPF_JIT` in `init/Kconfig`;
- ARM64's `select ARCH_WANT_DEFAULT_BPF_JIT`;
- `BPF_JIT_DEFAULT_ON`, defined from
  `ARCH_WANT_DEFAULT_BPF_JIT || BPF_JIT_ALWAYS_ON`.

Consequently, `bpf_jit_enable` initialized to zero. At the same time,
`CONFIG_BPF_JIT_ALWAYS_ON=y` compiled out the interpreter. BPF programs could
therefore be allocated without a requested JIT runtime while no interpreter was
available, causing the pre-Recovery failure.

The fix restored the exact Linux 5.10/Xiaomi Kconfig chain and removed an
accidental duplicate `BPF_UNPRIV_DEFAULT_OFF` block. In the resulting `vmlinux`,
GDB reads `bpf_jit_enable` as exactly `1`, and the symbol resides in initialized
data rather than zero-filled BSS.

## Published source

- Kernel fix and complete BPF backport:
  `ARLBR10/android_kernel_motorola_sm6150`
  commit `56146fa516106938ed3a8f0c0e187f3c679371a4`.
- Matching Odessa `ro.bpf.kver_override=5.10.239` declaration:
  `ARLBR10/android_device_motorola_odessa`
  commit `fc7495d15985fb611be1e8287f8efb2c58e48fa7`.
- Outer manifest pin: commit `989b118`.
- Session documentation through the Recovery fix: commit `6db5f80`.

The manifest now pins the published immutable kernel and Odessa revisions, so a
normal Repo sync no longer rolls back to the OpenELA-only kernel.

## Build verification

Command:

```bash
m -j8 bacon recoveryimage
```

Result: success in 7m40s.

- VINTF: `COMPATIBLE`.
- Generated config includes `ARCH_WANT_DEFAULT_BPF_JIT=y`,
  `BPF_JIT_DEFAULT_ON=y`, `BPF_JIT_ALWAYS_ON=y`, `BPF_JIT=y`,
  `BPF_SYSCALL=y`, `CGROUP_BPF=y`, `NET_CLS_BPF=y`, and `BPF_EVENTS=y`.
- OTA: `lineage-23.2-20260730-UNOFFICIAL-odessa.zip`.
- OTA size: 1,028,108,519 bytes.
- OTA SHA-256:
  `7fdc68d6e6503b7ca10a40fddbe55ff401b27cfaf84901eaa417e9b68db17a83`.
- Kernel `Image` SHA-256:
  `abc5f1281d2388e370e5676b41984079dd4fb49af366eb55ac0c6b7b27ebef75`.
- Packaged vendor property: `ro.bpf.kver_override=5.10.239`.

The checkout's native `brillo_update_payload verify` path applied all 2,265 OTA
operations offline. Generated `boot`, `dtbo`, `product`, `recovery`, `system`,
`vbmeta`, and `vendor` partitions matched target-files byte-for-byte. Operation
and partition hashes passed. Payload signature validation was not performed
because no public key was supplied for this test-key build.

## Device installation evidence

Before sideload:

- Running Lineage Recovery was on slot B.
- Kernel was `4.14.357-openela-perf+` with the production BPF fix.
- Device identity read `odessa`, SKU `XT2087-1`.

The user explicitly authorized one sideload of the OTA above. Recovery reported:

- install plan `target_slot: A`;
- all payload partition hashes successful;
- postinstall successful;
- `Update successfully applied, waiting to reboot`;
- `Install completed with status 0`.

Read-only post-install hashes matched the OTA target exactly for:

- `boot_a`: `9cae54ee031880a326c5ecf4b6a13b46c1aea80dcdc216811bb7d8f642716420`;
- `recovery_a`: `c26cdfdec8cb357383d7042a32e450bb158335f56d334a2ccc2294ea2f08fad7`;
- `dtbo_a`: `8d80708752b4bcc2170e2c7adcb8b41c39d7d19ca38cc1586616dc9982c87293`.

The running Recovery did not contain `bootctl`, so the selected GPT slot could
not be queried through that CLI. The install log nevertheless clearly targeted
slot A and wrote slot-A partitions.

## Current blocker

After explicit approval, `adb reboot recovery` was issued to validate Recovery A
before Android. The command produced no captured output and was aborted by the
user while the device rebooted. The user then reported a very fast reboot cycle
and suspects the partition-table/slot-attribute problem has recurred.

No evidence was collected after that reboot. In particular, the following are
unknown:

- whether MBM selected slot A or repeatedly fell back;
- the current GPT attribute bytes and CRC status;
- whether Recovery A starts and crashes, or the failure occurs before Recovery;
- whether the boot-control HAL wrote Motorola `0x04`/`0x00` attributes as in the
  previously hardware-validated fix;
- whether the device still exposes bootloader, fastboot, Recovery ADB, or Android
  ADB during the cycle.

Do not call this GPT corruption until the table and attributes are captured.

## Safe next session

1. Stop automatic reboot attempts by holding Volume Down into the bootloader.
2. Do not flash, erase, format, sideload, switch slots, or restore GPT until the
   current partition view and attributes are read and compared.
3. Confirm the host still has the validated stock restore package and procedure
   in `docs/stock-restore-rpas31-4-3-9.md`.
4. Observe USB enumeration with `tools/watch-usb.sh` and determine whether MBM,
   fastboot, Recovery, or Android appears.
5. Capture GPT metadata read-only using the established project procedure. Keep
   raw captures under `/tmp/opencode`; they may contain unique partition GUIDs.
6. Compare active/inactive A/B attributes against Motorola's proven encoding:
   active `0x04`, inactive `0x00`, consistently across all A/B boot-chain
   partitions.
7. Hash safe slot-A images (`boot_a`, `recovery_a`, `dtbo_a`) again if accessible;
   they matched the OTA immediately before reboot.
8. Only after identifying the exact failure should any corrective write be
   proposed, with a new explicit permission request naming every partition/image.

The BPF kernel fix itself is independently hardware-confirmed through Recovery
and should not be reverted while diagnosing this post-OTA slot-selection symptom.
