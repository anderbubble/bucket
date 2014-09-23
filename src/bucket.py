#!/usr/bin/python



import argparse
import hashlib
import mimetypes
import os


def main ():
    args = build_parser().parse_args()
    print 'bucket:', args.bucket
    for file_path in args.files:
        mimetype, _ = mimetypes.guess_type(file_path)
        extension = mimetypes.guess_extension(mimetype)
        digest = git_style_hash_object(file_path)
        bucket_path = '{path}{extension}'.format(
            path = os.path.join(*([args.bucket] + list(digest) + [digest])),
            extension = extension,
        )
        print '{source_file} -> {bucket_destination}'.format(
            source_file = file_path,
            bucket_destination = bucket_path,
        )


def build_parser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', metavar='FILE', nargs='+',
                        help='FILEs to store in the bucket')
    parser.add_argument('bucket', metavar='DIR',
                        help='DIRectory to use to store the bucket') 
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
