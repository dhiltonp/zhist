from unittest import TestCase
import zhist


class TestSplit(TestCase):
    def test_cwd(self):
        path = zhist.zfs_split(".")
        self.assertEqual(path[2], "")

    def test_separators(self):
        path = zhist.zfs_split("/")
        self.assertEqual(path, ("/", "", ""))

        # these next test cases assume /bin is not a mount point
        path1 = zhist.zfs_split("/bin/")
        path2 = zhist.zfs_split("/bin")
        self.assertEqual(path1, ("/", "bin/", ""))
        self.assertEqual(path1, path2)

        path1 = zhist.zfs_split("/bin/ls")
        path2 = zhist.zfs_split("/bin/ls")
        self.assertEqual(path1, ("/", "bin/", "ls"))
        self.assertEqual(path1, path2)

    def test_bad_file(self):
        with self.assertRaises(Exception):
            zhist.zfs_split("/thisfiledoesntexistandaoentuhasnothyrcdio")
        with self.assertRaises(Exception):
            zhist.zfs_split("/thisdirdoesntexistandaoentuhasnothyrcdio/")
        with self.assertRaises(Exception):
            zhist.zfs_split("/thisdirdoesntexistandaoentuhasnothyrcdio/thisfiledoesntexistandaoentuhasnothyrcdio")

