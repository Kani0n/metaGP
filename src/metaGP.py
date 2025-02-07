#!/user/bin/env python3

import argparse as ap
import os

import config

parser = ap.ArgumentParser()
parser.add_argument('-d', '--dir', dest='project_dir', type=str, required=True, 
                    help='Project directory.')
parser.add_argument('-i', '--indir', dest='input_dir', type=str, required=True, 
                    help='Input directory.')
args = parser.parse_args()

project_dir = args.project_dir
input_dir = args.input_dir

config.make_config(project_dir, input_dir)
