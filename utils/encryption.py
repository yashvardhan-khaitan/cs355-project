import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def encrypt_message(message, symmetric_key):
  iv = os.urandom(12)
  encryptor = Cipher(algorithms.AES(symmetric_key), modes.GCM(iv), backend=default_backend()).encryptor()
  ciphertext = encryptor.update(message) + encryptor.finalize()
  return (iv, encryptor.tag, ciphertext)

def decrypt_message(iv, tag, ciphertext, symmetric_key):
  decryptor = Cipher(algorithms.AES(symmetric_key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
  return decryptor.update(ciphertext) + decryptor.finalize()