from pwn import *

elf = context.binary = ELF('./badchars32')
p = process()
print(p.recvuntil(': '))
p.sendline(cyclic(50))
p.wait()
crash_addr = p.corefile.fault_addr
offset = cyclic_find(crash_addr)
print(offset)