#!/user/bin/env python3

import pandas as pd
import os
import time

import util


def funcprof_stats(mapping_file, process_dir, output_dir):
    samples = pd.read_csv(mapping_file, sep='\t')['SampleID'].tolist()
    func_out_dir = os.path.join(output_dir, 'func')
    while not os.path.isdir(func_out_dir) or set(samples) != set(os.listdir(func_out_dir)):
        print('sleeping...')
        time.sleep(60)

    prof_files = []
    func_dir = os.path.join(process_dir, 'profiles')
    util.create_dir(func_dir)
    for root, dirs, files in os.walk(func_out_dir):
        for file in files:
            # check the extension of files
            if file.endswith('.tsv'):
                # print whole path of files
                filename = os.path.join(root, file)
                prof_files.append(os.path.join(func_dir, filename))
                os.system('cp ' + filename + ' ' + func_dir)

    # join genefamilies
    cmd = 'humann_join_tables --input ' + func_dir + ' --output ' + os.path.join(func_dir, 'genefamilies.tsv') + ' --file_name genefamilies'
    print(cmd)
    os.system(cmd)
    # normalize genefamilies
    cmd = 'humann_renorm_table --input ' + os.path.join(func_dir, 'genefamilies.tsv') + ' --units cpm --special n --output ' + os.path.join(func_dir, 'genefamilies_cpm.tsv')
    print(cmd)
    os.system(cmd)
    cmd = 'humann_renorm_table --input ' + os.path.join(func_dir, 'genefamilies.tsv') + ' --units relab --special n --output ' + os.path.join(func_dir, 'genefamilies_relab.tsv')
    print(cmd)
    os.system(cmd)
    # join pathabundance
    cmd = 'humann_join_tables --input ' + func_dir + ' --output ' + os.path.join(func_dir, 'pathabundance.tsv') + ' --file_name pathabundance'
    print(cmd)
    os.system(cmd)
    # normalize pathabundance
    cmd = 'humann_renorm_table --input ' + os.path.join(func_dir, 'pathabundance.tsv') + ' --units cpm --special n --output ' + os.path.join(func_dir, 'pathabundance_cpm.tsv')
    print(cmd)
    os.system(cmd)
    cmd = 'humann_renorm_table --input ' + os.path.join(func_dir, 'pathabundance.tsv') + ' --units relab --special n --output ' + os.path.join(func_dir, 'pathabundance_relab.tsv')
    print(cmd)
    os.system(cmd)
    # join pathcoverage
    cmd = 'humann_join_tables --input ' + func_dir + ' --output ' + os.path.join(func_dir, 'pathcoverage.tsv') + ' --file_name pathcoverage'
    print(cmd)
    os.system(cmd)
    # normalize pathabundance
    cmd = 'humann_renorm_table --input ' + os.path.join(func_dir, 'pathcoverage.tsv') + ' --units cpm --special n --output ' + os.path.join(func_dir, 'pathcoverage_cpm.tsv')
    print(cmd)
    os.system(cmd)
    cmd = 'humann_renorm_table --input ' + os.path.join(func_dir, 'pathcoverage.tsv') + ' --units relab --special n --output ' + os.path.join(func_dir, 'pathcoverage_relab.tsv')
    print(cmd)
    os.system(cmd)
    for f in prof_files:
        os.system('rm ' + f)
