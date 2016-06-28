CC=gcc
CFLAGS=-Wall -std=c99 -lseccomp


default: clean example seccomp

example: unsafe_program.c
	$(CC) unsafe_program.c -o unsafe_program

seccomp: seccomp_isolate.c
	$(CC) seccomp_isolate.c -o seccomp_isolate $(CFLAGS)
	

.PHONY: clean
clean:
	rm -f seccomp_isolate seccomp_isolate.o
	rm -f unsafe_program unsafe_program.o