#!/usr/bin/env nextflow

def input_dir = "${params.i}"
def output_dir = "${params.o}"

process make_mapping_file {

    publishDir "${output_dir}/mapping", mode: 'copy'
    
    output:
        file("mapping.tab") 

    script:
    """
    python3 ${projectDir}/src/metaGP.py --mapping -p \$PWD -i ${input_dir}
    """
}

process make_config_file {

    publishDir "${output_dir}/config", mode: 'copy'

    output:
        file("config.info")

    script:
    """
    python3 ${projectDir}/src/metaGP.py --config -d ${projectDir} -i ${input_dir} > config.info
    """
}

process preprocessing {

    tag "${SampleID}"

    publishDir "${output_dir}/pre/${SampleID}", mode: 'copy'

    input:
        tuple val(Num), val(SampleID), path(Forward_read), path(Reverse_read)

    output:
        tuple path('stats'), path('fastqc'), path('quality_control')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --pre -p \$PWD -s ${SampleID} -f ${Forward_read} -r ${Reverse_read}
    """
}

process quality_control {

    tag "${SampleID}"

    publishDir "${output_dir}/qc/${SampleID}", mode: 'copy'

    input:
        path config
        tuple val(Num), val(SampleID), path(Forward_read), path(Reverse_read)

    output:
        tuple file('samples_to_process.tab'), path('remove_blankspace'), path('adapter_trimming'), path('decontamination'), path('stats'), path('quality_control')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --qc -p \$PWD  -s ${SampleID} -f ${Forward_read} -r ${Reverse_read}
    """
}

process taxonomy_profiling {

    tag "${SampleID}"

    publishDir "${output_dir}/taxo/${SampleID}", mode: 'copy'

    input:
        path config
        tuple val(Num), val(SampleID), path(Forward_read), path(Reverse_read)

    output:
        path 'taxonomic_profile'

    script:
    """
    python3 ${projectDir}/src/metaGP.py --taxo -p \$PWD -s ${SampleID} -f ${Forward_read} -r ${Reverse_read}
    """
}

process diversity_computation {

    tag "${SampleID}"

    publishDir "${output_dir}/div/${SampleID}", mode: 'copy'

    input:
        path config
        path taxo
        tuple val(Num), val(SampleID), path(Forward_read), path(Reverse_read)

    output:
        path 'diversity'

    script:
    """
    python3 ${projectDir}/src/metaGP.py --div -p \$PWD -s ${SampleID} -f ${Forward_read} -r ${Reverse_read}
    """
}

process functional_profiling {

    tag "${SampleID}"

    publishDir "${output_dir}/func/${SampleID}", mode: 'copy'

    input:
        path config
        tuple val(Num), val(SampleID), path(Forward_read), path(Reverse_read)

    output:
        path 'functional_profile'

    script:
    """
    python3 ${projectDir}/src/metaGP.py --func -p \$PWD -s ${SampleID} -f ${Forward_read} -r ${Reverse_read}
    """
}

workflow {

    make_mapping_file()
    make_config_file()
    preprocessing(make_mapping_file.out
                    .splitCsv(header: ['Num', 'SampleID', 'Forward_read', 'Reverse_read'], sep: '\t', skip: 1)
                    .map{ row -> tuple(row.Num, row.SampleID, row.Forward_read, row.Reverse_read)})
    quality_control(make_config_file.out,
                    make_mapping_file.out
                        .splitCsv(header: ['Num', 'SampleID', 'Forward_read', 'Reverse_read'], sep: '\t', skip: 1)
                        .map{ row -> tuple(row.Num, row.SampleID, row.Forward_read, row.Reverse_read)})
    taxonomy_profiling(make_config_file.out,
                       quality_control.out[0]
                        .splitCsv(header: ['Num', 'SampleID', 'Forward_read', 'Reverse_read'], sep: '\t', skip: 1)
                        .map{ row -> tuple(row.Num, row.SampleID, row.Forward_read, row.Reverse_read)})
                        /*
    diversity_computation(make_config_file.out,
                          taxonomy_profiling.out,
                          quality_control.out[0]
                            .splitCsv(header: ['Num', 'SampleID', 'Forward_read', 'Reverse_read'], sep: '\t', skip: 1)
                            .map{ row -> tuple(row.Num, row.SampleID, row.Forward_read, row.Reverse_read)})
                            */
    functional_profiling(make_config_file.out,
                         quality_control.out[0]
                            .splitCsv(header: ['Num', 'SampleID', 'Forward_read', 'Reverse_read'], sep: '\t', skip: 1)
                            .map{ row -> tuple(row.Num, row.SampleID, row.Forward_read, row.Reverse_read)})
}
