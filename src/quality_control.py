#!/user/bin/env python3

import os
import multiprocessing as mp
import pandas as pd

import util, mapping, config
import quality_control_stats as stats


def remove_blankspace(fwd, rev, output_dir):
    util.create_dir(output_dir)

    fwd_filename = os.path.split(fwd)[-1]
    rev_filename = os.path.split(rev)[-1]

    out_fwd_file = os.path.join(output_dir, fwd_filename)
    out_rev_file = os.path.join(output_dir, rev_filename)

    cmd = "gunzip -d -c " + fwd + " | sed -E 's/ 1:[^ ]*/\/1/g'| gzip -c > " + out_fwd_file
    os.system(cmd)
    cmd = "gunzip -d -c " + rev + " | sed -E 's/ 2:[^ ]*/\/2/g'| gzip -c > " + out_rev_file
    os.system(cmd)


# Execute Cutadapt on a file
def call_cutadapt(fwd, rev, output_dir, config_file):
    util.create_dir(output_dir)
    
    fwd_filename = os.path.split(fwd)[-1]
    rev_filename = os.path.split(rev)[-1]

    out_fwd_file = os.path.join(output_dir, fwd_filename)
    out_rev_file = os.path.join(output_dir, rev_filename)

    with open(config.read_from_config(config_file, 'QA', 'adapter'), 'r') as f:
        adap = [line.strip() for line in f if not line.startswith('>')] 

    fwd_adapter = adap[0]
    rev_adapter = adap[1]
    minlength = str(config.read_from_config(config_file, 'QA', 'minlength'))

    cmd = 'cutadapt --quiet -a ' + fwd_adapter + ' -A ' + rev_adapter + ' --cores=8 -m ' + minlength + ' -o ' + out_fwd_file + ' -p ' + out_rev_file + ' ' + fwd + ' ' + rev
    os.system(cmd)
    return out_fwd_file, out_rev_file


# Execute Kneaddata
def call_kneaddata(fwd, rev, output_dir, config_file, bypass_trf):
    util.create_dir(output_dir)

    refdb = [os.path.join(config.read_from_config(config_file, 'QA', 'host_db'), 'human/human_hg37dec_v0.1'), 
             os.path.join(config.read_from_config(config_file,'QA', 'host_db'), 'mouse/mouse_C57BL_6NJ')]
    adapter = config.read_from_config(config_file, 'QA', 'adapter')
    headcrop = config.read_from_config(config_file, 'QA', 'headcrop')

    cmd = 'kneaddata --input1 ' + fwd + ' --input2 ' + rev + ' -db ' + ' -db '.join(refdb) + ' --output ' + output_dir 
    cmd += ' --trimmomatic /mnt/main_hdd/miniconda3/envs/metaGP/share/trimmomatic-0.39-2/'
    cmd += ' --trimmomatic-options="ILLUMINACLIP:' + adapter + ':2:30:10"' + ' --trimmomatic-options="HEADCROP:' + str(headcrop) + '" --trimmomatic-options="LEADING:20"'
    if bypass_trf:
        cmd += ' --bypass-trf'  
    else:  
        cmd += ' --run-trim-repetitive --trf /mnt/main_hdd/miniconda3/envs/metaGP/bin/'
    cmd += ' --fastqc /mnt/main_hdd/miniconda3/envs/metaGP/bin/fastqc'
    cmd += ' --bowtie2 /mnt/main_hdd/miniconda3/envs/metaGP/bin/'
    cmd += ' --bowtie2-options="--quiet" --bowtie2-options="--threads 24" --processes 16 --threads 2'
    os.system(cmd)

    fwd_filename = os.path.split(fwd)[-1]
    rev_filename = os.path.split(rev)[-1]

    out_fwd_file = os.path.join(output_dir, fwd_filename.replace('.fq.gz', '_kneaddata_paired_1.fastq'))
    out_rev_file = os.path.join(output_dir, fwd_filename.replace('.fq.gz', '_kneaddata_paired_2.fastq'))
    util.call_fastqc([out_fwd_file, out_rev_file], os.path.join(output_dir, 'fastqc_kneaddata'))

    # count reads for files
    # no of repeat reads
    repeat_fwd = os.path.join(output_dir, fwd_filename.replace('.fq.gz', '_kneaddata.repeats.removed.1.fastq'))
    repeat_rev = os.path.join(output_dir, fwd_filename.replace('.fq.gz', '_kneaddata.repeats.removed.2.fastq'))
    if bypass_trf:
       fp = open(repeat_fwd,'w')
       fp = open(repeat_rev,'w')
    # no of trimmed reads
    trim_fwd = os.path.join(output_dir, fwd_filename.replace('.fq.gz', '_kneaddata.trimmed.1.fastq'))
    trim_rev = os.path.join(output_dir, fwd_filename.replace('.fq.gz', '_kneaddata.trimmed.2.fastq'))
    for host in refdb:
        hostname = os.path.basename(host)
        # num of contaminated reads (human)
        if 'human' in host:
            human_contam_fwd = os.path.join(output_dir, fwd_filename.replace('.fq.gz', '_kneaddata_' + hostname + '_bowtie2_paired_contam_1.fastq'))
            human_contam_rev = os.path.join(output_dir, fwd_filename.replace('.fq.gz', '_kneaddata_' + hostname + '_bowtie2_paired_contam_2.fastq'))
        # num of contaminated reads (mouse)
        elif 'mouse' in host:
            mouse_contam_fwd = os.path.join(output_dir, fwd_filename.replace('.fq.gz', '_kneaddata_' + hostname + '_bowtie2_paired_contam_1.fastq'))
            mouse_contam_rev = os.path.join(output_dir, fwd_filename.replace('.fq.gz', '_kneaddata_' + hostname + '_bowtie2_paired_contam_2.fastq'))
    return  [repeat_fwd, repeat_rev, trim_fwd, trim_rev, human_contam_fwd, human_contam_rev, mouse_contam_fwd, mouse_contam_rev, out_fwd_file, out_rev_file]


