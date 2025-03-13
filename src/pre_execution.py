#!/user/bin/env python3

import os
import pandas as pd

import util


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
# Main function for pre-processing
#------------------------------------------------------------------------------------
def run_pre_processing(item):
    sample, fwd, rev, process_dir = item
    count_distribution(sample, fwd, rev, process_dir)
    output_dir = os.path.join(process_dir, 'fastqc')
    util.call_fastqc([fwd, rev], output_dir)
