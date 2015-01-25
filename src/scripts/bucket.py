#!/usr/bin/python


import argparse
import filebucket
import errno
import os
import sys


def main ():
    args = build_parser().parse_args()
    bucket = filebucket.FileBucket(args.bucket)
    if args.action == 'add':
        for file_path in args.files:
            bucket.add(file_path, move=args.move)
    elif args.action == 'list':
        for item in bucket:
            metadata = bucket.get_metadata(item)
            print item, metadata['Content-Type']
    elif args.action == 'validate':
        for message in bucket.validate():
            warn(message)
    else:
        print >>sys.stderr, 'invalid action {0}'.format(args.action)


def build_parser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('action')
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
    parser.set_defaults(
        noop = False,
        verbose = False,
        move = False,
    )
    return parser


def warn (message):
    print >>sys.stderr, message


if __name__ == '__main__':
    main()
