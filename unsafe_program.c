#include <stdio.h>
#include <unistd.h>

int main(int argc, char const *argv[]){
	// fork();
	printf("%s\nmy argument: %s\n", "Hello, I'm an dangerous program.", argv[1]);
	return 0;
}