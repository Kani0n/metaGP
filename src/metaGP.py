#!/user/bin/env python3

import argparse as ap
import pandas as pd

import mapping, config, pre_execution, quality_control, taxonomy_profiling, diversity_execution, functional_profiling
import pre_execution_stats, quality_control_stats, taxonomy_profiling_stats, functional_profiling_stats

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

parser.add_argument('--pres', dest='pre_stats', action='store_true', default=False, 
                    help='Option for performing pre-execution stats.')
parser.add_argument('--qcs', dest='qc_stats', action='store_true', default=False, 
                    help='Option for performing quality control stats.')
parser.add_argument('--taxos', dest='taxo_stats', action='store_true', default=False, 
                    help='Option for performing taxonomy profiling stats.')
parser.add_argument('--funcs', dest='func_stats', action='store_true', default=False, 
                    help='Option for performing functional analysis stats.')

parser.add_argument('-d', '--dir', dest='project_dir', type=str,
                    help='Project directory.')
parser.add_argument('-p', '--p-dir', dest='process_dir', type=str,
                    help='Prcess directory.')
parser.add_argument('-i', '--indir', dest='input_dir', type=str,
                    help='Input directory.')
parser.add_argument('-o', '--outdir', dest='output_dir', type=str,
                    help='Output directory.')
parser.add_argument('-m', '--map', dest='mapping', type=str,
                    help='Path to mapping file.')

parser.add_argument('-s', '--sample', dest='sample', type=str,
                    help='sample ID.')
parser.add_argument('-f', '--fwd', dest='fwd', type=str,
                    help='Path to forward read file.')
parser.add_argument('-r', '--rev', dest='rev', type=str,
                    help='Path to reverse read file.')

args = parser.parse_args()

MAPPING = args.mapping_exec
CONFIG = args.config_exec
PRE = args.pre_exec
PRES = args.pre_stats
QC = args.qc_exec
QCS = args.qc_stats
TAXO = args.taxo_exec
TAXOS = args.taxo_stats
DIV = args.div_exec
FUNC = args.func_exec
FUNCS = args.func_stats

project_dir = args.project_dir
process_dir = args.process_dir
input_dir = args.input_dir
output_dir = args.output_dir
mapping_file = args.mapping

sample = args.sample
fwd = args.fwd
rev = args.rev

pd.set_option('display.max_colwidth', None)

if MAPPING:
    mapping.make_mapping(process_dir, input_dir)
elif CONFIG:
    config.make_config(project_dir, input_dir)
elif PRE:
    pre_execution.run_pre_processing([sample, fwd, rev, process_dir])
elif PRES:
    pre_execution_stats.qcheck_stats(mapping_file, process_dir, output_dir)
elif QC:
    quality_control.run_quality_control([sample, fwd, rev, process_dir])
elif QCS:
    quality_control_stats.qcheck_stats(mapping_file, process_dir, output_dir)
elif TAXO:
    taxonomy_profiling.run_taxonomy_profiling([sample, fwd, rev, process_dir])
elif TAXOS:
    taxonomy_profiling_stats.taxoprof_stats(mapping_file, process_dir, output_dir)
elif DIV:
    diversity_execution.run_diversity_execution(process_dir)
elif FUNC:
    functional_profiling.run_functional_profiling([sample, fwd, rev, process_dir])
elif FUNCS:
    functional_profiling_stats.funcprof_stats(mapping_file, process_dir, output_dir)
