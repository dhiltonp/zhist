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
        self.assertEquals(result[0][0], mountpoint+"nothing_in_fs/")
        self.assertEqual(len(result), 1, "More than one version received")

        result = zhist.ZHist().get_versions(mountpoint+"nothing_in_fs/", "imaginary_file")
        self.assertEquals(result, [])

        result = zhist.ZHist().get_versions(mountpoint+"nothing_in_fs/", "imaginary_dir/imaginary_file")
        self.assertEquals(result, [])

    def test_no_snapshots(self):
        result = zhist.ZHist().get_versions(mountpoint+"no_snapshots/", "f1")
        self.assertEquals(result[0][0], mountpoint+"no_snapshots/f1")
        self.assertEqual(len(result), 1)

    def test_file_added(self):
        result = zhist.ZHist().get_versions(mountpoint+"file_added/", "f1")
        self.assertEqual(len(result), 2)
        self.assertEquals(result[0][0], mountpoint+"file_added/f1")
        self.assertEquals(result[1][0], mountpoint+"file_added/.zfs/snapshot/t2/f1")

    def test_file_removed(self):
        result = zhist.ZHist().get_versions(mountpoint+"file_removed/", "f1")
        self.assertEqual(len(result), 1)
        self.assertEquals(result[0][0], mountpoint+"file_removed/.zfs/snapshot/t2/f1")

    def test_file_changed(self):
        result = zhist.ZHist().get_versions(mountpoint+"file_changed/", "f1")
        self.assertEquals(result, [])

