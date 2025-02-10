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
    python3 ${projectDir}/src/metaGP.py --mapping -d \$PWD -i ${input_dir} > mapping.tab
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
    python3 ${projectDir}/src/metaGP.py --config -d \$PWD -i ${input_dir} > config.info
    """
}

process preprocessing {

    publishDir 'out', mode: 'copy'

    input:
        val input_dir

    output:
        

    script:
    """
    
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
    
}
