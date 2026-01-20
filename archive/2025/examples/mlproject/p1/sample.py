#!/usr/bin/python3

import sys

print("Running the sampler script")

if len(sys.argv) <= 4:
    print("requires <count> <mean> <sd> <data_path>")
    sys.exit(0)

import numpy as np

print(sys.argv)

count = int(sys.argv[1])
sd = float(sys.argv[3])
mean = float(sys.argv[2])

print("generating %d random numbers" % count)
samples = np.random.randn(count)
adj_samples = samples * sd + mean

print("saving the output to: %s.npy" % sys.argv[4])
np.save(sys.argv[4], adj_samples)

