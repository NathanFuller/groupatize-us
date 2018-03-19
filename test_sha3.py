import hashlib
import sha3
from random import randint

s = hashlib.sha3_256()
s.update("bob")
print s.hexdigest()

# make a hash to use as ID
def encodeID(num, alphabet="23456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ"):
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        num, rem = divmod(num, base)
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)
	    
print encodeID(randint(10000000, 99999999))