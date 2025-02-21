#!/user/bin/env python3

import argparse as ap
import pandas as pd

import mapping, config, pre_execution, quality_control, taxonomy_profiling, diversity_execution, functional_profiling

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
parser.add_argument('-d', '--dir', dest='project_dir', type=str,
                    help='Project directory.')
parser.add_argument('-p', '--p-dir', dest='process_dir', type=str,
                    help='Prcess directory.')
parser.add_argument('-i', '--indir', dest='input_dir', type=str,
                    help='Input directory.')
args = parser.parse_args()

MAPPING = args.mapping_exec
CONFIG = args.config_exec
PRE = args.pre_exec
QC = args.qc_exec
TAXO = args.taxo_exec
DIV = args.div_exec
FUNC = args.func_exec
project_dir = args.project_dir
process_dir = args.process_dir
input_dir = args.input_dir

pd.set_option('display.max_colwidth', None)

if MAPPING:
    mapping.make_mapping(process_dir, input_dir)
elif CONFIG:
    config.make_config(project_dir, input_dir)
elif PRE:
    pre_execution.run_pre_processing(project_dir, process_dir)
elif QC:
    quality_control.run_quality_control(project_dir, process_dir)
elif TAXO:
    taxonomy_profiling.run_taxonomy_profiling(project_dir, process_dir)
elif DIV:
    diversity_execution.run_diversity_execution(project_dir, process_dir)
elif FUNC:
    functional_profiling.run_functional_profiling(project_dir, process_dir)
