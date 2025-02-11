#!/user/bin/env python3

import os


#------------------------------------------------------------------------------------
# Create a new directory at the location
#------------------------------------------------------------------------------------
def create_dir(dirpath):
    try:
        os.makedirs(dirpath, exist_ok=False)
    except OSError:
        pass


#------------------------------------------------------------------------------------
# Count the number of reads present in a fastq file
#------------------------------------------------------------------------------------
def count_reads(filelist):
    no_of_reads = []
    # if filelist contains filename as list
    if isinstance(filelist, list):
        for filename in filelist:
            if filename.endswith('.gz'):          
                no_of_lines = int(os.popen('zcat '+filename+'|wc -l').read().strip().split(' ')[0])
            else:
                no_of_lines = int(os.popen('wc -l ' +filename).read().strip().split(' ')[0])
            reads = int(no_of_lines/4)
            no_of_reads.extend([filename,reads])
    # if filelist contains a single filename as string
    elif isinstance(filelist, str):
        if filelist.endswith('.gz'):          
            no_of_lines = int(os.popen('zcat '+filelist+'|wc -l').read().strip().split(' ')[0])
        else:
            no_of_lines = int(os.popen('wc -l ' +filelist).read().strip().split(' ')[0])
        reads = int(no_of_lines/4)
        no_of_reads.extend([filelist,reads])
    return no_of_reads
