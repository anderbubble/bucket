import hashlib
import mimetypes
import os
import re
import shutil
import xattr


class FileBucket (object):


    def __init__ (self, path):
        self.path = path


    def add (self, file_path, move=False):
        file_basename = os.path.basename(file_path)
        digest = git_style_hash(file_path)
        bucket_full_path = self.get_file(digest)

        mkdir_p(os.path.dirname(bucket_full_path))
        if move:
            shutil.move(file_path, bucket_full_path)
        else:
            shutil.copy(file_path, bucket_full_path)

        mime_type, _ = mimetypes.guess_type(file_path)
        file_attributes = xattr.xattr(bucket_full_path)
        file_attributes.set('user.bucket.original_filename', file_basename)
        file_attributes.set('user.bucket.sha1', digest)
        if mime_type is not None:
            file_attributes.set('user.mime_type', mime_type)

        return digest


    def link_extensions (self, digest):
        original_filename = self.get_metadata(digest)['original-filename']
        mime_type, _ = mimetypes.guess_type(original_filename)
        extensions = mimetypes.guess_all_extensions(mime_type)

        bucket_full_path = self.get_file(digest)
        bucket_file_name = os.path.basename(bucket_full_path)

        for extension in extensions:
            os.symlink(bucket_file_name, ''.join((bucket_full_path, extension)))
        return extensions


    def get_file (self, digest):
        bucket_relative_dir = os.path.join(*list(digest))
        bucket_full_dir = os.path.join(self.path, bucket_relative_dir)
        bucket_file_name = digest
        bucket_full_path = os.path.join(bucket_full_dir, bucket_file_name)
        return bucket_full_path


    def get_metadata (self, digest):
        file_path = self.get_file(digest)
        file_attributes = xattr.xattr(file_path)
        metadata = {}
        if 'user.mime_type' in file_attributes:
            metadata['Content-Type'] = file_attributes.get('user.mime_type')
        metadata['sha1'] = file_attributes.get('user.bucket.sha1')
        metadata['original-filename'] = file_attributes.get('user.bucket.original_filename')
        return metadata


    def __iter__ (self):
        for (dirpath, dirnames, filenames) in os.walk(self.path):
            for filename in filenames:
                if is_git_style_hash(os.path.basename(filename)):
                    yield filename


    def validate (self):
        for basename in self:
            filename = self.get_file(basename)
            relpath = os.path.relpath(filename, self.path)
            metadata = self.get_metadata(basename)
            digest_from_path = get_digest_from_path(relpath)
            if digest_from_path != basename:
                yield '{0} stored at invalid path {1}'.format(
                    basename, relpath)
            digest = git_style_hash(filename)
            if digest != basename:
                yield '{0} does not match calculated hash {1}'.format(
                    basename, digest)
            if digest != metadata['sha1']:
                yield '{0} does not match stored hash {1}'.format(
                    basename, metadata['sha1'])


def mkdir_p (path):
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def get_digest_from_path (path):
    return ''.join(completely_split_path(os.path.dirname(path)))


def completely_split_path (path):
    head, tail = os.path.split(path)
    if head and tail:
        return completely_split_path(head) + [tail]
    else:
        return [tail]


def git_style_hash (file_path, blocksize=65536):
    filesize = os.stat(file_path).st_size
    sha1_hash = hashlib.sha1()
    sha1_hash.update("blob {0}\0".format(filesize))
    with open(file_path, 'rb') as file_:
        while True:
            buffer_ = file_.read(blocksize)
            if not buffer_:
                break
            else:
                sha1_hash.update(buffer_)
    return sha1_hash.hexdigest()


git_style_hash_p = re.compile(r'[0-9a-f]')


def is_git_style_hash (possible_digest):
    return (
        git_style_hash_p.match(possible_digest)
        and len(possible_digest) == 40)
