from pwn import *

# r = remote('pwnable.kr', 9007)
# 遠端連線發現太慢...所以用之前的憑證登入並在`/tmp`下創建資料夾並改用localhost連線
r = remote('localhost', 9007)

r.recvuntil('- Ready? starting in 3 sec... -')

for i in range(100):
    r.recvuntil('N=')
    inf = r.recvline().decode('utf-8').strip().split(" C=")
    N = int(inf[0])
    C = int(inf[1])
    print("[Round {}] N={}, C={}".format(i+1, N, C))

    start = 0
    end = N

    for _ in range(C):
        if (start == end) :
            print("* Correct Ans is {}".format(int(start)))
            break

        mid = (start + end)//2
        idx_str = ' '.join(str(i) for i in range(start, mid+1))
        r.sendline(idx_str)
        weight = int(r.recvline())
        print("- Weight for idx from {} to {} is {}".format(start, mid, weight))

        if (weight & 1 != 0):
            end = mid
        else:
            start = mid + 1


    r.sendline(str(start))
    print(r.recvline())

r.interactive()

