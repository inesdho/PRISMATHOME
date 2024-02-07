#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>

int main(int argc, char *argv[]) {

    int pid = atoi(argv[1]);
    int signal = atoi(argv[2]);

    if (kill(pid, signal) == -1) {
        perror("Error sending signal");
        return 1;
    }

    return 0;
}
