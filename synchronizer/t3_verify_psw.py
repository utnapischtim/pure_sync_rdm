import hashlib, binascii, os
 
def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')
 
def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


sp = '74c3c1643f12b5663f58460042d7c827644605ae810031fecb7d90c16e4171a59b14b4970fda2b8575b85c8dc9e7fbc2ccb18787b51f885a40de245f89ff830a09c84bdf2ba96e67de9b4077356dc33dc0183937dfb0488f85f5e0a7ac6d8e2e'
pp = '123456'
print(verify_password(sp,pp))