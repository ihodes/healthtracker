# -*- coding: utf-8 -*-
import scrypt
import base64
import random



def encrypt_password(password, maxtime=0.1, datalength=64):
    crypted = scrypt.encrypt(_randstr(datalength), str(password), maxtime=maxtime)
    b64 = base64.b64encode(crypted)
    return b64


def verify_password(hashed_password, guessed_password, maxtime=0.1):
    try:
        b64 = base64.b64decode(hashed_password)
        scrypt.decrypt(b64, guessed_password, maxtime)
    except scrypt.error:
        return False
    else: 
        return True


def _randstr(length):
    return ''.join(chr(random.randint(0,255)) for i in range(length))
