# strmode.h translated into python
#
# Original Copyright (c) 1990, 1993
# 	  The Regents of the University of California.  All rights reserved.
#
# Copyright (c) 2015 "David Hilton" <david.hilton.p@gmail.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 4. Neither the name of the University nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
                                                                    # OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

from stat import *


def strmode(mode):
    """
    This returns a human-readable mode.
    It is a direct port of strmode from C. Just like strmode, it does not report ACL existence.

    If you do not need python2 compatibility, use python3's stat.filemode.

    :param mode: st_mode, as returned from stat
    :return: human-readable mode like "-rw-r--r--". ACL existence not reported
    """
    output = ""

    # file type?
    if S_ISDIR(mode):
        output+="d"
    elif S_ISCHR(mode):
        output+="c"
    elif S_ISBLK(mode):
        output+="b"
    elif S_ISREG(mode):
        output+="-"
    elif S_ISLNK(mode):
        output+="l"
    elif S_ISSOCK(mode):
        output+="s"
    elif S_ISFIFO(mode):
        output+="p"
    #elif S_ISWHT(mode):  # I don't know what a whiteout is and python doesn't support it.
    #    output+="w"
    else:
        output+="?"


    # user readable?
    if mode & S_IRUSR:
        output+="r"
    else:
        output+="-"

    # user writeable?
    if mode & S_IWUSR:
        output+="w"
    else:
        output+="-"

    # user executeable?
    tmp = mode & (S_IXUSR | S_ISUID)
    if tmp==0:
        output+="-"
    elif tmp==S_IXUSR:
        output+="x"
    elif tmp==S_ISUID:
        output+="S"
    else:
        output+="s"


    # group readable?
    if mode & S_IRGRP:
        output+="r"
    else:
        output+="-"

    # group writeable?
    if mode & S_IWGRP:
        output+="w"
    else:
        output+="-"

    # group executeable?
    tmp = mode & (S_IXGRP | S_ISGID)
    if tmp==0:
        output+="-"
    elif tmp==S_IXGRP:
        output+="x"
    elif tmp==S_ISGID:
        output+="S"
    else:
        output+="s"


    # other readable?
    if mode & S_IROTH:
        output+="r"
    else:
        output+="-"

    # other writeable?
    if mode & S_IWOTH:
        output+="w"
    else:
        output+="-"

    # group executeable?
    tmp = mode & (S_IXOTH | S_ISVTX)
    if tmp==0:
        output+="-"
    elif tmp==S_IXOTH:
        output+="x"
    elif tmp==S_ISVTX:
        output+="S"
    else:
        output+="s"


    return output