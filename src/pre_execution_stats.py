#!/user/bin/env python3

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import util

#------------------------------------------------------------------------------------
# Merge the statistic files of RAW DATA. The statistic files endswith '.stat' 
#------------------------------------------------------------------------------------
def merge_raw_stats(stats_dir, output_dir):
    frames = []
    count = 0
    for f in os.listdir(stats_dir):
        if f.endswith('.stat'):
            filename = os.path.join(stats_dir, f)
            frames.append(pd.read_csv(filename, sep='\t'))
            count += 1
    result = pd.concat(frames, ignore_index=True)
    result['Raw.Count'] = result[['Raw_F.Count', 'Raw_R.Count']].sum(axis=1)
    result = result.sort_values(by=['Raw.Count'], ascending=False)
    result['num'] = list(range(1, count + 1))
    cols = ['num', 'SampleID', 'Raw.Count']
    result = result[cols]
    outfile = os.path.join(output_dir,'raw_readcount.tab')
    result.to_csv(outfile, sep='\t', index=False, header=True)

    fig, axs = plt.subplots(1, 1, figsize=(10, 5), tight_layout=True)
    sns.barplot(data=result, x='SampleID', y='Raw.Count', color='#2F70B3')
    plt.xticks(rotation=90)
    axs.set_ylabel('Raw read count')
    plt.savefig(os.path.join(output_dir,'raw_readcount.png'))


def qcheck_stats(process_dir):
    stats_dir = os.path.join(process_dir, 'stats')
    output_dir = os.path.join(process_dir, 'quality_control')
    util.create_dir(output_dir)
    # to determine stat. for raw data
    merge_raw_stats(stats_dir, output_dir)
