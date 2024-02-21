#include <linux/types.h>
#include <linux/flex_array.h>

#ifndef KH_H
#define KH_H

extern atomic64_t LAST_TIMESTAMP;
extern atomic64_t LAST_DELTA;
extern atomic64_t SEED;
extern atomic_t GLOBAL_TIMES;
extern atomic_t SEEDS_INDEX;
extern unsigned long long int timer_seeds[20]; // 80 is the maximum (heuristically) number of times the 'try_timer_kh' gets called during kernel initialization, so we can generate 10 seeds
    // i put 20 seeds just to be safe lol
extern unsigned long long int get_tsc(void);

#endif
