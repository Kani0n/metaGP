#!/bin/bash

# default values:
nCORES="4"
nPARALLEL="1"

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -i|--input)
      INPUT="$2"
      shift # past argument
      shift # past value
      ;;
    -o|--output)
      OUTPUT="$2"
      shift # past argument
      shift # past value
      ;;
    -n|--nCores)
      nCORES="$2"
      shift # past argument
      shift # past value
      ;;
    -p|--nParallel)
      nPARALLEL="$2"
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
echo "OUTPUT DIR: ${OUTPUT}"
echo "NUMBER OF CORES: ${nCORES}"
echo "NUMBER OF PARALLEL PROCESSES: ${nPARALLEL}"
#echo "Building Docker..."
#docker build -t metagp .
#docker run --name metagp -d -i -t -v ${INPUT}:/data metagp
#docker exec -d metagp nextflow run main.nf

echo "SETTING UP ENVIRONMENT..."
source /mnt/main_hdd/miniconda3/bin/activate
if ! { conda env list | grep 'metaGP'; } >/dev/null 2>&1; then
  echo "Building Conda Environment..."
  conda env create -f conda.yml
fi
conda activate metaGP

echo "STARTING..."
nextflow run main.nf --i ${INPUT} --o ${OUTPUT} --n ${nCORES} --np ${nPARALLEL}
