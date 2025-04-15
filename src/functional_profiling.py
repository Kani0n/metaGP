#!/user/bin/env python3

import pandas as pd
import multiprocessing as mp
import os

import util, config


def concat_pairs(sample, fwd, rev, output_dir):
    
    # concatenate pair-end reads
    concat_pair = os.path.join(output_dir, sample + '.fastq')
    if fwd.endswith('.gz') and rev.endswith('.gz'): 
        cmd = 'zcat ' + fwd + ' ' + rev + ' > ' + concat_pair
    else:
        cmd = 'cat ' + fwd + ' ' + rev + ' > ' + concat_pair
    print(cmd)
    os.system(cmd)

    # convert fastq to fasta
    x = os.system("sed -n '1~4s/^@/>/p;2~4p' " + concat_pair + " > " + concat_pair.replace('.fastq', '.fasta'))
    if x == 0:
        os.system('rm ' + concat_pair)
    
    return concat_pair.replace('.fastq', '.fasta')


# Execute Humann3
def exec_humann(concat_file, config_file, nCores):
    nucleotide_db = config.read_from_config(config_file, 'Functional_Profile', 'nucleotide_db') 
    protein_db = config.read_from_config(config_file, 'Functional_Profile', 'protein_db') 
    bowtie_db = config.read_from_config(config_file, 'Functional_Profile', 'bowtie_db') 
    bowtie_index = config.read_from_config(config_file, 'Functional_Profile', 'bowtie_index') 
    concat_dir = os.path.dirname(concat_file)

    cmd = 'humann --input ' + concat_file + ' --input-format fasta -o ' + concat_dir + ' --search-mode uniref90 --threads ' + str(2)
    cmd += ' --metaphlan-options="--index ' + bowtie_index + ' --bowtie2db ' + bowtie_db + ' --nproc ' + str(2 * nCores) + '" '
    cmd += '--nucleotide-database ' + nucleotide_db + ' --protein-database ' + protein_db + ' --bypass-nucleotide-index'
    print(cmd)
    os.system(cmd)


def run_functional_profiling_parallel(item):
    process_dir, sample, fwd, rev, config_file, nCores = item
    output_dir = os.path.join(process_dir, 'functional_profile', sample)
    util.create_dir(output_dir)
    concat_file = concat_pairs(sample, fwd, rev, output_dir)
    exec_humann(concat_file, config_file, nCores)


def run_functional_profiling(mapping_file, process_dir, nCores, nParallel):
    config_file = config.read_config(process_dir)
    df_mapping = pd.read_csv(mapping_file,sep='\t')
    item = []
    for idx in df_mapping.index:
        sample = df_mapping.loc[idx, 'SampleID']
        fwd = df_mapping.loc[idx, 'Forward_read']
        rev = df_mapping.loc[idx, 'Reverse_read']

        item.append([process_dir, sample, fwd, rev, config_file, nCores])

    pool = mp.Pool(min(nParallel, len(item)))
    pool.map(run_functional_profiling_parallel, item)
