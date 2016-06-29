#include <stdio.h>
#include <unistd.h>

int main(int argc, char const *argv[]){
    printf("Hello, I'm an dangerous program.\n");
    for (int i=0; i<argc; i++){
        printf("my %d argument: %s\n", i, argv[i]);
    }
	printf("my pid is: %d\n", getpid());
	return 0;
}