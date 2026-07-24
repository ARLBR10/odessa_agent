# Build Checkpoint 2026-07-18

All validation in this document is host-only. No generated LineageOS image has been booted, flashed, or sideloaded.

## Source commits

- Odessa device: `23809aa` (`odessa: Set VINTF target level to 6`)
- SM6150 common device: `101bf343` (`sm6150-common: Update power HAL for current libperfmgr`)
- SM6150 common device: `ade40c34` (`sm6150-common: Complete Android 16 compatibility integration`)
- SM6150 kernel: `70f404ff7c1f` (merge Android common kernel 4.14.336)
- SM6150 kernel: `98efff6a92e3` (`BACKPORT: mm: Support PMD and PUD moves`)
- SM6150 kernel: `b9df0469a7a2` (`arm64: configs: odessa: Satisfy FCM 6 requirements`)
- SM6150 common vendor: `73b5933` (`sm6150-common: Regenerate Android 16 compatibility blobs`)

These commits currently exist only in local repositories. `manifests/odessa.xml` must continue to reference fetchable public baselines until remotes capable of serving the new commits are configured.

## Artifacts

| Artifact | Size (bytes) | SHA-256 |
| --- | ---: | --- |
| `lineage_odessa-target_files.zip` | 2,615,265,928 | `6f80655466ccbd7cf9193bce23fb0b253b665760be3be304be27033c4b6f0f72` |
| `lineage-23.2-20260719-UNOFFICIAL-odessa.zip` | 1,028,374,656 | `65d3a91433e470899f79c75386e771bd6d84b3d4cde28f0a06a7d0dd23280dee` |
| `boot.img` | 67,108,864 | `b3778bfeaa72aced813a9b04bda1878ab1c31c1e7447752e468a993432667737` |
| `dtbo.img` | 25,165,824 | `be2e144cc4578577d1ae73ce28b924c302652b2ba7bd2d2e4d0495cbf9ff98e6` |
| `recovery.img` | 67,108,864 | `dd4e3350ac92278b42a7db13bbc2f778898a923b09ab48b6d1368886272c2d26` |

Both ZIP files pass `unzip -tq`. Verbose `check_target_files_vintf` returns `COMPATIBLE` for Linux `4.14.336-perf+` at FCM 6.

## Rebuild decision

No rebuild was required after committing. The successful artifacts were generated from the exact working-tree contents that were reviewed and committed; Git commits change repository metadata, not source bytes or generated output.

A future clean rebuild is still required for release reproducibility after the local commits are available from pinned remotes. It is not a prerequisite for completing Phase 0 or the first controlled hardware validation.

This is a test-key `userdebug` build. Phase 0 is complete with documented baseline limitations, but the build is not release-signed and remains unapproved for flashing until `docs/first-install-checkpoint.md` closes the firmware-slot and immediate preflight gates.
