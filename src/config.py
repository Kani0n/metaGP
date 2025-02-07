#!/user/bin/env python3

import os
from glob import glob
import pandas as pd
import configparser


def merge_readfile(input_dir, files, output_dir, tag):
    basedir = os.path.basename(input_dir)
    util.create_dir(output_dir)

    names = ''
    for f in files:
        names += f + ' '
    merged_filename = output_dir + '/'+ str(basedir) + '_' + str(tag) + '.fq.gz'
    cmd = 'cat ' + names + ' > ' + merged_filename
    os.system(cmd)
    return merged_filename


def create_mapping_file(project_dir, input_dir):
    output_dir = os.path.join(project_dir, 'config', 'tmp')

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
    df.to_csv(os.path.join(output_dir,'mapping_file.tab'), sep='\t', index=False)
    return(os.path.join(output_dir,'mapping_file.tab'))


def create_configfile(mapping_file, output_dir, adapter, hostdb, minlength, headcrop, min_readcount, taxo_db, taxo_idx, abundace, prevalence, metafile, sampleid, metainfo, taxlbl, nt_db, pro_db, bw_db, bowtie_idx):
    config = configparser.ConfigParser()
    config['General'] = {
                        'mapping_file' :   mapping_file,
                        'output_dir'   :   output_dir
    }
    config['QA'] = {
                        'adapter'       : adapter,
                        'host_db'       : hostdb,
                        'minlength'     : minlength,
                        'headcrop'      : headcrop,
                        'min_readcount' : min_readcount
    }
    config['Taxonomy_Profile'] = {
                                    'taxonomy_db'   : taxo_db,
                                    'taxonomy_index': taxo_idx
    }
    config['Diversity'] = {
                            'abundace_cutoff'           : abundace,
                            'prevalent_cutoff'          : prevalence,
                            'metafile_for_diversity'    : metafile,
                            'metafile_sampleid'         : sampleid,
                            'metafile_category'         : metainfo,
                            'tax_lbl_for_diversity'     : taxlbl
    }
    config['Functional_Profile'] = {
                                        'nucleotide_db' : nt_db, 
                                        'protein_db'    : pro_db,
                                        'bowtie_db'     : bw_db,
                                        'bowtie_index'  : bowtie_idx
    }

    with open(os.path.join(output_dir,'config.info'),'w') as fp:
        config.write(fp)


def make_config(project_dir, input_dir):

    # DEFAULT PARAMETERS
    adapter = 'tools/Trimmomatic-0.39/adapters/TruSeq3-PE.fa'
    hostdb = 'database/hostdb'
    minlength = 50
    headcrop = 10
    min_readcount = 4000000
    taxo_db = 'database/bowtie2db'
    taxo_idx = 'mpa_vOct22_CHOCOPhlAnSGB_202212'
    abundance = 0.2
    prevalence = 30.5
    metafile = '/path/to/the/metafile'
    samplecol = 'column_name_of_samples'
    metacol = 'column_name_of_metainfo'
    taxlbl = 'g'
    nt_db = 'database/bowtie2db/mpa_vOct22_CHOCOPhlAnSGB_202212'
    pro_db = 'database/protein_db/uniref'
    bw_db = 'database/bowtie2db'
    bowtie_idx = 'mpa_vOct22_CHOCOPhlAnSGB_202212'

    mapping_file = create_mapping_file(project_dir, input_dir)
    create_configfile(mapping_file, output_dir, adapter, hostdb, minlength, headcrop, min_readcount, taxo_db, taxo_idx, abundance, prevalence, metafile, samplecol, metacol, taxlbl, nt_db, pro_db, bw_db, bowtie_idx)

    if not os.path.isdir(dir):
        print('Data directory not found.')
        exit()
    
    with open(os.path.join(dir, 'out.txt'), 'r')as f:
        for line in f.readlines():
            print(line)
