## ZFS History - simplified usage of ZFS snapshots

The purpose of zhist is to simplify access to past ZFS snapshots. Currently, a command-line interface a-la 'ls' exists. Ultimately, a GUI allowing easy browsing of history would be ideal.

Main features:
 * Specify a valid filename and all snapshots will be searched for the existence of that file (by name, not inode), whether or not it currently exists.
 * Intermediate snapshots are skipped - only changes are shown.

Currently the code has been tested on MacOS and OmniOS. Python version >= 2.7 is required.

## EXAMPLE

```
david$ ./zhist.py /zpools/test_zhist_zpool2/file_changed/f1
A /Volumes/test_zhist_zpool2/file_changed/.zfs/snapshot/t2/f1 {'st_mtime': 'Sun Nov  8 21:10:49 2015', 'st_size': 0}
C /Volumes/test_zhist_zpool2/file_changed/.zfs/snapshot/t3/f1 {'st_mtime': 'Sun Nov  8 21:10:50 2015', 'st_size': 4}
C /Volumes/test_zhist_zpool2/file_changed/.zfs/snapshot/t5/f1 {'st_mtime': 'Sun Nov  8 21:10:52 2015'}
C /Volumes/test_zhist_zpool2/file_changed/.zfs/snapshot/t6/f1 {'st_mtime': 'Sun Nov  8 21:10:53 2015', 'st_size': 8}
D /Volumes/test_zhist_zpool2/file_changed/.zfs/snapshot/t7/f1
A /Volumes/test_zhist_zpool2/file_changed/f1 {'st_mtime': 'Sun Nov  8 21:10:56 2015', 'st_size': 0}
```
