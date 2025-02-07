FROM continuumio/miniconda3:main

RUN apt-get update \
    && apt-get install -y procps \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY conda.yml .
COPY src/ src/

RUN conda env create -f /conda.yml \
    && conda clean -a

ENV PATH /opt/conda/envs/metaGP/bin:$PATH

#COPY install_packages.R /
#COPY bed_convert.R /
#COPY cut_tag_fingerprint_cmd.R /
#
#RUN Rscript install_packages.R
#CMD ["Rscript", "bed_convert.R"]
#CMD ["Rscript", "cut_tag_fingerprint_cmd.R"]
