# OSGDataAnalysis
Notebook for finding OSG Eligible Jobs using sacct results.

## Defitionions: 
There are two catergories of jobs being looked at, OSG Ideal Jobs and OSG Limit Jobs. 

OSG Ideal jobs are ones that would be ideal canidiates to run on the open science grid due to their small resource and times requests.
Similarly, OSG Limit jobs are ones that would still work well on the Open Science Grid, but would be harder to finish or find available resources.

Both types of jobs are single node and single core, the differences are how long the job runs for, and how much memory is requested. 

OSG Ideal has 4GB of memory requested or less and 10 hours in length or less, while OSG Limit is 4-10GB of memory requested and a day or less in runtime.



## In the output file, there are six columns:
user: Username of the user

osgIdeal: Number of jobs meeting the OSG Ideal Requirements

osgLimit: Number of jobs meeting the OSG Limit Requirements

total: Total Number of jobs ran by the user. 

percIdeal: Decimal percentage of jobs meeting the OSG Ideal Requirements

percLimit: Decimal percentage of jobs meeting the OSG Limit Requirements
