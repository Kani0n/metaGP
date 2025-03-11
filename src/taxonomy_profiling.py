#!/user/bin/env python3

import pandas as pd
import os
import multiprocessing as mp

import util, config
import taxonomy_profiling_stats as stats
    

def exec_metaphlan(sample, fwd, rev, config_file, process_dir, category, del_bowtieout):
    # metaphlan without usgbs or with usgbs
    samdir = os.path.join(process_dir, 'taxonomic_profile', category, 'sam')
    bowtiedir = os.path.join(process_dir, 'taxonomic_profile', category, 'bowtie2')
    profiledir = os.path.join(process_dir, 'taxonomic_profile', category, 'profiles')
    util.create_dir(samdir)
    util.create_dir(bowtiedir)
    util.create_dir(profiledir)
    samout = os.path.join(samdir, sample + '.sam.bz2')
    bowtieout = os.path.join(bowtiedir, sample + '.bowtie2.bz2')
    tax_prof = os.path.join(profiledir, sample + '.txt')
    
    # execute Metaphlan
    # if os.path.isfile(os.path.join(util.read_config(config_file,'Taxonomy_Profile','taxo_db'),'mpa_latest')):
    #     fp = open(os.path.join(util.read_config(config_file,'Taxonomy_Profile','taxo_db'),'mpa_latest'))
    #     idx = fp.readline()
    # else:
    #     print('Information of the index file not found. Missing mpa_latest file in the folder.')
    #     exit()

    taxonomy_index = config.read_from_config(config_file, 'Taxonomy_Profile', 'taxonomy_index')
    taxonomy_db = config.read_from_config(config_file, 'Taxonomy_Profile', 'taxonomy_db') 
    cmd = 'metaphlan ' + fwd + ',' + rev + ' -o ' + tax_prof + ' --input_type fastq'
    cmd += ' -s ' + samout + ' --bowtie2db ' + taxonomy_db + ' -x ' + taxonomy_index + ' --bowtie2out ' + bowtieout + ' --nproc 16 -t rel_ab_w_read_stats'
    if category == 'ignore_usgbs':
        cmd += ' --ignore_usgbs'
    os.system(cmd)
    if del_bowtieout:
        os.remove(bowtieout)


def taxonomy_profiling_parallel(item):
    sample, fwd, rev, process_dir = item
    config_file = config.read_config(process_dir)
    output_dir = os.path.join(process_dir, 'taxonomic_profile')
    util.create_dir(output_dir)
    for category in ['ignore_usgb','usgb']:
        exec_metaphlan(sample, fwd, rev, config_file, process_dir, category, del_bowtieout=False)
    stats.taxoprof_stats(config_file, process_dir)


def run_taxonomy_profiling(process_dir):
    df_mapping = util.adjust_paths(pd.read_csv(os.path.join(process_dir, 'quality_control', 'samples_to_process.tab'), sep='\t'), process_dir)
    config_file = config.read_config(process_dir)

    item = []
    for idx in df_mapping.index:
        sample = df_mapping.loc[idx,'SampleID']
        fwd = df_mapping.loc[idx,'Forward_read']
        rev = df_mapping.loc[idx,'Reverse_read']
        item.append([sample, fwd, rev, config_file, process_dir])
    pool = mp.Pool(min(int(mp.cpu_count()/2), len(item)))
    # parallel execution of taxonomy_profiling
    result = pool.map(taxonomy_profiling_parallel, item)
    print(result)
    # taxonomy_profiling report
    stats.taxoprof_stats(config_file, process_dir)
