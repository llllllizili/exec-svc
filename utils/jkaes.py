#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   jkaes.py
@Time    :   2020/09/02 11:53:53
'''


import base64
from Crypto.Cipher import AES
#from .jklog import jklog
from utils.jklog import jklog

AES_SECRET_KEY = "jkstack123456789" #此处16|24|32个字符
IV = "9a8b7c6d5e4f3g2h"
 
# padding算法
BS = len(AES_SECRET_KEY)
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1:])]

class jkAes(object):
    def __init__(self):
        self.key = AES_SECRET_KEY
        self.mode = AES.MODE_CBC
 
    #加密函数
    def encrypt(self, text):
        cryptor = AES.new(self.key.encode("utf8"), self.mode, IV.encode("utf8"))
        # self.ciphertext = cryptor.encrypt(bytes(pad(text), encoding="utf8"))
        ciphertext = cryptor.encrypt((pad(text)))
        # 使用base64编码
        return base64.b64encode(ciphertext)
 
    #解密函数
    def decrypt(self, text):
        if isinstance(text,str):
            text=text.encode()
        if not text:
            return text
        try:
            decode = base64.b64decode(text)
            cryptor = AES.new(self.key.encode("utf8"), self.mode, IV.encode("utf8"))
            plain_text = cryptor.decrypt(decode)
            return bytes.decode(unpad(plain_text))
        except ValueError:
            jklog('error','Input strings must be a multiple of 16 in length')
            return '__jkstack_decrypt_error'

 
if __name__ == '__main__':
    jkaes = jkAes()
    ttt = "JKstack@1"
    e = jkaes.encrypt(ttt)
    print(e)
    
    # java = "COuW0p+rDf1GYL0ai4TXBd2YQawa/jTejSuydT3k+w4="
    d = jkaes.decrypt("gJfkONLPGVjOxTwniOg4yA==")
    print(d)
