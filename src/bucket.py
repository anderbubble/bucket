#!/usr/bin/python


import argparse
import errno
import hashlib
import mimetypes
import os
import shutil
import sys
import xattr


def main ():
    args = build_parser().parse_args()
    for file_path in args.files:
        file_basename = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        digest = git_style_hash_object(file_path)
        bucket_relative_dir = os.path.join(*list(digest))
        bucket_full_dir = os.path.join(args.bucket, bucket_relative_dir)
        bucket_relative_path = os.path.join(bucket_relative_dir, digest)
        bucket_full_path = os.path.join(bucket_full_dir, digest)
        if args.verbose:
            print >>sys.stderr, '{mime_type} {source_file} -> {bucket_destination}'.format(
                mime_type = mime_type,
                source_file = file_path,
                bucket_destination = bucket_full_path,
            )
        if not args.noop:
            try:
                mkdir_p(bucket_full_dir)
            except OSError as ex:
                print >>sys.stderr, '{0}: {1}'.format(ex.strerror, bucket_full_dir)
                if not os.path.exists(bucket_full_dir):
                    continue
            if args.move:
                shutil.move(file_path, bucket_full_path)
            else:
                shutil.copy(file_path, bucket_full_path)
            file_attributes = xattr.xattr(bucket_full_path)
            file_attributes.set('user.mime_type', mime_type)
            file_attributes.set('user.bucket.sha1', digest)
            file_attributes.set('user.bucket.original_filename', file_basename)
        if not args.verbose:
            print bucket_relative_path


def mkdir_p (path):
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def build_parser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', metavar='FILE', nargs='+',
                        help='FILEs to store in the bucket')
    parser.add_argument('bucket', metavar='DIR',
                        help='DIRectory to use to store the bucket') 
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display more information about where files will be bucketed')
    parser.add_argument('-n', '--noop', action='store_true',
                        help='do not actually bucket any files')
    parser.add_argument('-m', '--move', action='store_true',
                        help='move, rather than copy, bucketed files')
    parser.set_defaults(
        noop = False,
        verbose = False,
        move = False,
    )
    return parser


def git_style_hash_object (file_path, blocksize=65536):
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


if __name__ == '__main__':
    main()
