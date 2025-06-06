#!/user/bin/env python3

import os
import configparser


#------------------------------------------------------------------------------------
# Actual creation
#------------------------------------------------------------------------------------
def create_configfile(input_dir, adapter, hostdb, minlength, headcrop, min_readcount, taxo_db, taxo_idx, abundace, prevalence, metafile, metafile_sep, sampleid, metainfo, taxlbl, nt_db, pro_db, bw_db, bowtie_idx):
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
                            'seperator_for_metafile'    : metafile_sep,
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
def make_config(project_dir, input_dir):

    # DEFAULT PARAMETERS
    adapter = os.path.join(project_dir, 'static/adapters/TruSeq3-PE.fa')
    hostdb = os.path.join(project_dir, 'static/database/hostdb')
    minlength = 50
    headcrop = 10
    min_readcount = 4000000
    taxo_db = os.path.join(project_dir, 'static/database/bowtie2db')
    taxo_idx = 'mpa_vOct22_CHOCOPhlAnSGB_202212'
    abundance = 0.2
    prevalence = 30.5
    metafile = '/path/to/metafile.csv'
    metafile_sep = ','
    samplecol = 'e.g. sampleID'
    metacol = 'e.g. treatment'
    taxlbl = 'g'
    nt_db = os.path.join(project_dir, 'static/database/bowtie2db/mpa_vOct22_CHOCOPhlAnSGB_202212')
    pro_db = os.path.join(project_dir, 'static/database/protein_db/uniref')
    bw_db = os.path.join(project_dir, 'static/database/bowtie2db')
    bowtie_idx = 'mpa_vOct22_CHOCOPhlAnSGB_202212'

    config = create_configfile(input_dir, adapter, hostdb, minlength, headcrop, min_readcount, taxo_db, taxo_idx, abundance, prevalence, metafile, metafile_sep, samplecol, metacol, taxlbl, nt_db, pro_db, bw_db, bowtie_idx)
    
    print_config(config)


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


#------------------------------------------------------------------------------------
# Get config file
#------------------------------------------------------------------------------------
def read_config(process_dir):
    config = configparser.ConfigParser()
    config.read(os.path.join(process_dir, 'config.info'))
    return config


#------------------------------------------------------------------------------------
# Read config file
#------------------------------------------------------------------------------------
def read_from_config(config, section, item):
    return config.get(section, item)
