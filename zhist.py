#!/usr/bin/python
# 
# Copyright (c) 2010 "Edward Harvey" <rahvee@gmail.com>
# Copyright (c) 2015 "David Hilton" <david.hilton.p@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import time
import collections
import argparse
import platform
import subprocess
import sys, os, os.path
from contextlib import contextmanager

#maemoize
def get_snapshot_time(mount_point, snapshot):
    volume_name = get_volume_name(mount_point)
    full_snapshot_name = volume_name+"@"+snapshot
    command = "zfs get -H -p -o value creation "+full_snapshot_name
    output = subprocess.check_output(command.split()).strip()
    return int(output)

#maemoize
def get_volume_name(mount_point):
    command = "zfs list -H -o name " + mount_point
    output = subprocess.check_output(command.split()).strip()
    return output


@contextmanager
def temporary_mount_snapshot(mount_point, snapshot):
    #mount_point to snapshot
    volume_name = get_volume_name(mount_point)
    full_snapshot_name = volume_name+"@"+snapshot

    already_mounted = False
    with open(os.devnull, "w") as fnull:
        retval = subprocess.call(["zfs", "mount", full_snapshot_name], stderr=fnull)

        if retval == 0:
            pass
        elif retval == 1:
            already_mounted = True
        else:
            sys.stderr.write("Unable to mount "+full_snapshot_name+", results will be incomplete. (%d)\n" % retval)

    try:
        yield
    finally:
        if not already_mounted:
            with open(os.devnull, 'w') as fnull:
                retval = subprocess.call(["zfs", "unmount", full_snapshot_name], stderr=fnull, stdout=fnull)
                if retval != 0:
                    sys.stderr.write("Unable to unmount "+full_snapshot_name+" sorry (%d)!\n" % retval)


Version = collections.namedtuple("Version", ['path', 'snapshot_time', 'stat_result'])


class ZHist:
    def zfs_split(self, f):
        """
        Returns f's full path, split into 2:
        the longest mount_point: "/mount/point/", leading and trailing "/"
        the zfs_path within that mount point: "path/to" with no leading or trailing "/"

        The zfs_path will never have a trailing "/", as both directories and files may exist with the same name
        """
        # get full path:
        f = os.path.abspath(f)

        # get path to mount point
        mount_point = f
        while not os.path.ismount(mount_point):
            mount_point = os.path.dirname(mount_point)
        if mount_point[-1] is not '/':
            mount_point += '/'

        # get path from mount point
        zfs_path = f[len(mount_point):]

        return mount_point, zfs_path

    def ls(self, files):
        files = files[0]
        if len(files) == 0:
            files.append('.')

        mount_points = []

        for f in files:
            try:
                mount_point, zfs_path = self.zfs_split(f)
                versions = self.get_versions(mount_point, zfs_path)
                self.print_roll_up(versions)
            except Exception as e:
                print(e)

    def print_roll_up(self, versions):
        versions.sort(key=lambda v: v.snapshot_time)

        # make values human readable
        for version in versions:
            if version.stat_result != {}:
                version.stat_result['st_ctime'] = time.ctime(version.stat_result['st_ctime'])
                version.stat_result['st_mtime'] = time.ctime(version.stat_result['st_mtime'])

        # display changed values
        for pre, post in zip(versions, versions[1:]):
            # display all differences post has from pre
            if pre.stat_result == post.stat_result:
                continue
            elif pre.stat_result == {}:
                # print Added
                tmp = {}
                tmp['st_mtime'] = post.stat_result['st_mtime']
                tmp['st_size'] = post.stat_result['st_size']
                #mode, uid, gid
                print("A "+post.path+" "+str(tmp))
                pass
            elif post.stat_result == {}:
                # print Deleted
                print("D "+post.path)
            else:
                # diff keys
                diff = {}
                for key in pre.stat_result.keys():
                    if pre.stat_result[key] != post.stat_result[key]:
                        diff[key] = post.stat_result[key]
                if diff['st_ctime'] == diff['st_mtime']:
                    del diff['st_ctime']  # file modified - mtime implies ctime also changed
                else:
                    del diff['st_mtime']  # permissions changed? - only ctime implies stats changed, not content
                print "C "+post.path+" "+str(diff)

    def get_versions(self, mount_point, zfs_path):
        """
        uses a mount_point and zfs_path to get all available versions of a file.
        Returns all found versions, along with the stat results
        """
        versions = [Version("in the beginning...", -1, {})]
        current_version = mount_point+zfs_path
        if os.path.exists(current_version):
            version = Version(current_version, int(time.time()), self._stat_to_dict(os.lstat(current_version)))
            versions.append(version)
        else:
            version = Version(current_version, int(time.time()), {})
            versions.append(version)

        snapshot_dir = mount_point+".zfs/snapshot/"
        for snapshot in self.get_snapshots(snapshot_dir):
            possible_version = snapshot_dir+snapshot+"/"+zfs_path
            version_stat = self.stat(possible_version, mount_point, snapshot)
            snapshot_time = get_snapshot_time(mount_point, snapshot)
            versions.append(Version(possible_version, snapshot_time, version_stat))

        # this is just for debugging, not display
        return versions

    def _stat_to_dict(self, stat):
        stat_dict = {}
        for field in ["st_mode", "st_ino", "st_nlink", "st_uid", "st_gid", "st_size", "st_mtime", "st_ctime"]:
            stat_dict[field] = getattr(stat, field)
        return stat_dict

    def stat(self, version, mount_point, snapshot):
        with temporary_mount_snapshot(mount_point, snapshot):
            if os.path.exists(version):
                return self._stat_to_dict(os.lstat(version))
            return {}

    def get_snapshots(self, snapshot_dir):
        try:
            return os.listdir(snapshot_dir)
        except OSError:
            sys.stderr.write("Cannot read %s; is this ZFS?\n" % snapshot_dir)
            if platform.system() == "Darwin":
                sys.stderr.write("You need to reset the zpool via export/import (see https://github.com/openzfsonosx/zfs/issues/232).\n")
            raise

    def zfs_diff(self, mount_point, zfs_path, filename):
        pass


def osx_test():
    if platform.system() == "Darwin" and os.geteuid() != 0:
        raise Exception("MacOS needs root permissions (sudo) to mount snapshots; see the O3X FAQ.")
    return True


def parse_arguments():
    parser = argparse.ArgumentParser("Lists all available snapshot versions of a specified file or directory.")
    parser.add_argument("file", action="append", nargs='*', help="file or directories to list")
    #options: show checksum, size, date modified...
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    osx_test()
    ZHist().ls(args.file)

if __name__ == "__main__":
    sys.exit(main())
