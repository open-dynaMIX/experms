#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import parse_arguments

def main():
    args = parse_arguments.ParseArgs()
    print args.args.debug

if __name__ == "__main__":
    main()
