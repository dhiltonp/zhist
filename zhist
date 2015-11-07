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
import optparse
import sys, os, os.path, getopt


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


def zfs_split(f):
    """Returns f's full path, split into 3:
        the highest mount point: "/mount/point/", leading and trailing "/"
        the path within that mount point: "path/to/" with no leading but a trailing "/"
        the filename, if it exists. If not, ""

        An exception will be raised if:
         - the path does not exist
         - a symlink is passed in
         - the mount point found is not zfs (does not have a .zfs folder)
        """
    # does the file exist?
    if not os.path.exists(f):
        raise Exception("file does not exist: "+f)

    # get full path:
    f = os.path.abspath(f)
    if os.path.islink(f):
        raise Exception("symlinks not supported (use realpath): "+f)

    # get filename
    filename = ''
    if os.path.isfile(f):
        filename = f.split("/")[-1]
        f = '/'.join(f.split("/")[:-1])
    
    # get path to mount point
    mount_point = f
    while not os.path.ismount(mount_point):
        mount_point = os.path.dirname(mount_point)
    if mount_point[-1] is not '/':
        mount_point += '/'
    # check mount point for zfs-ness
    if not os.path.exists(mount_point+".zfs"):
        raise Exception("mount point isn't zfs('%s'): %s" % (mount_point, f))
    if not os.path.isdir(mount_point+".zfs/snapshot"):
        import platform
        error = "snapshots do not exist or cannot be accessed ('%s'): %s" % (mount_point, f)
        if platform.system() == "Darwin":
            error += "\n(MacOS requires that snapshots be manually mounted; see the O3X FAQ)"
        raise Exception(error)
    
    # get path from mount point
    zfs_path = f[len(mount_point):]
    if len(zfs_path) > 0 and zfs_path[-1] != '/':
        zfs_path += "/"

    return mount_point, zfs_path, filename


def ls(files):
    files = files[0]
    if len(files) == 0:
        files.append('.')

    for f in files:
        try:
            mount_point, zfs_path, filename = zfs_split(f)
        except Exception as e:
            print e




def parse_arguments():
    parser = argparse.ArgumentParser("Lists all available snapshot versions of a specified file or directory.")
    parser.add_argument("file", action="append", nargs='*', help="file or directories to list")
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    ls(args.file)

if __name__ == "__main__":
    sys.exit(main())
