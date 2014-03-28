/* 
	GPS.C

	written by: Manuel Dionne
        credit to: the internet
*/

#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>

#define FNAME "send.wav"
#define BAUD 60
#define MARK 20300
#define SPACE 20250
#define SAMPLE_RATE 48000
#define POSITION_X 300
#define POSITION_Y 600
#define IDENTIFIER 1
#define LOOPDELAY 2
#define TRUE 1
#define FALSE 0
#define BILLION 1E9

double currenttime(struct timespec rawtime) {
	double time;
	clock_gettime(CLOCK_REALTIME, &rawtime);
	time = (rawtime.tv_sec) + (double)(rawtime.tv_nsec) / (double)BILLION;
	return time;
}


int main(int argc,char *argv[]) {

	int refreshtime = 0;
	struct timespec rawtime;
	double oldtime;
	char command[118];
	char aplay[19];
	while(TRUE) {
		if(!oldtime > 1)
			oldtime = 0.000000;
  		printf ("[GPS] %lf\n", time);

		//encoding the stuff
		sprintf(command, "echo \"|START|%lf|%d_%d|%d|END\" | sudo ./minimodem --tx -8 -f %s %d --space %d --mark %d", oldtime, POSITION_X, POSITION_Y, IDENTIFIER, FNAME, BAUD, SPACE, MARK);
		printf("[GPS] %s\n", command);
		system(command);

		//transmitting it 
		oldtime = currenttime(&rawtime);
		sprintf(aplay, "sudo aplay %s -f S16_LE", FNAME);
		system(aplay);
		printf("[GPS] sleeping...\n");
		sleep(2);
		refreshtime++;
		if(refreshtime >= 100)
		{
			printf("this is supposed to refresh the time");
			system("sudo service ntp stop && sudo ntpd -qg && sudo service ntp start");
			refreshtime = 0;
		}
	}


	return 0;
}
