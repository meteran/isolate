#include <stdio.h>     /* printf */
#include <seccomp.h>   /* libseccomp */
#include <sys/prctl.h> /* prctl */
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>


static int run_program(int argc, char const *argv[]){
	int i;
	prctl(PR_SET_NO_NEW_PRIVS, 1);

	prctl(PR_SET_DUMPABLE, 0);

	char **args = (char **) malloc(sizeof(char *)*argc);

    if (!args){
        perror("malloc");
        return -1;
    }

	for (i=1; i<argc; i++){
	    args[i-1] = argv[i];
	}

	scmp_filter_ctx ctx;
	ctx = seccomp_init(SCMP_ACT_KILL);

    if (!ctx) {
        perror("seccomp_init");
        return -1;
    }

    int syscalls_whitelist[] = {SCMP_SYS(read), SCMP_SYS(fstat),
                                SCMP_SYS(mmap), SCMP_SYS(mprotect), 
                                SCMP_SYS(munmap), SCMP_SYS(open), 
                                SCMP_SYS(arch_prctl), SCMP_SYS(brk), 
                                SCMP_SYS(access), SCMP_SYS(exit_group), 
                                SCMP_SYS(close), SCMP_SYS(rt_sigreturn),
                                SCMP_SYS(exit), SCMP_SYS(write)};
    int syscalls_whitelist_length = sizeof(syscalls_whitelist) / sizeof(int);

    for (i = 0; i < syscalls_whitelist_length; i++) {
            if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, syscalls_whitelist[i], 0) != 0) {
                printf("loading syscall %d failed\n", syscalls_whitelist[i]);
                return -1;
            }
        }
	if (seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(execve), 1, SCMP_CMP(0, SCMP_CMP_EQ, (scmp_datum_t)args[0]))){
	    perror("seccomp_rule_add execve");
	    return -1;
	}

	if (seccomp_load(ctx)){
	    perror("seccomp");
	    return -1;
	}
	seccomp_release(ctx);

	execve(args[0], args, NULL);

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