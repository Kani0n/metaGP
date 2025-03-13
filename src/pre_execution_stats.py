#!/user/bin/env python3

import pandas as pd
import os
import time
import matplotlib.pyplot as plt
import seaborn as sns


#------------------------------------------------------------------------------------
# Merge the statistic files of RAW DATA. The statistic files endswith '.stat' 
#------------------------------------------------------------------------------------
def merge_raw_stats(pre_out_dir, process_dir):
    frames = []
    count = 0
    for root, dirs, files in os.walk(pre_out_dir):
        for file in files:
            # check the extension of files
            if file.endswith('.stat'):
                # print whole path of files
                filename = os.path.join(root, file)
                frames.append(pd.read_csv(filename, sep='\t'))
                count += 1
    result = pd.concat(frames, ignore_index=True)
    result['Raw.Count'] = result[['Raw_F.Count', 'Raw_R.Count']].sum(axis=1)
    result = result.sort_values(by=['Raw.Count'], ascending=False)
    result['num'] = list(range(1, count + 1))
    cols = ['num', 'SampleID', 'Raw.Count']
    result = result[cols]
    outfile = os.path.join(process_dir, 'raw_readcount.tab')
    result.to_csv(outfile, sep='\t', index=False, header=True)

    fig, axs = plt.subplots(1, 1, figsize=(10, 5), tight_layout=True)
    sns.barplot(data=result, x='SampleID', y='Raw.Count', color='#2F70B3')
    plt.xticks(rotation=90)
    axs.set_ylabel('Raw read count')
    plt.savefig(os.path.join(process_dir, 'raw_readcount.png'))


def qcheck_stats(mapping_file, process_dir, output_dir):
    samples = pd.read_csv(mapping_file, sep='\t')['SampleID'].tolist()
    pre_out_dir = os.path.join(output_dir, 'pre')
    while not os.path.isdir(pre_out_dir) or set(samples) != set(os.listdir(pre_out_dir)):
        print('sleeping...')
        time.sleep(60)
    # to determine stat. for raw data
    merge_raw_stats(pre_out_dir, process_dir)
