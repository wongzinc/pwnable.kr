target = 0x21DD09EC
quotient = target // 5
rem = target - quotient * 4  

print(hex(quotient))
print(hex(rem))

#####################

# ./col $(perl -e 'print "\xc8\xce\xc5\x06"x4 . "\xcc\xce\xc5\x06"')