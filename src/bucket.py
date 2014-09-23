#!/usr/bin/python



import argparse
import hashlib
import mimetypes
import os


def main ():
    args = build_parser().parse_args()
    print 'bucket:', args.bucket
    for file_path in args.files:
        extension = guess_extension(file_path, args.extensions)
        digest = git_style_hash_object(file_path)
        bucket_path = '{path}{extension}'.format(
            path = os.path.join(*([args.bucket] + list(digest) + [digest])),
            extension = extension,
        )
        print '{source_file} -> {bucket_destination}'.format(
            source_file = file_path,
            bucket_destination = bucket_path,
        )


def guess_extension (file_path, preferred_extensions=[]):
    mimetype, _ = mimetypes.guess_type(file_path)
    if preferred_extensions:
        valid_extensions = [
            extension.lower()
            for extension in mimetypes.guess_all_extensions(mimetype)
        ]
        for extension in preferred_extensions:
            if extension.lower() in valid_extensions:
                return extension

    return mimetypes.guess_extension(mimetype)


def build_parser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', metavar='FILE', nargs='+',
                        help='FILEs to store in the bucket')
    parser.add_argument('bucket', metavar='DIR',
                        help='DIRectory to use to store the bucket') 
    parser.add_argument('-x', '--extension', dest='extensions',
                        metavar='EXT', nargs='*',
                        help='prefer these EXTensions when bucketing files')
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
