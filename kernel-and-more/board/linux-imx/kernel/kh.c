#include <linux/kh.h>
#include <linux/types.h>
#include <linux/module.h>

#include <asm/atomic.h>

atomic64_t LAST_TIMESTAMP = ATOMIC_INIT(-1);
atomic64_t LAST_DELTA = ATOMIC_INIT(-1);
atomic64_t SEED = ATOMIC_INIT(0);
atomic_t GLOBAL_TIMES = ATOMIC_INIT(0);
atomic_t SEEDS_INDEX = ATOMIC_INIT(0);
unsigned long long int timer_seeds[20] = { -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 }; 

inline unsigned long long int get_tsc(void){
	unsigned long long int cpu_val = 0;
	asm volatile ("mrs %0, cntvct_el0": "=r" (cpu_val));
	return cpu_val;
}


EXPORT_SYMBOL(LAST_TIMESTAMP);
EXPORT_SYMBOL(LAST_DELTA);
EXPORT_SYMBOL(SEED);
EXPORT_SYMBOL(GLOBAL_TIMES);
EXPORT_SYMBOL(SEEDS_INDEX);
EXPORT_SYMBOL(timer_seeds);
EXPORT_SYMBOL(get_tsc);
