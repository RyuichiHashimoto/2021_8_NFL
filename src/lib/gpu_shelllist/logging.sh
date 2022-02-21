#!/bin/bash

nvidia-smi   --query-gpu=timestamp,name,utilization.gpu,utilization.memory,memory.used,memory.free   --format=csv -l 1  > /work/log/gpu.log &