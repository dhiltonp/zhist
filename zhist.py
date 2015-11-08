#!/usr/bin/python
# 
# Copyright (c) 2010 Edward Harvey
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
import argparse
import platform
import subprocess
import sys, os, os.path


def snapshotdir(pathname=''):
    if pathname.startswith('/'):
        if pathname == '/':
            if os.path.exists('/.zfs/snapshot'):
                return '/.zfs/snapshot'
            else:
                return False
        elif os.path.exists(pathname+'/.zfs/snapshot'):
            return pathname+'/.zfs/snapshot'
        else:
            return snapshotdir(os.path.dirname(pathname))


def ls(files):
    files = files[0]
    if len(files) == 0:
        files.append('.')

    for f in files:
        targetabsname=os.path.abspath(f)
        snapdir=snapshotdir(targetabsname)
        suffix=targetabsname.replace(os.path.commonprefix([targetabsname,snapdir]),'',1)
        targetsnaps=[]
        exists=os.path.exists
        try:
            exists=os.path.lexists
        except:
            print("Note: No such os.lexists. You must be using python < 2.4. Therefore forced to follow symlinks. Results questionable.")

        for snapname in os.listdir(snapdir):
            if exists(snapdir+'/'+snapname+'/'+suffix):
                mystat=os.lstat(snapdir+'/'+snapname+'/'+suffix)
                mode=mystat[0]   # protection bits
                inode=mystat[1]
                uid=mystat[4]
                gid=mystat[5]
                size=mystat[6]
                mtime=mystat[8]
                # This tuple is composed of:  ( an integer mtime, (a tuple), 'pathname' )
                # Having the mtime as the first component makes it easy to sort the whole list
                # Having the tuple, which includes mtime, allows us to easily identify repeat (non-unique) items
                # and of course, the pathname is needed in order to display the pathname.
                targetsnaps.append((mtime,(mtime,mode,inode,uid,gid,size),snapdir+'/'+snapname+'/'+suffix))
        # I'd like the output to also consider the item that's in the present filesystem,
        # and since I'm writing it, that's the behavior it will have.  ;-)
        if exists(targetabsname):
            mystat=os.lstat(targetabsname)
            mode=mystat[0]   # protection bits
            inode=mystat[1]
            uid=mystat[4]
            gid=mystat[5]
            size=mystat[6]
            mtime=mystat[8]
            targetsnaps.append((mtime,(mtime,mode,inode,uid,gid,size),targetabsname))
        targetsnaps.sort()
        targetsnaps.reverse()
        newstat=()
        oldstat=()
        for targetsnap in targetsnaps:
            newstat=targetsnap[1]
            if newstat == oldstat:
                # not written yet:
                # if we have selected not to omit duplicates,
                #    then print
                pass
            else:
                print(targetsnap[2])   # this is the absolute name
            oldstat=newstat

    sys.exit(0)


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
                mount_point, zfs_path, filename = self.zfs_split(f)
                versions = self.get_versions(mount_point, zfs_path)
                # by default, show all existing versions.
                # if a flag is shown,
                #mount_points.append(mount_point)
                #self.zfs_diff(mount_point, zfs_path, filename)
            except Exception as e:
                print e
            print(f)

    def get_versions(self, mount_point, zfs_path):
        """
        uses a mount_point and zfs_path to get all available versions of a file.
        Returns all found versions, along with the stat results
        """
        versions = []
        possible_versions = [mount_point+zfs_path]
        snapshot_dir = mount_point+".zfs/snapshot/"
        for snapshot in self.get_snapshots(snapshot_dir):
            snapshot += "/"
            possible_versions.append(snapshot_dir+snapshot+zfs_path)
        for version in possible_versions:
            if os.path.exists(version):
                print(version)
                stat=os.lstat(version)
                versions.append((version, stat))

        return versions

    def get_snapshots(self, snapshot_dir):
        #subprocess.check_output("zfs set snapdir=visible test_zhist_zpool1/file_changed".split())
        #subprocess.check_output("zfs mount test_zhist_zpool1/file_changed")
        return os.listdir(snapshot_dir)
        # https://openzfsonosx.org/wiki/FAQ#Q.29_How_can_I_access_the_.zfs_snapshot_directories.3F
        # These notes seem out of date. I'll do what I can without them
        #$ sudo zfs set snapdir=visible tank/bob
        #$ sudo zfs mount tank/bob@yesterday
        #$ ls -l /tank/bob/.zfs/snapshot/yesterday/


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