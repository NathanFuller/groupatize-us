import hashlib
import sha3

s = hashlib.sha3_256()
s.update("bob")
print s.hexdigest()