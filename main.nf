#!/usr/bin/env nextflow


params.n = 4
params.np = 8
def nCores = "${params.n}"
def nParallel = "${params.np}"
def input_dir = "${params.i}"
def output_dir = "${params.o}"


process make_config_file {

    publishDir "${output_dir}/config", mode: 'copy'

    output:
        file('config.info')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --config -d ${projectDir} -i ${input_dir} > config.info
    """
}

process make_mapping_file {

    publishDir "${output_dir}/mapping", mode: 'copy'
    
    output:
        file('mapping.tab') 

    script:
    """
    python3 ${projectDir}/src/metaGP.py --mapping -p \$PWD -i ${input_dir}
    """
}

process preprocessing {

    tag "${SampleID}"

    publishDir "${output_dir}/pre/${SampleID}", mode: 'copy'

    input:
        tuple val(Num), val(SampleID), path(Forward_read), path(Reverse_read)

    output:
        path('stats')
        path('fastqc')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --pre -p \$PWD -s ${SampleID} -f ${Forward_read} -r ${Reverse_read}
    """
}

process preprocessing_stats {

    publishDir "${output_dir}/pre_stats", mode: 'copy'

    input:
        file(mapping)

    output:
        file('raw_readcount.tab')
        file('raw_readcount.png')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --pres -p \$PWD -m ${mapping} -o ${output_dir}
    """
}

process quality_control {

    tag "${SampleID}"

    publishDir "${output_dir}/qc/${SampleID}", mode: 'copy'

    input:
        file(config)
        tuple val(Num), val(SampleID), path(Forward_read), path(Reverse_read)

    output:
        path('remove_blankspace')
        path('adapter_trimming')
        path('decontamination')
        path('stats')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --qc -p \$PWD  -s ${SampleID} -f ${Forward_read} -r ${Reverse_read}
    """
}

process quality_control_stats {

    publishDir "${output_dir}/qc_stats", mode: 'copy'

    input:
        file(config)
        file(mapping)

    output:
        file('readcounts.tab')
        file('samples_to_process.tab')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --qcs -p \$PWD -m ${mapping} -o ${output_dir}
    """
}

process taxonomy_profiling {

    tag "${SampleID}"

    publishDir "${output_dir}/taxo/${SampleID}", mode: 'copy'

    input:
        file(config)
        tuple val(Num), val(SampleID), path(Forward_read), path(Reverse_read)

    output:
        path('ignore_usgb')
        path('usgb')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --taxo -p \$PWD -s ${SampleID} -f ${Forward_read} -r ${Reverse_read} -n ${nCores}
    """
}

process taxonomy_profiling_stats {

    publishDir "${output_dir}/taxo_stats", mode: 'copy'

    input:
        file(config)
        file(mapping)

    output:
        path('ignore_usgb')
        path('usgb')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --taxos -p \$PWD -m ${mapping} -o ${output_dir}
    """
}

process diversity_computation {

    publishDir "${output_dir}/div", mode: 'copy'

    input:
        file(config)
        path('ignore_usgb')
        path('usgb')

    output:
        path('diversity')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --div -p \$PWD -o ${output_dir}
    """
}

/*
process functional_profiling {

    tag "${SampleID}"

    publishDir "${output_dir}/func/${SampleID}", mode: 'copy'

    input:
        file(config)
        path('ignore_usgb')
        path('usgb')
        tuple val(Num), val(SampleID), path(Forward_read), path(Reverse_read)

    output:
        path('functional_profile')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --func -p \$PWD -s ${SampleID} -f ${Forward_read} -r ${Reverse_read} -n ${nCores}
    """
}
*/

process functional_profiling {

    publishDir "${output_dir}/func", mode: 'copy'

    input:
        file(config)
        path('ignore_usgb')
        path('usgb')
        file(mapping)

    output:
        path('functional_profile')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --func -p \$PWD -m ${mapping} -n ${nCores} -np ${nParallel}
    """
}

process functional_profiling_stats {

    publishDir "${output_dir}/func_stats", mode: 'copy'

    input:
        path('ignore_usgb')
        path('usgb')
        file(mapping)

    output:
        path('profiles')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --funcs -p \$PWD -m ${mapping} -o ${output_dir}
    """
}

workflow {
    
    make_config_file()
    make_mapping_file()
    /*
    preprocessing(make_mapping_file.out
                    .splitCsv(header: ['Num', 'SampleID', 'Forward_read', 'Reverse_read'], sep: '\t', skip: 1)
                    .map{ row -> tuple(row.Num, row.SampleID, row.Forward_read, row.Reverse_read)})
    preprocessing_stats(make_mapping_file.out)
    quality_control(make_config_file.out,
                    make_mapping_file.out
                        .splitCsv(header: ['Num', 'SampleID', 'Forward_read', 'Reverse_read'], sep: '\t', skip: 1)
                        .map{ row -> tuple(row.Num, row.SampleID, row.Forward_read, row.Reverse_read)})
    */
    quality_control_stats(make_config_file.out, make_mapping_file.out)
    /*
    taxonomy_profiling(make_config_file.out,
                       quality_control_stats.out[1]
                        .splitCsv(header: ['Num', 'SampleID', 'Forward_read', 'Reverse_read'], sep: '\t', skip: 1)
                        .map{ row -> tuple(row.Num, row.SampleID, row.Forward_read, row.Reverse_read)})
    */
    taxonomy_profiling_stats(make_config_file.out,
                             quality_control_stats.out[1])
    diversity_computation(make_config_file.out,
                          taxonomy_profiling_stats.out)
    /*
    functional_profiling(make_config_file.out,
                         taxonomy_profiling_stats.out,
                         quality_control_stats.out[1])
    /*
    functional_profiling(make_config_file.out,
                         taxonomy_profiling_stats.out,
                         quality_control_stats.out[1]
                            .splitCsv(header: ['Num', 'SampleID', 'Forward_read', 'Reverse_read'], sep: '\t', skip: 1)
                            .map{ row -> tuple(row.Num, row.SampleID, row.Forward_read, row.Reverse_read)})
    functional_profiling_stats(taxonomy_profiling_stats.out,
                               quality_control_stats.out[1])
    */
}
