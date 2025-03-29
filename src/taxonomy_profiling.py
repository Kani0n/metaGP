#!/user/bin/env python3

import multiprocessing as mp
import os

import util, config
    

def exec_metaphlan(sample, fwd, rev, config_file, process_dir, category, nCores):
    # metaphlan without usgbs or with usgbs
    samdir = os.path.join(process_dir, category, 'sam')
    bowtiedir = os.path.join(process_dir, category, 'bowtie2')
    profiledir = os.path.join(process_dir, category, 'profiles')
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
    cmd += ' --nproc ' + nCores
    os.system(cmd)


def run_taxonomy_profiling(sample, fwd, rev, process_dir, nCores):
    config_file = config.read_config(process_dir)
    for category in ['ignore_usgb','usgb']:
        exec_metaphlan(sample, fwd, rev, config_file, process_dir, category, nCores)
