#!/bin/bash

export ZPOOL=test_zhist_zpool1

# create test zpool
echo creating 64MB file: $ZPOOL
head -c 68000000 /dev/zero > $ZPOOL
echo creating zpool: $ZPOOL
zpool create $ZPOOL `pwd`/$ZPOOL
export MOUNTPOINT=$(zfs get mountpoint $ZPOOL | awk '{print $3}' | grep test)

# setup for test: check main fs (no actions needed)
# also test behavior on non-zfs fs
# make tests for sub-directories
# removed files

# setup for test_dir
zfs create $ZPOOL/cwd
mkdir -p $MOUNTPOINT/cwd/a/b/c

# setup for test_file
zfs create $ZPOOL/test_file
mkdir -p $MOUNTPOINT/test_file/d1/d2
touch $MOUNTPOINT/test_file/f1
touch $MOUNTPOINT/test_file/d1/f2

# setup for test: nothing in fs
zfs create $ZPOOL/nothing_in_fs

# setup for test: no snapshots
zfs create $ZPOOL/no_snapshots
echo foo > $MOUNTPOINT/no_snapshots/bar

# setup for test: file exists, has multiple changes
zfs create $ZPOOL/file_changed
zfs snapshot $ZPOOL/file_changed@t1
touch $MOUNTPOINT/file_changed/bar
zfs snapshot $ZPOOL/file_changed@t2
echo foo > $MOUNTPOINT/file_changed/bar
zfs snapshot $ZPOOL/file_changed@t3
zfs snapshot $ZPOOL/file_changed@t4
echo baz > $MOUNTPOINT/file_changed/bar
zfs snapshot $ZPOOL/file_changed@t5
echo foo >> $MOUNTPOINT/file_changed/bar
zfs snapshot $ZPOOL/file_changed@t6

# setup for test: deleted file recovery
#zfs clone $ZPOOL/file_changed@t6 file_deleted
#rm $MOUNTPOINT/file_deleted/bar

# try to configure test runner; if not, explain what to do
echo $MOUNTPOINT
