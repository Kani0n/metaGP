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
    python3 ${projectDir}/src/metaGP.py --config -i ${input_dir} > config.info
    """
}

process preprocessing {

    publishDir 'pre', mode: 'copy'

    input:
        path mapping

    output:
        path "pre.txt"

    script:
    """
    python3 ${projectDir}/src/metaGP.py --pre -d ${projectDir} -p \$PWD > pre.txt
    """
}

process quality_control {

    publishDir 'out', mode: 'copy'

    input:
        

    output:
        

    script:
    """
    
    """
}

process taxonomy_profiling {

    publishDir 'out', mode: 'copy'

    input:
        

    output:
        

    script:
    """
    
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
}
