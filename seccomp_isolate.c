#include <stdio.h>     /* printf */
#include <seccomp.h>   /* libseccomp */
#include <sys/prctl.h> /* prctl */
#include <sys/types.h>
#include <unistd.h>


static int run_program(int argc, char const *argv[]){
	int i, ret=0;
	prctl(PR_SET_NO_NEW_PRIVS, 1);

	prctl(PR_SET_DUMPABLE, 0);
	char *argg[] = {argv[1], argv[2], NULL};

	scmp_filter_ctx ctx;
	ctx = seccomp_init(SCMP_ACT_KILL);

    int syscalls_whitelist[] = {SCMP_SYS(read), SCMP_SYS(fstat),
                                SCMP_SYS(mmap), SCMP_SYS(mprotect), 
                                SCMP_SYS(munmap), SCMP_SYS(open), 
                                SCMP_SYS(arch_prctl), SCMP_SYS(brk), 
                                SCMP_SYS(access), SCMP_SYS(exit_group), 
                                SCMP_SYS(close)};
    int syscalls_whitelist_length = sizeof(syscalls_whitelist) / sizeof(int);

    for (i = 0; i < syscalls_whitelist_length; i++) {
            if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, syscalls_whitelist[i], 0) != 0) {
                printf("load syscall white list failed\n");
                return -1;
            }
        }

	seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(rt_sigreturn), 0);
	// seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0);
	seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0);
	// seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0);
	seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
	seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(execve), 0);

	printf("seccomp_load\n");
	ret = seccomp_load(ctx);
	seccomp_release(ctx);
	printf("running program... %d\n", ret);

	execve("./unsafe_program", argg, NULL);

	return 0;
}

int main(int argc, char const *argv[]){
	int res;

	if (argc<2){
		printf("usage: seccomp_isolate <unsafe_program>[ <arg>[ <arg>...]]\n");
		return 0;
	}

	res = fork();
	if (res < 0){
		perror("fork");
	}
	if (res == 0){
		run_program(argc, argv);
	}
	return 0;
}