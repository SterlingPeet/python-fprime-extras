from os import linesep
from os import sep
from os.path import abspath
from os.path import join as join_dir

class ExtrasFile(object):
    """File manager for fprime extras file interactions."""
    def __init__(self, filename=None):
        super(ExtrasFile, self).__init__()
        self.filename = filename
        self.full_filename = abspath(filename)
        self._loaded = False
        self._orig_contents = None
        self._orig_contents_lines = None
        self._orig_contents_pos = 0
        self._orig_contents_lines_pos = 0
        self._backup_flag = False
        self._write_flag = False
        self._write_handle = None

    def read(self, size):
        if not self._loaded:
            self.load_file_contents()
        ret = self._orig_contents
        content_size = len(self._orig_contents)
        if size is not None:
            end = self._orig_contents_pos + size
            if end >= content_size:
                end = content_size
            # print("File len {}, pos {}, end {}, requested {}".format(content_size, self._orig_contents_pos, end, size))
            ret = self._orig_contents[self._orig_contents_pos:end]
            self._orig_contents_pos = end
        return ret

    def readline(self):
        if not self._loaded:
            self.load_file_contents()
        ret = None
        if self._orig_contents_lines_pos <= len(self._orig_contents_lines):
            ret = self._orig_contents_lines[self._orig_contents_lines_pos]
            self._orig_contents_lines_pos += 1
        return ret

    def resolve_relative_path(self, file_path):
        this_path = self.full_filename.split(sep)
        this_path.pop()
        return join_dir(sep.join(this_path), file_path)

    def load_file_contents(self):
        with open(self.filename, 'rb') as f:
            self._orig_contents = f.read()
            self._orig_contents_lines = self._orig_contents.split(bytearray(linesep, 'utf-8'))
            self._loaded = True

    def _write_backup(self):
        if not self._backup_flag:
            with open('.{}.{}'.format(self.filename, '0.bak'), 'wb') as f:
                f.write(self._orig_contents)
                self._backup_flag = True

    def write(self, contents):
        if not self._loaded:
            self.load_file_contents()
        self._write_backup()
        if not self._write_flag:
            self._write_handle = open(self.filename, 'wb')
            self._write_flag = True

        self._write_handle.write(contents)

    def __del__(self):
        if self._write_flag:
            self._write_handle.close()
