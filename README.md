# OSGDataAnalysis
Python script for finding OSG/PATh Eligible Jobs using sacct results.

## Defitionions: 
There are two catergories of jobs being looked at, jobs that would be good candidates for the Open Science Grid (OSG), and the Partnership to Advanced Throughput Computing (PATh).

Both categories would be requeired to be single node jobs and a limit of 1 GPU. 
OSG eligible jobs would need to meet the job resource requirements below:
* <= 8 CPU Cores
* <= 8GB of Memory
* <= 24 hours of runtime

PATh expands on these requirements:
* <= 64 CPU Cores
* <= 200GB of Memory
* <= 40 hours of runtime

## Data Generation:

### sacct
The primary method for generating data is using Slurm's `sacct` utility. The example command below would pull the required data for a week of jobs on the current cluster. Additional data can be appended to the output file, but would need the `-n` flag added to the sacct command to remove the header from the output. 
`sacct -P -a -S 2022-08-20 -E 2022-08-27 -o JobID,Cluster,User,Group,ReqCPUS,ReqNodes,ReqMem,ReqTRES,TimeLimitRaw > ~/sacct.csv`
Adding more data:
`sacct -n -P -a -S 2022-08-13 -E 2022-08-20 -o JobID,Cluster,User,Group,ReqCPUS,ReqNodes,ReqMem,ReqTRES,TimeLimitRaw >> ~/sacct.csv`

**IMPORTANT NOTE:** Do not `sacct` run more than a few weeks at a time depending on the size of the cluster and resources available to the slurmdb database. Pulling too much data from `sacct` can cause the slurm process to crash and prevent slurm from processing jobs cluster wide. 

### XDMoD
If you have an XDMoD instance, version 9.0 or greater, larger data requests are better served by the XDMoD `mod_hpcdb` database. By default, this will include all HPC resources within XDMoD. 
`SELECT local_job_id_raw,resource_id,username,groupname,cpu_req,nodecount,mem_req,gpucount,timelimit FROM hpcdb_jobs WHERE submit_time >= 1660953600 AND submit_time <= 1661558400 INTO OUTFILE '/tmp/xdmod.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';`



## In the output files, there are four columns:
username/groupname: Group or username
osg: Number of OSG eligible jobs for the group/user.
path: Number of PATh eligible jobs for the group/user.
total: Number of jobs analyzed for the group/user. 
