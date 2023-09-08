#!/usr/bin/env python3

import os
import sys
import argparse
import pandas as pd
import socket

sys.path.append(os.path.dirname(__name__))

from app import app, main

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in_file", type=str, default='./crowdsourcing.csv', help="Input CSV file.")
    parser.add_argument("-n", "--num_rel", type=int, default=5, help="Number of described relations.")
    parser.add_argument("-o", "--out_dir", type=str, default="./responses", help="Output directory.")
    parser.add_argument("-c", "--compl_code", type=str, default="DUMMY_CODE", help="Prolific completion code.")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)

    if socket.gethostname() == "nlg":
        app.run(debug=True, host="10.10.51.97", port=80)
    else:
        app.run(debug=True)
