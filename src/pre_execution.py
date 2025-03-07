#!/user/bin/env python3

import os
import multiprocessing as mp
import pandas as pd

import util, mapping
import pre_execution_stats as stats


#------------------------------------------------------------------------------------
# Compute the histogram of the read counts
#------------------------------------------------------------------------------------
def count_distribution(sample, fwd, rev, process_dir):
    #print("Submitting pre_execution for sample: {}".format(sample))
    rd_count = util.count_reads([fwd, rev])
    df = pd.DataFrame([sample] + rd_count).T
    df.columns = ['SampleID', 'Raw_F', 'Raw_F.Count', 'Raw_R', 'Raw_R.Count']
    output_dir = os.path.join(process_dir, 'stats')
    util.create_dir(output_dir)
    df.to_csv(os.path.join(output_dir, sample + '.stat'), sep='\t', index=False)


#------------------------------------------------------------------------------------
# Compute the histogram of the read counts
#------------------------------------------------------------------------------------
def pre_process_parallel(item):
    sample, fwd, rev, process_dir = item
    count_distribution(sample, fwd, rev, process_dir)
    output_dir = os.path.join(process_dir, 'fastqc')
    util.call_fastqc([fwd, rev], output_dir)


#------------------------------------------------------------------------------------
# Main function for pre-processing
#------------------------------------------------------------------------------------
def run_pre_processing(project_dir, process_dir):
    mapping_file = mapping.read_mapping(project_dir)

    item = []
    for idx in mapping_file.index:
        sample = mapping_file.loc[idx, 'SampleID']
        fwd = mapping_file.loc[idx, 'Forward_read']
        rev = mapping_file.loc[idx, 'Reverse_read']
        item.append([sample, fwd, rev, process_dir])
    # Number of Parallel processing
    pool = mp.Pool(min(int(mp.cpu_count()/2), len(item)))

    # parallel execution of pre-execution
    result = pool.map(pre_process_parallel, item)
    print(result)
    # pre-execution report
    stats.qcheck_stats(process_dir)
