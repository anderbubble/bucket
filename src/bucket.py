#!/usr/bin/python



import argparse
import hashlib
import os


def main ():
    args = build_parser().parse_args()
    print 'bucket:', args.bucket
    for file_path in args.files:
        print git_style_hash_object(file_path), file_path


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
