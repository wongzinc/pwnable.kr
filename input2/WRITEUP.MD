## Pwnable.kr
Target: input2 <br>
SSH Connect: ssh input2@pwnable.kr -p2222 (pw:guest)

### Code Overview
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main(int argc, char* argv[], char* envp[]){
	printf("Welcome to pwnable.kr\n");
	printf("Let's see if you know how to give input to program\n");
	printf("Just give me correct inputs then you will get the flag :)\n");

	// argv
	if(argc != 100) return 0;
	if(strcmp(argv['A'],"\x00")) return 0;
	if(strcmp(argv['B'],"\x20\x0a\x0d")) return 0;
	printf("Stage 1 clear!\n");	

	// stdio
	char buf[4];
	read(0, buf, 4);
	if(memcmp(buf, "\x00\x0a\x00\xff", 4)) return 0;
	read(2, buf, 4);
        if(memcmp(buf, "\x00\x0a\x02\xff", 4)) return 0;
	printf("Stage 2 clear!\n");
	
	// env
	if(strcmp("\xca\xfe\xba\xbe", getenv("\xde\xad\xbe\xef"))) return 0;
	printf("Stage 3 clear!\n");

	// file
	FILE* fp = fopen("\x0a", "r");
	if(!fp) return 0;
	if( fread(buf, 4, 1, fp)!=1 ) return 0;
	if( memcmp(buf, "\x00\x00\x00\x00", 4) ) return 0;
	fclose(fp);
	printf("Stage 4 clear!\n");	

	// network
	int sd, cd;
	struct sockaddr_in saddr, caddr;
	sd = socket(AF_INET, SOCK_STREAM, 0);
	if(sd == -1){
		printf("socket error, tell admin\n");
		return 0;
	}
	saddr.sin_family = AF_INET;
	saddr.sin_addr.s_addr = INADDR_ANY;
	saddr.sin_port = htons( atoi(argv['C']) );
	if(bind(sd, (struct sockaddr*)&saddr, sizeof(saddr)) < 0){
		printf("bind error, use another port\n");
    		return 1;
	}
	listen(sd, 1);
	int c = sizeof(struct sockaddr_in);
	cd = accept(sd, (struct sockaddr *)&caddr, (socklen_t*)&c);
	if(cd < 0){
		printf("accept error, tell admin\n");
		return 0;
	}
	if( recv(cd, buf, 4, 0) != 4 ) return 0;
	if(memcmp(buf, "\xde\xad\xbe\xef", 4)) return 0;
	printf("Stage 5 clear!\n");

	// here's your flag
	setregid(getegid(), getegid());
	system("/bin/cat flag");	
	return 0;
}


```

### Solution
#### Stage 1
First mistake I did was:
```
root@kali:~# $(perl -e 'print "\x00"')
bash: warning: command substitution: ignored null byte in input
```
When using command substitution, All trailing newlines are removed. Intermediate newlines are preserved.
Especially, Null Byte cannot appear due to C limitation. Bash will drop it and warned about the Null Byte in input. In C actually, every string will automatically be added \x00 at the end. So in order to conquered `c strcmp['A'],"\x00")` , we only need to insert ""(which -> "\x00"). However, we can't use perl here since command substitution will do word splitting on its own. Therefore, we need to use bash command here.

Apart from that, to clear "\x20\x0a\x0d", We can use Ansi-C quoting($''), to correctly evaluate escape
sequences. %.0s means print zero characters but still consumes one parameters.

```
./input2 $(printf "A %.0s" {1..64}) "" $'\x20\x0a\x0d' $(printf "B %.0s" {1..33})
```

#### Stage 2
It is apparent that one is read from stdin and the another is read from stderr. We can use redirection technique to conquer this one. 

<() is process substitution. inside bracket needs to put commands that can output data. The data will be inputted to /dev/fd/.. 
< is input redirection
'>' is output redirection
```
./input2 $(printf "A %.0s" {1..64}) "" $'\x20\x0a\x0d' $(printf "B %.0s" {1..33}) \
        < <(printf '\x00\x0a\x00\xff') 2< <(printf '\x00\x0a\x02\xff')
```

#### Stage 3
We can't use export command here `export VARIABLE_NAME=value` as the variable_name must be valid identifier. However, we have another workaround which is env command. -i to ignore all other environment variables

```
env -i $'\xde\xad\xbe\xef'=$'\xca\xfe\xba\xbe' \
/home/input2/input2 $(printf "A %.0s" {1..64}) "" $'\x20\x0a\x0d' $(printf "B %.0s" {1..33}) \
        < <(printf '\x00\x0a\x00\xff') 2< <(printf '\x00\x0a\x02\xff')
```

#### Stage 4
Since the server is only readable inside /tmp/.. , therefore we can `printf "\x00\x00\x00\x00" > $'\x0a'`  . We can stay inside /tmp/hello3 then executethe Stage 3's command.

#### Stage 5
https://blog.gtwang.org/programming/bash-tutorial-open-tcp-udp-socket/

In Bash, We can use below syntax to open tcp/udp socket
```
exec FILE_DESCRIPTOR<>/dev/PROTOCOL/HOST/PORT
```
- <> : File Descriptor enable read/write mode(input/output redirection)
- PROTOCOL: tcp or udp

To close socket: 
```
exec FILE_DESCRIPTOR<&-
exec FILE_DESCRIPTOR>&-
```

command -v is to check whether a command exists or not

#### Final
```bash
#!/bin/bash
set -uo pipefail
TARGET=/home/input2/input2
PORT=55555
printf "\x00\x00\x00\x00" > /tmp/hello4/$'\x0a'
cd /tmp/hello4
ln -s /home/input2/flag flag
env -i $'\xde\xad\xbe\xef=\xca\xfe\xba\xbe' \
"$TARGET" $(printf "A %.0s" {1..64}) "" $'\x20\x0a\x0d' "$PORT" $(printf "B %.0s" {1..32}) \
        < <(printf '\x00\x0a\x00\xff') 2< <(printf '\x00\x0a\x02\xff') &
srv=$! # get the pid of the program put behind background
sleep 0.3


if command -v nc > /dev/null 2>&1; then
    printf "\xde\xad\xbe\xef" | nc 127.0.0.1 "$PORT"
else 
    exec 3<>/dev/tcp/127.0.0.1/"$PORT"
    printf '\xde\xad\xbe\xef' >&3
    exec 3<&- 3>&-
fi
wait "$srv" # 等程式被回收

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
