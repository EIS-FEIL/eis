import fcntl
import os

class FileLock(object):
    def __init__(self, fn):
        self.fd = None
        self.fn = fn

    def __enter__(self):
        self.fd = open(self.fn, 'w')
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            return None
        self.fd.write('pid:%s\n' % os.getpid())
        self.fd.flush()
        return self

    def release(self):
        if self.fd:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            self.fd.close()
        self.fd = None

    def __exit__(self, type, value, traceback):
        self.release()
  
    def __del__(self):
        self.release()    

