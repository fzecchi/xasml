#!/usr/bin/env bash
SWD=$(pwd); cd /data/scisoft/xasml/materials/mp-449/Fe/job15; sbatch job.sbatch; cd $SWD
SWD=$(pwd); cd /data/scisoft/xasml/materials/mp-19725/Fe/job15; sbatch job.sbatch; cd $SWD
