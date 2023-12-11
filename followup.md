# Is there noise down there? pt. 2
Now that Gianmarco went through all that mathematical fuss about entropy and random number generators, it’s time to bring his implementation on the board I have been given, a Google Coral Dev Board, which is an ARMv8 board.<br>
Requirements:
- gcc
- kernel headers
- bc
- 
## Reading the timestamp counter on ARMv8
There is no `RDTSC` function on ARMv8, and that, at first, startled me a bit, but luckily, as we can see here, there is an equivalent. 
The ARM implementation uses the Performance Monitoring Units (PMU) to retrieve the timer’s value, and it’s pretty straightforward:
```
    asm volatile ("msr cntv_ctl_el0, %0": "=r" (cpu_val));
```
We also need to compile the entropy assessment toolkit (located inside the `SP800-90B_EntropyAssessment` folder) for ARMv8. Doing so requires adding the modifying the Makefile in the following way:
```
ARCH ?= arm64
THIS_DIR := $(dir $(abspath $(firstword $(MAKEFILE_LIST))))

CXX ?= $(CROSS_COMPILE)g++

CXXFLAGS = -std=c++11 -fopenmp -O2 -ffloat-store -I/usr/include/jsoncpp -g
ifeq ($(ARCH),x86)
CXXFLAGS += -msse2 -march=native
endif

ifeq ($(ARCH),arm64)
CXXFLAGS += -march=native
endif
... 
```