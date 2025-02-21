#!/usr/bin/env nextflow

process make_mapping_file {

    conda "/mnt/DATA/miniconda3/envs/metaGP"

    publishDir 'mapping', mode: 'copy'

    input:
        val input_dir
    
    output:
        path "mapping.tab"

    script:
    """
    python3 ${projectDir}/src/metaGP.py --mapping -p \$PWD -i ${input_dir}
    """
}

process make_config_file {

    conda "/mnt/DATA/miniconda3/envs/metaGP"

    publishDir 'config', mode: 'copy'

    input:
        val input_dir
    
    output:
        path "config.info"

    script:
    """
    python3 ${projectDir}/src/metaGP.py --config -d ${projectDir} -i ${input_dir} > config.info
    """
}

process preprocessing {

    publishDir 'pre', mode: 'copy'

    input:
        path mapping

    output:
        tuple path('stats'), path('fastqc')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --pre -d ${projectDir} -p \$PWD
    """
}

process quality_control {

    publishDir 'qc', mode: 'copy'

    input:
        path mapping
        path config
        path preprocessing

    output:
        tuple path('remove_blankspace'), path('adapter_trimming'), path('decontamination'), path('stats')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --qc -d ${projectDir} -p \$PWD
    """
}

process taxonomy_profiling {

    publishDir 'tax', mode: 'copy'

    input:
        path quality_control

    output:
        

    script:
    """
    python3 ${projectDir}/src/metaGP.py --taxo -d ${projectDir} -p \$PWD
    """
}

process diversity_computation {

    publishDir 'out', mode: 'copy'

    input:
        

    output:
        

    script:
    """
    
    """
}

process functional_profiling {

    publishDir 'out', mode: 'copy'

    input:
        

    output:
        

    script:
    """
    
    """
}

workflow {

    input_ch = Channel.of(params.i)

    make_mapping_file(input_ch)
    make_config_file(input_ch)
    preprocessing(make_mapping_file.out)
    quality_control(make_mapping_file.out, make_config_file.out, preprocessing.out)
}
