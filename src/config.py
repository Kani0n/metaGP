#!/user/bin/env python3

import os
import configparser


#------------------------------------------------------------------------------------
# Actual creation
#------------------------------------------------------------------------------------
def create_configfile(input_dir, adapter, hostdb, minlength, headcrop, min_readcount, taxo_db, taxo_idx, abundace, prevalence, metafile, sampleid, metainfo, taxlbl, nt_db, pro_db, bw_db, bowtie_idx):
    config = configparser.ConfigParser()
    config['General'] = {
                        'input_dir'    :   input_dir,
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
    return config


#------------------------------------------------------------------------------------
# Main function for creating config file
#------------------------------------------------------------------------------------
def make_config(input_dir):

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

    config = create_configfile(input_dir, adapter, hostdb, minlength, headcrop, min_readcount, taxo_db, taxo_idx, abundance, prevalence, metafile, samplecol, metacol, taxlbl, nt_db, pro_db, bw_db, bowtie_idx)
    
    print_config(config)

    #if not os.path.isdir(dir):
    #    print('Data directory not found.')
    #    exit()
    #
    #with open(os.path.join(dir, 'out.txt'), 'r')as f:
    #    for line in f.readlines():
    #        print(line)


#------------------------------------------------------------------------------------
# Print config file
#------------------------------------------------------------------------------------
def print_config(config):
    configstr = ''
    for section in config.sections():
        print('[{}]'.format(section))
        configstr += '[{}]\n'.format(section)
        for option in config.options(section):
            if option in ['pre_execution','qa_execution','taxo_execution','div_execution','func_exection']:
                val = config.getboolean(section, option) 
            elif option in ['headcrop']:
                val = config.getint(section, option) 
            elif option in ['abundace_cutoff','prevalent_cutoff']:
                val = config.getfloat(section, option)
            else:
                val = config.get(section, option)
            print('{} = {}'.format(option,val))
            configstr += '{} = {}\n'.format(option,val)
    return configstr
