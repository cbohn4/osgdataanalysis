import pandas as pd
import numpy as np
import sys


#  sacct -P -a -S 2022-08-20 -E 2022-08-27 -o JobID,Cluster,User,Group,ReqCPUS,ReqNodes,ReqMem,ReqTRES,TimeLimitRaw > ~/test.sacct

def gpu_count(req_tres):
    gpu_req = []
    for tres in req_tres:
        if "gpu" not in tres:
            gpu_req.append(0)
        else:
            gpu_req.append(int(tres.split("gres/gpu=")[1].split(",")[0]))
    return gpu_req

def mem_parse(cores,nodes,mem):
    suffixes = ["K","M","G","T","P"]
    if "c" == mem[-1]:
        return float(mem[:-2]) * cores * 1024**(suffixes.index(mem[-2])-2)
    if "n" == mem[-1]:
        return float(mem[:-2]) * nodes * 1024**(suffixes.index(mem[-2])-2)

input_file = sys.argv[1]

df = pd.read_csv(input_file,delimiter="|")
# Get rid of slurm steps. 
df = df.dropna()
# Clean up in the event of duplicate jobs from combining multiple sacct runs
df = df.drop_duplicates(subset=["JobID", "Cluster"], keep="first")
# Get GPU Requests
df = df.assign(ReqGPU=gpu_count(df["ReqTRES"]))
user_list = np.unique(list(df["User"]))
group_list = np.unique(list(df["Group"]))

total_statistics = {"osg":0,"path":0,"total":len(df)}

user_job_count = {}
for user in user_list: 
    user_job_count[user] = {"osg":0, "path":0, "total":len(df[df['User'] == user])}

group_job_count = {}
for group in group_list: 
    group_job_count[group] = {"osg":0, "path":0, "total":len(df[df['Group'] == group])}


# Current Eligibility: <= 64 Cores, <= 1 GPU, 1 Node, <=200GB Memory <= 40 hours, <= 1 GPU

for r, job in df.iterrows():
    mem_req = mem_parse(job["ReqCPUS"],job["ReqNodes"],job["ReqMem"])
    if job["ReqNodes"] == 1 and job["TimelimitRaw"] <= 40 * 3600: # Basic filter

        if job["ReqGPU"] == 0 and job["ReqCPUS"] <= 8 and mem_req <= 8 and job["TimelimitRaw"] <= 24 * 3600: # OSG Requirements
            user_job_count[job["User"]]["osg"] += 1
            group_job_count[job["Group"]]["osg"] += 1
            total_statistics["osg"] += 1

        if job["ReqGPU"] <= 1 and job["ReqCPUS"] <= 64 and mem_req <= 200: # PATh Requirements
            user_job_count[job["User"]]["path"] += 1
            group_job_count[job["Group"]]["path"] += 1
            total_statistics["path"] += 1
    if job["User"] == "osg":
        print("NOW",user_job_count["osg"])



