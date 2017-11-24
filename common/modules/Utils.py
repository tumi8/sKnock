import errno
import stat
import pwd
import os
from OpenSSL import crypto

def convertDERtoPEM(key):
    return crypto.dump_publickey(crypto.FILETYPE_PEM, crypto.load_publickey(crypto.FILETYPE_ASN1, key))


def convertPEMtoDER(key):
    return crypto.dump_publickey(crypto.FILETYPE_ASN1, crypto.load_publickey(crypto.FILETYPE_PEM, key))


def touch(path):
    """
    Creates a file at the given path.

    If the directories in the given path are not existing, they are created
    recursively with the permissions on each of them deriving from the umask,
    but with an execute permission for others.  The created file will be owned
    by `nobody`

    If the path already exists then the ownership is changed to `nobody`.

    Throws OSError in case the given path is a directory, or upon no sufficient
    disk space
    """
    f_mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP
    try:
        mode = os.stat(path).st_mode
    except os.error as e:
        if errno.ENOENT != e.errno:
            raise e
        mask = os.umask(0)
        os.umask(mask ^ 1)  # enable dir access for others
        try:
            os.makedirs(os.path.dirname(path))
        except os.error as e:
            if errno.EEXIST != e.errno:
                raise e
        finally:
            os.umask(mask)
        f = os.open(path, os.O_CREAT, f_mode)
        os.close(f)
    else:
        f_mode = f_mode | mode & 0o777
        os.chmod(path, f_mode)
    # File will either be created or already existing by now change the
    # ownership of the file to nobody
    user = pwd.getpwnam('nobody')
    os.chown(path, user.pw_uid, -1)
