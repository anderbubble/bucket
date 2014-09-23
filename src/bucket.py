#!/usr/bin/python



import argparse


def main ():
    args = build_parser().parse_args()
    print args


def build_parser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', metavar='FILE', nargs='+',
                        help='FILEs to store in the bucket')
    parser.add_argument('bucket', metavar='DIR',
                        help='DIRectory to use to store the bucket') 
    return parser


if __name__ == '__main__':
    main()
