#!/bin/bash

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -i|--input)
      INPUT="$2"
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

echo "INPUT DIR: ${INPUT}"
#echo "Building Docker..."
#docker build -t metagp .
#docker run --name metagp -d -i -t -v ${INPUT}:/data metagp
#docker exec -d metagp nextflow run main.nf

source /mnt/DATA/miniconda3/bin/activate
if ! { conda env list | grep 'metaGP'; } >/dev/null 2>&1; then
  echo "Building Conda Environment..."
  conda env create -f conda.yml
fi
conda activate metaGP

echo "Starting..."
nextflow run main.nf --i ${INPUT}
