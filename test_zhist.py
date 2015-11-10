from unittest import TestCase
import zhist

####### taken from http://stackoverflow.com/questions/431684/how-do-i-cd-in-python/24176022#24176022
from contextlib import contextmanager
import os

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

####### end borrowed block

mountpoint = '/Volumes/test_zhist_zpool2/'

class TestSplit(TestCase):
    def test_root(self):
        result = zhist.ZHist().zfs_split("/")
        self.assertEqual(result, ("/", ""))

    def test_dir(self):
        test_data = [
            (mountpoint, (mountpoint, "")),
            (mountpoint+"cwd", (mountpoint+"cwd/", "")),
            (mountpoint+"cwd/a/b", (mountpoint+"cwd/", "a/b"))]
        for path, expected_result in test_data:
            # absolute path
            result = zhist.ZHist().zfs_split(path)
            self.assertEquals(result, expected_result)
            # relative path
            with cd(mountpoint):
                partial_path = "./"+path[len(mountpoint):]
                result = zhist.ZHist().zfs_split(partial_path)
                self.assertEquals(result, expected_result)
            # inside of directory
            with cd(path):
                result = zhist.ZHist().zfs_split(".")
                self.assertEquals(result, expected_result)

    def test_file(self):
        # absolute test
        result = zhist.ZHist().zfs_split(mountpoint+"test_file/f1")
        self.assertEquals(result, (mountpoint+'test_file/', 'f1'))

        result = zhist.ZHist().zfs_split(mountpoint+"test_file/d1/f2")
        self.assertEquals(result, (mountpoint+'test_file/', 'd1/f2'))
        # relative test
        with cd(mountpoint):
            result = zhist.ZHist().zfs_split("test_file/f1")
            self.assertEquals(result, (mountpoint+'test_file/', 'f1'))

            result = zhist.ZHist().zfs_split("test_file/d1/f2")
            self.assertEquals(result, (mountpoint+'test_file/', 'd1/f2'))

    def test_no_file(self):
        result = zhist.ZHist().zfs_split(mountpoint+"no_file")
        self.assertEquals(result, (mountpoint, 'no_file'))
        result = zhist.ZHist().zfs_split(mountpoint+"no_dir")
        self.assertEquals(result, (mountpoint, 'no_dir'))
        result = zhist.ZHist().zfs_split(mountpoint+"no_dir/")
        self.assertEquals(result, (mountpoint, 'no_dir'))
        result = zhist.ZHist().zfs_split(mountpoint+"no_dir/no_file")
        self.assertEquals(result, (mountpoint, 'no_dir/no_file'))


class TestGetVersions(TestCase):
    def test_nothing_in_fs(self):
        result = zhist.ZHist().get_versions(mountpoint+"nothing_in_fs/", "")
        self.assertEquals(result[1].path, mountpoint+"nothing_in_fs/")
        self.assertEqual(len(result), 2)

        result = zhist.ZHist().get_versions(mountpoint+"nothing_in_fs/", "imaginary_file")
        self.assertEquals(len(result), 2)
        self.assertEquals(result[1].stat_result, {})

        result = zhist.ZHist().get_versions(mountpoint+"nothing_in_fs/", "imaginary_dir/imaginary_file")
        self.assertEquals(len(result), 2)
        self.assertEquals(result[1].stat_result, {})

    def test_no_snapshots(self):
        result = zhist.ZHist().get_versions(mountpoint+"no_snapshots/", "f1")
        self.assertEquals(result[1].path, mountpoint+"no_snapshots/f1")
        self.assertEqual(len(result), 2)

    def test_file_added(self):
        result = zhist.ZHist().get_versions(mountpoint+"file_added/", "f1")
        result.sort(key=lambda v: v.snapshot_time)
        self.assertEqual(len(result), 4)
        self.assertEquals(result[0].stat_result, {})
        self.assertEquals(result[1].stat_result, {})
        self.assertNotEquals(result[2].stat_result, {})
        self.assertNotEquals(result[3].stat_result, {})

    def test_file_removed(self):
        result = zhist.ZHist().get_versions(mountpoint+"file_removed/", "f1")
        result.sort(key=lambda v: v.snapshot_time)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0].stat_result, {})
        self.assertEqual(result[1].stat_result, {})
        self.assertNotEqual(result[2].stat_result, {})
        self.assertEqual(result[3].stat_result, {})

    def test_bad_get_snapshots(self):
        result = zhist.ZHist().get_snapshots("/bin")

        with self.assertRaises(OSError):
            zhist.ZHist().get_snapshots("/bin/sh")


class TestRollUp(TestCase):
    def test_file_removed_roll_up(self):
        versions = zhist.ZHist().get_versions(mountpoint+"file_removed/", "f1")
        roll_up = zhist.ZHist().generate_roll_up(versions)
        self.assertEqual(len(roll_up), 2)
        self.assertEqual(roll_up[0][0], "A")
        self.assertEqual(roll_up[1][0], "D")

    def test_file_added_roll_up(self):
        versions = zhist.ZHist().get_versions(mountpoint+"file_added/", "f1")
        roll_up = zhist.ZHist().generate_roll_up(versions)
        self.assertEqual(len(roll_up), 1)
        self.assertEqual(roll_up[0][0], "A")

    def test_file_changed_roll_up(self):
        versions = zhist.ZHist().get_versions(mountpoint+"file_changed/", "f1")
        roll_up = zhist.ZHist().generate_roll_up(versions)
        changes = ''.join([line[0] for line in roll_up])
        self.assertEqual(len(roll_up), 7)
        self.assertEqual(changes, "ACCCDAP")

