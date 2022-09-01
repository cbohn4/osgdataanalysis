import pandas as pd
import numpy as np
import sys
from optparse import OptionParser


parser = OptionParser()
parser.add_option("-i","--input", action="store", dest="input_file",
        help="(required) Input file containing sacct or XDMoD data.")
parser.add_option("-x","--xdmod", action="store_true", dest="xdmod",
        help="Use XDMoD data instead of sacct data.")
parser.add_option("-u","--userout", action="store", dest="userout",
        help="(required) Output file for user data")
parser.add_option("-g","--groupout", action="store", dest="groupout",
        help="(required) Output file for group data")
parser.usage = "%prog [options] LOGIN"
(options, args) = parser.parse_args()

# Convert sacct ReqTRES to GPU Count
def gpu_count(req_tres):
    gpu_req = []
    for tres in req_tres:
        if "gpu" not in tres:
            gpu_req.append(0)
        else:
            gpu_req.append(int(tres.split("gres/gpu=")[1].split(",")[0]))
    return gpu_req

# Convert slurm memory format to total memory requested
def mem_parse(cores,nodes,mem):
    suffixes = ["K","M","G","T","P"]
    if "c" == mem[-1]:
        return float(mem[:-2]) * cores * 1024**(suffixes.index(mem[-2])-2)
    if "n" == mem[-1]:
        return float(mem[:-2]) * nodes * 1024**(suffixes.index(mem[-2])-2)

if options.xdmod:
    df = pd.read_csv(options.input_file,delimiter=",",names=["JobID","Cluster","User","Group","ReqCPUS","ReqNodes","ReqMem","ReqGPU","TimelimitRaw"])
else:
    df = pd.read_csv(options.input_file,delimiter="|")
    
# Get rid of slurm steps and missing data. 
df = df.dropna()

# Clean up in the event of duplicate jobs from combining multiple sacct runs
df = df.drop_duplicates(subset=["JobID", "Cluster"], keep="first")

# Get GPU Requests if using sacct
if not options.xdmod:
    df = df.assign(ReqGPU=gpu_count(df["ReqTRES"]))

# Setup data structure
user_list = np.unique(list(df["User"]))
group_list = np.unique(list(df["Group"]))
total_statistics = {"osg":0,"path":0,"total":len(df)}

user_job_count = {}
for user in user_list: 
    user_job_count[user] = {"osg":0, "path":0, "total":len(df[df['User'] == user])}

group_job_count = {}
for group in group_list: 
    group_job_count[group] = {"osg":0, "path":0, "total":len(df[df['Group'] == group])}


# Get data organized and processed
for r, job in df.iterrows():
    mem_req = mem_parse(job["ReqCPUS"],job["ReqNodes"],job["ReqMem"])
    if job["ReqNodes"] == 1 and job["TimelimitRaw"] <= 40 * 3600: # Basic filter

        if job["ReqCPUS"] <= 8 and mem_req <= 8 and job["TimelimitRaw"] <= 24 * 3600: # OSG Requirements
            user_job_count[job["User"]]["osg"] += 1
            group_job_count[job["Group"]]["osg"] += 1
            total_statistics["osg"] += 1

        if job["ReqGPU"] <= 1 and job["ReqCPUS"] <= 64 and mem_req <= 200: # PATh Requirements
            user_job_count[job["User"]]["path"] += 1
            group_job_count[job["Group"]]["path"] += 1
            total_statistics["path"] += 1

# Organize for CSV output
user_output = {"username":[],"osg":[],"path":[],"total":[]}
group_output = {"groupname":[],"osg":[],"path":[],"total":[]}

for user in user_job_count.keys():
    user_output["username"].append(user)
    user_output["osg"].append(user_job_count[user]["osg"])
    user_output["path"].append(user_job_count[user]["path"])
    user_output["total"].append(user_job_count[user]["total"])

for group in group_job_count.keys():
    group_output["groupname"].append(group)
    group_output["osg"].append(group_job_count[group]["osg"])
    group_output["path"].append(group_job_count[group]["path"])
    group_output["total"].append(group_job_count[group]["total"])

user_output_file = options.userout if options.userout is not None else ".".join(options.input_file.split(".")[:-1]) + "_users.csv"
group_output_file = options.groupout if options.groupout is not None else ".".join(options.input_file.split(".")[:-1])+ "_groups.csv"

pd.DataFrame(user_output).to_csv(user_output_file, index=False)
pd.DataFrame(group_output).to_csv(group_output_file, index=False)

print(f"User output file can be found at: {user_output_file}")
print(f"Group output file can be found at: {group_output_file}")

print(f"{np.round((total_statistics['osg']*100)/(total_statistics['total']),2)} % of {(total_statistics['total'])} jobs were eligible for the OSG.")
print(f"{np.round((total_statistics['path']*100)/(total_statistics['total']),2)} % of {(total_statistics['total'])} jobs were eligible for PATh.")



