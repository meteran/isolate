#include <stdio.h>
#include <unistd.h>

int main(int argc, char const *argv[]){
	printf("%s\nmy argument: %s\n", "Hello, I'm an dangerous program.", argv[1]);
//	printf("my pid is: %d\n", getpid());
	return 0;
}