# Patches for `hardware/qcom-caf/bootctrl`

`hardware/qcom-caf/bootctrl` is an upstream LineageOS repository
(`LineageOS/android_hardware_qcom_bootctrl`). It is **not** one of the five
tracked project repositories and is **not** pinned in `manifests/odessa.xml`, so
a `repo sync` will discard local commits made there.

These patches are kept here so the work is not lost. They are exported with
`git format-patch` and apply on top of the recorded base commit.

| Patch | Base commit | Purpose |
| --- | --- | --- |
| `0001-bootctrl-Don-t-mark-UFS-boot-LUN-partitions-unbootab.patch` | `846dfb0` | Stop `update_slot_attribute()` marking `xbl`, `xbl_config`, `multiimgoem`, and `multiimgqti` unbootable on UFS. See `docs/xbl-unbootable-root-cause-20260724.md`. |

To apply after a fresh sync:

```bash
cd lineageos/hardware/qcom-caf/bootctrl
git am /path/to/odessa/patches/hardware-qcom-bootctrl/*.patch
```

This is a stopgap. The proper fix is to fork the repository to the project's
remote and pin the fork in `manifests/odessa.xml`, as is already done for the
kernel. Until that happens the build is not reproducible from the manifest
alone.
