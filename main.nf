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

    output:
        tuple path('remove_blankspace'), path('adapter_trimming'), path('decontamination'), path('stats'), path('quality_control')

    script:
    """
    python3 ${projectDir}/src/metaGP.py --qc -d ${projectDir} -p \$PWD
    """
}

process taxonomy_profiling {

    publishDir 'taxo', mode: 'copy'

    input:
        path qc

    output:
        path 'taxonomic_profile'

    script:
    """
    python3 ${projectDir}/src/metaGP.py --taxo -d ${projectDir} -p \$PWD
    """
}

process diversity_computation {

    publishDir 'div', mode: 'copy'

    input:
        path taxo

    output:
        path 'diversity'

    script:
    """
    python3 ${projectDir}/src/metaGP.py --div -d ${projectDir} -p \$PWD
    """
}

process functional_profiling {

    publishDir 'func', mode: 'copy'

    input:
        path qc

    output:
        path 'functional_profile'

    script:
    """
    python3 ${projectDir}/src/metaGP.py --func -d ${projectDir} -p \$PWD
    """
}

workflow {

    input_ch = Channel.of(params.i)

    make_mapping_file(input_ch)
    make_config_file(input_ch)
    preprocessing(make_mapping_file.out)
    quality_control(make_mapping_file.out, make_mapping_file.out)
    taxonomy_profiling(quality_control.out)
    diversity_computation(taxonomy_profiling.out)
    functional_profiling(quality_control.out)
}
