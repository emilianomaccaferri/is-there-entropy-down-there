/*
 * arch/arm64/include/asm/arch_timer.h
 *
 * Copyright (C) 2012 ARM Ltd.
 * Author: Marc Zyngier <marc.zyngier@arm.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#ifndef __ASM_ARCH_TIMER_H
#define __ASM_ARCH_TIMER_H

#include <asm/barrier.h>
#include <asm/sysreg.h>

#include <linux/bug.h>
#include <linux/init.h>
#include <linux/jump_label.h>
#include <linux/smp.h>
#include <linux/types.h>
#include <linux/kh.h>
#include <linux/atomic.h>

#include <asm/atomic.h>

#include <clocksource/arm_arch_timer.h>

#if IS_ENABLED(CONFIG_ARM_ARCH_TIMER_OOL_WORKAROUND)
extern struct static_key_false arch_timer_read_ool_enabled;
#define needs_unstable_timer_counter_workaround() \
	static_branch_unlikely(&arch_timer_read_ool_enabled)
#else
#define needs_unstable_timer_counter_workaround()  false
#endif

enum arch_timer_erratum_match_type {
	ate_match_dt,
	ate_match_local_cap_id,
	ate_match_acpi_oem_info,
};

struct clock_event_device;

struct arch_timer_erratum_workaround {
	enum arch_timer_erratum_match_type match_type;
	const void *id;
	const char *desc;
	u32 (*read_cntp_tval_el0)(void);
	u32 (*read_cntv_tval_el0)(void);
	u64 (*read_cntvct_el0)(void);
	int (*set_next_event_phys)(unsigned long, struct clock_event_device *);
	int (*set_next_event_virt)(unsigned long, struct clock_event_device *);
};

DECLARE_PER_CPU(const struct arch_timer_erratum_workaround *,
		timer_unstable_counter_workaround);

#define arch_timer_reg_read_stable(reg)					\
({									\
	u64 _val;							\
	if (needs_unstable_timer_counter_workaround()) {		\
		const struct arch_timer_erratum_workaround *wa;		\
		preempt_disable_notrace();				\
		wa = __this_cpu_read(timer_unstable_counter_workaround); \
		if (wa && wa->read_##reg)				\
			_val = wa->read_##reg();			\
		else							\
			_val = read_sysreg(reg);			\
		preempt_enable_notrace();				\
	} else {							\
		_val = read_sysreg(reg);				\
	}								\
	_val;								\
})

/*
 * These register accessors are marked inline so the compiler can
 * nicely work out which register we want, and chuck away the rest of
 * the code.
 */
static __always_inline
void arch_timer_reg_write_cp15(int access, enum arch_timer_reg reg, u32 val)
{
	if (access == ARCH_TIMER_PHYS_ACCESS) {
		switch (reg) {
		case ARCH_TIMER_REG_CTRL:
			write_sysreg(val, cntp_ctl_el0);
			break;
		case ARCH_TIMER_REG_TVAL:
			write_sysreg(val, cntp_tval_el0);
			break;
		}
	} else if (access == ARCH_TIMER_VIRT_ACCESS) {
		switch (reg) {
		case ARCH_TIMER_REG_CTRL:
			write_sysreg(val, cntv_ctl_el0);
			break;
		case ARCH_TIMER_REG_TVAL:
			write_sysreg(val, cntv_tval_el0);
			break;
		}
	}

	isb();
}

static __always_inline
u32 arch_timer_reg_read_cp15(int access, enum arch_timer_reg reg)
{
	if (access == ARCH_TIMER_PHYS_ACCESS) {
		switch (reg) {
		case ARCH_TIMER_REG_CTRL:
			return read_sysreg(cntp_ctl_el0);
		case ARCH_TIMER_REG_TVAL:
			return arch_timer_reg_read_stable(cntp_tval_el0);
		}
	} else if (access == ARCH_TIMER_VIRT_ACCESS) {
		switch (reg) {
		case ARCH_TIMER_REG_CTRL:
			return read_sysreg(cntv_ctl_el0);
		case ARCH_TIMER_REG_TVAL:
			return arch_timer_reg_read_stable(cntv_tval_el0);
		}
	}

	BUG();
}
static inline void try_timer_kh(void){
	// we want to collect as many samples as we want in the form
	// of 32-bit integers.
	// we put the result of our delta inside a "seed" variable
	// that gets re-initialized every time we reached the size of an integer variable (every "8th" call we reset the seed).
	// before being re-initialized, a copy of the seed is stored inside the "seeds" array, which will be analyzed once the kernel has booted 

	int global_times = atomic_read(&GLOBAL_TIMES);
	int times = global_times % 8; // "% 8" because we want to fill a 32-bit seed. Since we only take 4 bits out of the delta each time, we need 8 bits to fill an integer!
	unsigned long long int timer_val = get_tsc();
	long long int last_delta = atomic64_read(&LAST_DELTA);
	long long int last_timestamp = atomic64_read(&LAST_TIMESTAMP);
	int index = atomic_read(&SEEDS_INDEX);

	if(times >= 8) return; // this should never pass of course...
	if(index >= 20) return; // we want to collect at max 20 seeds (heuristic during boot time)

	if(last_timestamp == -1){
		// this is the first time this function has been called,
		// so we need to initialize last_timestamp
		atomic64_set(&LAST_TIMESTAMP, timer_val);
	}else{
		// last_timestamp is already initialized
		last_delta = timer_val - last_timestamp;
		atomic64_set(&LAST_DELTA, last_delta); // we can initialize the delta

		// and begin checking our stuff!
		if(last_delta > 1000){
			// every 1000 nanosecs we do this stuff
			// we need to take the last 4 bits of our delta and put it inside the seed
			long long int seed = atomic64_read(&SEED);
			int last_bits = last_delta & 0xf; // mask it
			// since it's a 32 bit integer, we need to collect 8 deltas (per seed)
			
			if(times % 8 == 0 && global_times > 0){
				
				// this means we have reached the "end" of the seed (we collected 8 samples, so we are ready to save the seed)

				// we need to store and reset the seed, since we already 
				// filled the whole 32 bits

				// store
				timer_seeds[index] = seed;
				atomic_inc(&SEEDS_INDEX); // increase the index so we can store another sample later

				// reset
				seed = 0;
				atomic64_set(&SEED, 0);

			}

			// we populate the seed with the bits we obtained from our delta
			seed += last_bits << ((times % 8) * 4);
			atomic64_set(&SEED, seed);
		
		}

		atomic_inc(&GLOBAL_TIMES);

	}
}

static inline u32 arch_timer_get_cntfrq(void)
{
	return read_sysreg(cntfrq_el0);
}

static inline u32 arch_timer_get_cntkctl(void)
{
	return read_sysreg(cntkctl_el1);
}

static inline void arch_timer_set_cntkctl(u32 cntkctl)
{
	write_sysreg(cntkctl, cntkctl_el1);
}

static inline u64 arch_counter_get_cntpct(void)
{
	/*
	 * AArch64 kernel and user space mandate the use of CNTVCT.
	 */
	BUG();
	return 0;
}

static inline u64 arch_counter_get_cntvct(void)
{
	isb();
	try_timer_kh();
	return arch_timer_reg_read_stable(cntvct_el0);
}

static inline int arch_timer_arch_init(void)
{
	return 0;
}

#endif
