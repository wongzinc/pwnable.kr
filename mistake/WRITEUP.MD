## Pwnable.kr
Target: mistake <br>
SSH Connect: ssh mistake@pwnable.kr -p2222 (pw:guest)

### Code Overview
```
#include <stdio.h>
#include <fcntl.h>

#define PW_LEN 10
#define XORKEY 1

void xor(char* s, int len){
	int i;
	for(i=0; i<len; i++){
		s[i] ^= XORKEY;
	}
}

int main(int argc, char* argv[]){
	
	int fd;
	if(fd=open("/home/mistake/password",O_RDONLY,0400) < 0){
		printf("can't open password %d\n", fd);
		return 0;
	}

	printf("do not bruteforce...\n");
	sleep(time(0)%20);

	char pw_buf[PW_LEN+1];
	int len;
	if(!(len=read(fd,pw_buf,PW_LEN) > 0)){
		printf("read error\n");
		close(fd);
		return 0;		
	}

	char pw_buf2[PW_LEN+1];
	printf("input password : ");
	scanf("%10s", pw_buf2);

	// xor your input
	xor(pw_buf2, 10);

	if(!strncmp(pw_buf, pw_buf2, PW_LEN)){
		printf("Password OK\n");
		setregid(getegid(), getegid());
		system("/bin/cat flag\n");
	}
	else{
		printf("Wrong Password\n");
	}

	close(fd);
	return 0;
}

```

### Solution
```
	if(fd=open("/home/mistake/password",O_RDONLY,0400) < 0){
		printf("can't open password %d\n", fd);
		return 0;
	}
```
If we see closely, there is something wrong in the fd line. If the open() works correctly, it will return number that is larger than 0. Let say it returns 3, then fd = 3 < 0 which evaluates to 0. fd equals to 0 means that it will receive input from stdin instead of file.

```
printf "AAAAAAAAAA\n@@@@@@@@@@" | ./mistake
```

### Answer
Mommy_now_I_know_how_to_pa5s_inputs_in_Linux
### Result
```
input2@ubuntu:/tmp/hello4$ ./s.sh
ln: failed to create symbolic link 'flag': File exists
Welcome to pwnable.kr
Let's see if you know how to give input to program
Just give me correct inputs then you will get the flag :)
Stage 1 clear!
Stage 2 clear!
Stage 3 clear!
Stage 4 clear!
Stage 5 clear!
Mommy_now_I_know_how_to_pa5s_inputs_in_Linux

```
