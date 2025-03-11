#!/user/bin/env python3

import os
from glob import glob
import pandas as pd

import util


#------------------------------------------------------------------------------------
# Merging multiple fastq files
#------------------------------------------------------------------------------------
def merge_readfile(dir, files, output_dir, strand):
    basedir = os.path.basename(dir)
    util.create_dir(output_dir)

    names = ''
    for f in files:
        names += f + ' '
    merged_filename = output_dir + '/'+ str(basedir) + '_' + str(strand) + '.fq.gz'
    cmd = 'cat ' + names + ' > ' + merged_filename
    os.system(cmd)
    return merged_filename


#------------------------------------------------------------------------------------
# Actual creation
#------------------------------------------------------------------------------------
def create_mapping_file(process_dir, input_dir):

    #if not os.path.isdir(input_dir):
    #    print('Data directory not found.')
    #    exit()
    #

    output_dir = os.path.join(process_dir, 'tmp')

    metainfo = []
    dirlist = [ name for name in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, name)) ]
    sample_num = 0
    for dir in dirlist:
        sample_num += 1
        sample = [sample_num, dir]
        dir = os.path.join(input_dir, dir)
        fwd_file = [f for f in glob(dir + "/*_1.*.gz")]
        fwd_file.sort()
        if len(fwd_file) > 1:
            filename = merge_readfile(dir, fwd_file, output_dir, '1')
            sample.append(filename)
        else:
            # filename = copyfile(dir, fwd_file, output_dir, '1')
            sample.append(fwd_file[0])
        rev_file = [f for f in glob(dir + "/*_2.*.gz")]
        rev_file.sort()
        if len(rev_file) > 1:
            filename = merge_readfile(dir, rev_file, output_dir, '2')
            sample.append(filename)
        else:
            # filename = copyfile(dir, rev_file, output_dir, '2')
            sample.append(rev_file[0])
        metainfo.append(sample)
        
    df = pd.DataFrame(metainfo, columns =['Num','SampleID', 'Forward_read', 'Reverse_read'])
    return(df)


#------------------------------------------------------------------------------------
# Main function for creating mapping file
#------------------------------------------------------------------------------------
def make_mapping(process_dir, input_dir):
    mapping_file = create_mapping_file(process_dir, input_dir)
    mapping_file.to_csv(os.path.join(process_dir, 'mapping.tab'), sep='\t', index=False)
    #print(mapping_file.to_string(index=False))


#------------------------------------------------------------------------------------
# Reading mapping file
#------------------------------------------------------------------------------------
def read_mapping(process_dir):
    return pd.read_csv(os.path.join(process_dir, 'mapping.tab'), sep='\t', header=0, index_col=False)
