# Firmware Slot Comparison

Collected **READ ONLY** from the installed recovery on 2026-07-19. No partition content was saved, copied, mounted, or written. No flash, erase, format, wipe, install, or sideload occurred.

## Preflight

- Product: `odessa`
- SKU: `XT2087-1`
- Active slot before and after the check: `_a`
- Slot count: 2
- Bootloader mode: bootloader fastboot (`is-userspace: no`)
- Bootloader state: `securestate: flashing_unlocked`
- Battery before entering recovery: 100%
- Recovery ADB ran as root and provided `/system/bin/sha256sum`.
- The phone returned to Android successfully with `sys.boot_completed=1`.

## Scope

The comparison was limited to A/B low-level firmware partitions that are not updated by the current LineageOS OTA and are not known identity, calibration, DRM, attestation, or user-data storage.

Compared: `abl`, `aop`, `bluetooth`, `cmnlib`, `cmnlib64`, `devcfg`, `dsp`, `hyp`, `keymaster`, `logo`, `modem`, `multiimgoem`, `multiimgqti`, `qupfw`, `storsec`, `tz`, `uefisecapp`, `xbl`, and `xbl_config`.

Deliberately excluded: `fsg`, `prov`, `persist`, `modemst1`, `modemst2`, `cid`, `utags`, `utagsBackup`, and every other shared identity/calibration/data partition. `boot`, `dtbo`, `recovery`, `vbmeta`, and the dynamic `system`, `vendor`, and `product` partitions were also outside this low-level firmware comparison.

The recovery streamed each complete block device directly through `sha256sum`. It did not redirect partition bytes to a file.

## Results

| Partition | Slot A SHA-256 | Slot B SHA-256 | Result |
| --- | --- | --- | --- |
| `abl` | `3c96e9a4f31befadff79cf2963c572906620966f5fecdb82223448393e371a15` | `86fa84f32b238d02eaf5cfe9f8f681d390f73265837c5bdcdc241ce5787e29a1` | DIFFERENT |
| `aop` | `e3b5cfaf74cee29fb6d899f925d5e7c9806cb739f7a49b4f695b37a6ef275c19` | `8ad2bb687da6c61df7f30eb9b650aa032d24c0443eaf5eb38948446fb2c090cd` | DIFFERENT |
| `bluetooth` | `d9c20a0faf70481375ef1c52cdfc0fe8f6244e77c7591659f45934afc0b91317` | `1336d73919d85f8f6d34372ea9eba2ecf1f1168b14562a4a6f982f8fc83ce144` | DIFFERENT |
| `cmnlib` | `58d2898ecc0f6a57214b44b8e265ce392baaa534b886287293d67092ce005b68` | `81bd6f14cae552ea257be3eda7af3ab276972751e90158fc86ca9ab9b8a8099e` | DIFFERENT |
| `cmnlib64` | `8f6a0ee36e3998cf2265d8e89fdc20e65469771c94348aea10a302dfbddf99e9` | `43d3f746df68c2e244bdad3a6477a30281ca4148a95ad505ce4bc17e94b70d9c` | DIFFERENT |
| `devcfg` | `ae60df570324be8bc220fe26cfcc32b741840ba6b9254079292b52d87ed4fa4f` | `ae9e65b645a55f106da90a4ff1fd00e09db732aac4acccf022cc8a122630ca5e` | DIFFERENT |
| `dsp` | `32b5f820436092acbc37309ff9f0759b2c059fde8bbdda92d71c7b24cbb9f1fa` | `32b5f820436092acbc37309ff9f0759b2c059fde8bbdda92d71c7b24cbb9f1fa` | MATCH |
| `hyp` | `d179181ac10069e39ecd36da54b3ca88dd04343e3c0615d56c81b4b7fb167d7c` | `6a8338a99fcac253b11492a1d36608f2a760583a6b58c9c339271a665592ec80` | DIFFERENT |
| `keymaster` | `55c1fed71803526b565582f4c9947e73207cbbf97c91efc6e489ddfebd15fec5` | `1225544b960bc845198dbf5687f8617cf9aa6238b0bc7118aae6c79136b081ee` | DIFFERENT |
| `logo` | `9f1c4416d0b48041c96a29b10fd57819e706d2b67585795d652d26e2432294e0` | `b0502fc56a843295852ab32971f46cfc503b0e6eb1ee9f64a54c0e3f45062ebb` | DIFFERENT |
| `modem` | `5b45a564339721d1b3ceabea4038f114b8d52ac3d93edd44b827e4a951867365` | `b4cea4f2cac6d7b183d1e7ece5f9d916d262e3841c2b4d8b9fafb70492fea1ec` | DIFFERENT |
| `multiimgoem` | `c35020473aed1b4642cd726cad727b63fff2824ad68cedd7ffb73c7cbd890479` | `c35020473aed1b4642cd726cad727b63fff2824ad68cedd7ffb73c7cbd890479` | MATCH |
| `multiimgqti` | `c35020473aed1b4642cd726cad727b63fff2824ad68cedd7ffb73c7cbd890479` | `c35020473aed1b4642cd726cad727b63fff2824ad68cedd7ffb73c7cbd890479` | MATCH |
| `qupfw` | `7f4ca5b616813e0ba8c087f51faf931615fa2ade5abed9a310ce79808f3f5b46` | `8f3a17773f7f963a071b169186043965d654d41a88d2b89bd0ad3d6e933ed8d5` | DIFFERENT |
| `storsec` | `64642656f5ebe7eef16f6e04c634af90ba80b5dde0ddc8e44192c64530dda8eb` | `bb1610321e8f2ee03fbb27d59582c4e1215c0a31f1e59008c55bd53d537fc600` | DIFFERENT |
| `tz` | `5e7c60b717ac2ca76e7e41eeb4d3020dde5043023c72f049df92621e757b6f74` | `511a148e7d6665d0eca3220689f79f5c03d2cfcdb0de93126f4ef664ce907d13` | DIFFERENT |
| `uefisecapp` | `ac950e16167cb3dd0b04b0c603a203d7ad5d5b3a105870b05afeabdef3c1397f` | `5a1ba0add9fb3d9f79dd5d7e18c3b22e6df6fdee5ed95ccc9100b0d097755e09` | DIFFERENT |
| `xbl` | `1339f235b27ec5c222a359c88e4a0a252c32ac594722dfd18fe0c57dd6dfbd86` | `1a6321b0bdd285ed04b81c87b7a0a7fb9593fed7729fd340ff45414aeff31b12` | DIFFERENT |
| `xbl_config` | `89ab705f2e2059729153fbd5ee4ea49acf4d2be61ad448cc9e2216cc2d983bfe` | `f19f64e1b9e84666844cf1d06d50a5a911b8311b792820517554311ba72031ab` | DIFFERENT |

Summary: 3 pairs match and 16 pairs differ.

## Decision

Firmware copying cannot be omitted on the assumption that both slots are already identical. The hash differences also do not establish which copy is newer, internally consistent, or safe to propagate.

Do not run the generic `copy-partitions` package, do not copy slot A to B or B to A, and do not touch any excluded partition. The next step is a HOST ONLY partition-specific provenance review against the official Motorola package and the currently booted firmware before designing a minimal copy procedure, if one is needed at all.