def quality_control_parallel(item):
    sample, fwd, rev, process_dir = item
    config_file = config.read_config(process_dir)
    
    report = []
    sample_report = [sample]

    # remove blank space from the read headers
    outdir = os.path.join(process_dir,'remove_blankspace')
    remove_blankspace(fwd, rev, outdir)
    rd_count = util.count_reads([fwd, rev])
    sample_report.extend(rd_count)
    
    # call cutadapt
    outdir = os.path.join(process_dir,'adapter_trimming')
    fwd, rev = call_cutadapt(fwd, rev, outdir, config_file)
    rd_count = util.count_reads([fwd, rev])
    sample_report.extend(rd_count)

    # call kneaddata
    outdir = os.path.join(process_dir,'decontamination')
    #repeat_fwd, repeat_rev, trim_fwd, trim_rev, human_contam_fwd, human_contam_rev, mouse_contam_fwd, mouse_contam_rev, fwd, rev = call_kneaddata(fwd, rev, outdir, config_file, bypass_trf = True)
    result = call_kneaddata(fwd, rev, outdir, config_file, bypass_trf = True)
    rd_count = util.count_reads(result)
    sample_report.extend(rd_count)

    # Compute number of trimmed reads
    sample_report[14] = (sample_report[2] - sample_report[6]) + (sample_report[2] - sample_report[14])
    sample_report[16] = (sample_report[2] - sample_report[8]) + (sample_report[2] - sample_report[16])
    report.append(sample_report)

    cols = ['SampleID', 'Raw_F', 'Raw_F.Count', 'Raw_R', 'Raw_R.Count', 
            'Cutadapt_F', 'Cutadapt_F.Count', 'Cutadapt_R', 'Cutadapt_R.Count', 
            'Repeat_F','Repeat_F.Count','Repeat_R','Repeat_R.Count',
            'Trim_F', 'Trim_F.Count','Trim_R','Trim_R.Count',
            'Human_Contam_F','Human_Contam_F.Count','Human_Contam_R','Human_Contam_R.Count',
            'Mouse_Contam_F','Mouse_Contam_F.Count','Mouse_Contam_R','Mouse_Contam_R.Count',
            'Kneaddata_F', 'Kneaddata_F.Count', 'Kneaddata_R', 'Kneaddata_R.Count']
    df = pd.DataFrame(report, columns=cols)

    outdir = os.path.join(process_dir, 'stats')
    util.create_dir(outdir)
    df.to_csv(os.path.join(outdir, sample + '.stat'), sep='\t', index=False)

    stats.qcheck_stats(process_dir)
    

def run_quality_control(process_dir):
    mapping_file = mapping.read_mapping(process_dir)
    config_file = config.read_config(process_dir)

    item = []
    for idx in mapping_file.index:
        sample = mapping_file.loc[idx, 'SampleID']
        fwd = mapping_file.loc[idx, 'Forward_read']
        rev = mapping_file.loc[idx, 'Reverse_read']
        item.append([sample, fwd, rev, process_dir, config_file])
    # Number of Parallel processing
    pool = mp.Pool(min(int(mp.cpu_count()/2), len(item)))

    result = pool.map(quality_control_parallel, item)
    print(result)
    # quality_control report
    stats.qcheck_stats(process_dir)
