/* Copyright (C) Gianmarco Lusvardi, Emiliano Maccaferri 2023
 *
 * This software has been produced in fulfilment of the requirements of the
 * kernel hacking university exam
 *
 * THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE
 * LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDER PROVIDE THE
 * PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
 * FITNESS FOR A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
 * PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE,
 * YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION.  
 *
 * IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING WILL
 * ANY COPYRIGHT HOLDER, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL,
 * SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR
 * INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR
 * DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR
 * A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH
 * HOLDER HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.  
 *
 * If the disclaimer of warranty and limitation of liability provided above
 * cannot be given local legal effect according to their terms, reviewing courts
 * shall apply local law that most closely approximates an absolute waiver of
 * all civil liability in connection with the Program, unless a warranty or
 * assumption of liability accompanies a copy of the Program in return for a
 * fee.
*/

/* In this example we are going to read and write from sysfs */

#include <linux/fs.h>
#include <linux/init.h>
#include <linux/kobject.h>
#include <linux/module.h>
#include <linux/string.h>
#include <linux/sysfs.h>
#include <linux/delay.h>

static inline unsigned long long int read_tsc(void){
	unsigned long long int cpu_val = 0;
	#if defined(__aarch64__) || defined(_M_ARM64)
		//  we are on arm64
		// https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/arch/arm/include/asm/arch_timer.h?id=082471a8efe1a91d4e44abec202d9e3067dcec91#n34
		// we access the VIRTUAL (v stands for virtual) timer
		asm volatile ("msr cntv_ctl_el0, %0": "=r" (cpu_val));
	#elif defined(__x86_64__) || defined(_M_X64)
		// we are on x86_64
		asm volatile("RDTSC\n\t" \
		"SHL $0x20, %%rdx\n\t" \
		"OR %%rax, %%rdx\n\t" \
		"MOV %%rdx, %0\n\t": "=r" (cpu_val)::"%rax", "%rdx");
	
	// #else
		// how to handle err?
	#endif

	return cpu_val;
}

static struct kobject *mymodule;

static unsigned long sleepns = 1000;
static unsigned long long int lastdelta = 0;
static unsigned long long int ticks;

static ssize_t sleepns_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf){
	return sprintf(buf, "%lu\n", sleepns);
}

static ssize_t sleepns_store(struct kobject *kobj, struct kobj_attribute *attr, char *buf, size_t count){
	sscanf(buf, "%lu", &sleepns);
	return count;
}

static ssize_t lastdelta_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf){
	unsigned long long int t1, t2;
	if (sleepns != 0) {
		t1 = read_tsc();
		ndelay(sleepns);
		t2 = read_tsc();
	} else {
		t1 = read_tsc();
		t2 = read_tsc();
	}

	lastdelta = t2 - t1;
	return sprintf(buf, "%llu\n", lastdelta);
}

static ssize_t ticks_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf) {
	if (sleepns != 0)
		ndelay(sleepns);
	ticks = read_tsc();
	return sprintf(buf, "%llu\n", ticks);
}

static struct kobj_attribute sleepns_attribute = __ATTR(sleepns, 0660, sleepns_show, (void *)sleepns_store);
static struct kobj_attribute lastdelta_attribute = __ATTR(lastdelta, 0444, lastdelta_show, NULL);
static struct kobj_attribute ticks_attribute = __ATTR(ticks, 0444, ticks_show, NULL);

static int __init mymodule_init(void){
	int error = 0;
	pr_info("deltats: initialized\n");
	mymodule = kobject_create_and_add("deltats", kernel_kobj);
	if (!mymodule) return -ENOMEM;

	if ((error = sysfs_create_file(mymodule, &sleepns_attribute.attr))) goto err;
	if ((error = sysfs_create_file(mymodule, &lastdelta_attribute.attr))) goto err;
	if ((error = sysfs_create_file(mymodule, &ticks_attribute.attr))) goto err;

err:
	if (error)
		pr_info("failed to create file in /sys/kernel/deltats\n");
	return error;
}

static void __exit mymodule_exit(void){
	pr_info("deltats: exit success\n");
	kobject_put(mymodule);
}

module_init(mymodule_init);
module_exit(mymodule_exit);

MODULE_LICENSE("GPL");
