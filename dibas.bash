#!/bin/bash

export DIBAS_DIR=/home/onr_python/digital_backend/
export HASHPIPE_DIR=/opt/local/hash
export HASH_DIR=$HASHPIPE_DIR
#export HASH_DIR=/usr/local

#export DIBAS_MAIN_DIR=/home/dibas
#export DIBAS_MAIN_DIR=/home/flag
# source $DIBAS_MAIN_DIR/dibas-ve/bin/activate

# Set environment variables for DIBAS, bash version
#echo "Setting DIBAS environment.."

# This is not installed at SHAO
#export HEADAS=$DIBAS_DIR/pulsar/src/heasoft-6.6.2/x86_64-unknown-linux-gnu-libc2.3.4
#alias ftools=". $HEADAS/headas-init.sh"

#PSR64=$DIBAS_DIR/pulsar
#DIBASLIBS=$DIBAS_DIR/dibaslibs
#OPT64=$DIBASLIBS
#export CUDA=/opt/local/cuda75
#export CUDA=/usr/local/cuda
export CUDA=/opt/local/NVIDIA/cuda-10.0

#export DIBAS_DATA=/export/home/tank/scratch
#export DIBAS_DATA=/lustre/gbtdata
#export DIBAS_DATA=/lustre/gbtdata/TGBT16A_508_01/SIM
#export DIBAS_DATA=/lustre/projects/flag
#export DIBAS_DATA=/lustre/flag
export DIBAS_DATA=/opt/local/output_data
#export OVERLORD_DIR=$DIBAS_DIR/lib/python/scanOverlord

# may be needed by various programs & scripts:
export VEGAS=$DIBAS_DIR
export GUPPI_DIR=$DIBAS_DIR/etc/config
export VEGAS_DIR=$DIBAS_DIR/etc/config
export CONFIG_DIR=$DIBAS_DIR/etc/config

#export PRESTO=$PSR64/src/presto
#export GBT1PREFIX=$DIBASLIBS
#export QWTLIB=$GBT1PREFIX/qwt-6.0.1/lib
#export PATH=$HASHPIPE_DIR/bin:$PSR64/bin:$PRESTO/bin:$DIBAS_DIR/bin:$DIBAS_DIR/bin/x86_64-linux:$OPT64/bin:$DIBAS_DIR/lib/python:$PATH
#export PATH=$HASHPIPE_DIR/bin:$PSR64/bin:$PRESTO/bin:$DIBAS_DIR/bin:$DIBAS_DIR/bin/x86_64-linux:$OPT64/bin:$DIBAS_MAIN_DIR/dibas-ve/lib/python2.7/site-packages:$DIBAS_DIR/lib/python:$PATH
export PATH=$HASHPIPE_DIR/bin:$DIBAS_DIR/bin:$DIBAS_DIR/bin/x86_64-linux:/usr/lib/python/dist-packages:$DIBAS_DIR/lib/python:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/mruzinda/.local/bin:/home/mruzinda/bin:/opt/local/bin:$PATH

#export DIBASPYTHON=$DIBASLIBS/lib/python2.6/site-packages:$DIBASLIBS/lib64/python2.6/site-packages

# export PYTHONPATH=$PSR64/lib/python:$PRESTO/lib/python:$DIBAS_DIR/lib/python
# export PYTHONPATH=$PSR64/lib/python:$PSR64/lib/python2.6/site-packages:$PRESTO/lib/python
#export PYTHONPATH=$PSR64/lib/python:$PSR64/lib/python2.6/site-packages:$PRESTO/lib/python:$DIBASPYTHON:$OVERLORD_DIR/site-packages:$PYTHONPATH
# export PYTHONPATH=$DIBAS_MAIN_DIR/dibas-ve/lib/python2.7/site-packages:$DIBAS_DIR/lib/python:$PSR64/lib/python:$PSR64/lib/python2.6/site-packages:$PRESTO/lib/python:$DIBASPYTHON:$PYTHONPATH
#export PYTHONPATH=$DIBAS_MAIN_DIR/dibas-ve/lib/python2.7/site-packages:$DIBAS_DIR/lib/python:$PSR64/lib/python:$PRESTO/lib/python:$DIBASPYTHON:$PYTHONPATH:/usr/lib/python2.6/site-packages:$OVERLORD_DIR/site-packages
#export PYTHONPATH=$DIBAS_MAIN_DIR/flag-ve/lib/python2.7/site-packages:$DIBAS_DIR/lib/python:$PSR64/lib/python:$PRESTO/lib/python:$DIBASPYTHON:$PYTHONPATH:/usr/lib/python2.6/site-packages:$OVERLORD_DIR/site-packages
#export PYTHONPATH=$DIBAS_MAIN_DIR/flag-ve/lib/python2.7/site-packages:$DIBAS_DIR/lib/python:$DIBASPYTHON:$PYTHONPATH:/usr/lib/python2.6/site-packages:$OVERLORD_DIR/site-packages
export PYTHONPATH=/usr/lib/python2.7/dist-packages

#export PGPLOT_DIR=$PSR64/pgplot
#export LD_LIBRARY_PATH=$PSR64/lib:$OPT64/lib:$PGPLOT_DIR:$PRESTO/lib:$GBT1PREFIX/lib:$QWTLIB:$CUDA/lib64:$HASH_DIR/lib
#export LD_LIBRARY_PATH=$OPT64/lib:$GBT1PREFIX/lib:$QWTLIB:$CUDA/lib64:$HASH_DIR/lib
export LD_LIBRARY_PATH=$CUDA/lib64:$CUDA/lib:$HASH_DIR/lib

#export TEMPO=$PSR64/src/tempo
#export TEMPO2=$PSR64/share/tempo2
