#include <linux/types.h>

#ifndef KH_H
#define KH_H

extern atomic64_t LAST_TIMESTAMP;
extern atomic64_t LAST_DELTA;
extern atomic64_t SEED;
extern atomic_t GLOBAL_TIMES;
extern unsigned long long int get_tsc(void);

#endif