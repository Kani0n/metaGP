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
                no_of_lines = int(os.popen('zcat '+ filename + '|wc -l').read().strip().split(' ')[0])
            else:
                no_of_lines = int(os.popen('wc -l ' + filename).read().strip().split(' ')[0])
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


#------------------------------------------------------------------------------------
# Count the number of reads present in a fastq file
#------------------------------------------------------------------------------------
def call_fastqc(files, output_dir):
    inputfile = ' '.join(files)
    create_dir(output_dir)
    cmd_fastqc = 'fastqc --quiet --outdir ' + output_dir + ' ' + inputfile
    os.system(cmd_fastqc)


#------------------------------------------------------------------------------------
# Adjusts fastq filepaths from a work dir to a published dir
#------------------------------------------------------------------------------------
def adjust_paths(df_mapping, process_dir):
    for read in ['Forward_read', 'Reverse_read']:
        new_paths = []
        for path in df_mapping[read]:
            filename = os.path.basename(path)
            new_paths.append(os.path.join(process_dir, 'decontamination', filename))
        df_mapping[read] = new_paths
    return df_mapping
