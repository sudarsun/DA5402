#!/usr/bin/python3

import sys

print("Running the validation script")

if len(sys.argv) <= 3:
    print("requires <data_path> <true_mean> <true_sd>")
    sys.exit(0)

import numpy as np

true_mean = float(sys.argv[2])
true_sd = float(sys.argv[3])

samples = np.load(sys.argv[1])
mean = np.mean(samples)
sd = np.std(samples)

mean_error = (mean - true_mean)**2 
sd_error = (true_sd - sd) ** 2
print ("RMSE of the estimated mean (%f) is %f and the estimated SD (%f) is %f" % (mean, mean_error, sd, sd_error))
       
