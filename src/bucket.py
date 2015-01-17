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
    if args.validate:
        validate_bucket(args)
    else:
        bucket_files(args)


def bucket_files (args):
    for file_path in args.files:
        bucket_file(file_path, args)


def bucket_file (file_path, args):
    file_basename = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    extensions = mimetypes.guess_all_extensions(mime_type)
    digest = git_style_hash_object(file_path)
    bucket_relative_dir = os.path.join(*list(digest))
    bucket_full_dir = os.path.join(args.bucket, bucket_relative_dir)
    bucket_file_name = digest
    bucket_relative_path = os.path.join(bucket_relative_dir, bucket_file_name)
    bucket_full_path = os.path.join(bucket_full_dir, bucket_file_name)
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
                return
        if args.move:
            shutil.move(file_path, bucket_full_path)
        else:
            shutil.copy(file_path, bucket_full_path)
        file_attributes = xattr.xattr(bucket_full_path)
        file_attributes.set('user.mime_type', mime_type)
        file_attributes.set('user.bucket.sha1', digest)
        file_attributes.set('user.bucket.original_filename', file_basename)
        for extension in extensions:
            os.symlink(bucket_file_name, bucket_full_path + extension)
    if not args.verbose:
        print bucket_relative_path


def validate_bucket (args):
    for (dirpath, dirnames, filenames) in os.walk(args.bucket):
        relpath = os.path.relpath(dirpath, args.bucket)
        for filename in filenames:
            errors = False
            split_path = completely_split_path(relpath)
            name_hash = list(filename)[:len(split_path)]
            digest = git_style_hash_object(os.path.join(dirpath, filename))
            if split_path != name_hash:
                warn('{0} stored at invalid path {1}'.format(
                     filename, relpath))
                errors = True
            if ''.join(name_hash) != digest:
                warn('{0} does not match hash {1}'.format(
                    filename, digest))
                errors = True
            if not errors:
                print '{0} OK'.format(filename)


def completely_split_path (path):
    head, tail = os.path.split(path)
    if head and tail:
        return completely_split_path(head) + [tail]
    else:
        return [tail]


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
    parser.add_argument('files', metavar='FILE', nargs='*',
                        help='FILEs to store in the bucket')
    parser.add_argument('bucket', metavar='DIR',
                        help='DIRectory to use to store the bucket') 
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display more information about where files will be bucketed')
    parser.add_argument('-n', '--noop', action='store_true',
                        help='do not actually bucket any files')
    parser.add_argument('-m', '--move', action='store_true',
                        help='move, rather than copy, bucketed files')
    parser.add_argument('-V', '--validate', action='store_true',
                        help='validate all files in the bucket')
    parser.set_defaults(
        noop = False,
        verbose = False,
        move = False,
        validate = False,
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


def warn (message):
    print >>sys.stderr, message


if __name__ == '__main__':
    main()
