#!/user/bin/env python3

import argparse as ap

import mapping, config

parser = ap.ArgumentParser()
parser.add_argument('--mapping', dest='mapping_exec', action='store_true', default=False, 
                    help='Option for creating mapping file.')
parser.add_argument('--config', dest='config_exec', action='store_true', default=False, 
                    help='Option for creating config file.')
parser.add_argument('--pre', dest='pre_exec', action='store_true', default=False, 
                    help='Option for performing pre-execution.')
parser.add_argument('--qc', dest='qc_exec', action='store_true', default=False, 
                    help='Option for performing quality control.')
parser.add_argument('--taxo', dest='taxo_exec', action='store_true', default=False, 
                    help='Option for performing taxonomy profiling.')
parser.add_argument('--div', dest='div_exec', action='store_true', default=False, 
                    help='Option for performing diversity analysis.')
parser.add_argument('--func', dest='func_exec', action='store_true', default=False, 
                    help='Option for performing functional analysis.')
parser.add_argument('-d', '--dir', dest='process_dir', type=str, required=True, 
                    help='Prcess directory.')
parser.add_argument('-i', '--indir', dest='input_dir', type=str, required=True, 
                    help='Input directory.')
args = parser.parse_args()

MAPPING = args.mapping_exec
CONFIG = args.config_exec
PRE = args.pre_exec
QC = args.qc_exec
TAXO = args.taxo_exec
DIV = args.div_exec
FUNC = args.func_exec
process_dir = args.process_dir
input_dir = args.input_dir

if MAPPING:
    mapping.make_mapping(process_dir, input_dir)
elif CONFIG:
    config.make_config(input_dir)
elif PRE:
    pass
elif QC:
    pass
elif TAXO:
    pass
elif DIV:
    pass
elif FUNC:
    pass
