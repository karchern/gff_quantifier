Bootstrap: docker
From: ubuntu:20.04
IncludeCmd: yes

%labels
  MAINTAINER cschu (cschu1981@gmail.com)
  VERSION v.1.2.3

%environment
#R_VERSION=4.1
#export R_VERSION
#R_CONFIG_DIR=/etc/R/
#export R_CONFIG_DIR
export LC_ALL=C
export PATH=$PATH:/opt/software/miniconda3/bin:/opt/software/mOTUs

%post
  apt-get update
  apt-get install -y apt-transport-https apt-utils software-properties-common
  apt-get install -y add-apt-key
  export DEBIAN_FRONTEND=noninteractive
  ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
  apt-get install -y tzdata
  dpkg-reconfigure --frontend noninteractive tzdata

  apt-get install -y wget python3-pip git

  mkdir -p /opt/software

  # all the conda packages won't work together.. ><;
  wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh 
  bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/software/miniconda3
  rm -f Miniconda3-latest-Linux-x86_64.sh

  # /opt/software/miniconda3/bin/conda install -y -c conda-forge -c bioconda 'samtools>=1.13' bwa kraken2 fastqc multiqc bbmap seqtk
  wget https://github.com/cschu/gff_quantifier/archive/refs/tags/v.1.2.3.tar.gz
  tar xvzf v.1.2.3.tar.gz 
  cd gff_quantifier-v.1.2.3
  python setup.py bdist_wheel
  pip install --force-reinstall dist/*whl
  cd ..
  rm -rf gff_quantifier-v.1.2.3 v.1.2.3.tar.gz



