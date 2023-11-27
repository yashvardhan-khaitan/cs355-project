import sys
import socket
import threading

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

from utils.generator import generate_asymmetric, generate_symmetric
from utils.encryption import encrypt_message, decrypt_message
from utils.comparator import comparator
from utils.alphabetizer import alphabetizer

def send_message(client_socket, message, symmetric_key):
    iv, tag, ciphertext = encrypt_message(message.encode(), symmetric_key)
    client_socket.send(iv + tag + ciphertext)

def accept_client(client_socket, encoded_public_key):
  try:
    client_socket.send(encoded_public_key)

    client_pem_public_key = client_socket.recv(1024)
    client_public_key = serialization.load_pem_public_key(client_pem_public_key)

    symmetric_key = generate_symmetric()

    encrypted_symmetric_key = client_public_key.encrypt(
        symmetric_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None))
    client_socket.send(encrypted_symmetric_key)
    
    num_files = client_socket.recv(1024)
    num_files = int(decrypt_message(num_files[:12], num_files[12:28], num_files[28:], symmetric_key).decode())
    print("\n\n[*] Corresponding party has uploaded " + str(num_files) + " file(s) for comparison. You must upload the same number to proceed.")
    
    print("\n\nOn macOS, you can drag and drop a file into the terminal window to get its filepath.\nOn Windows, you can right click on a file, hold shift, and click on \"Copy as path\" to get its filepath.\n\n")
    print("Else, you can enter the filepath manually.\n\n")
    
    file_list = []
    for i in range(num_files):
        file = str(input("Enter filepath of file " + str(i+1) + ": "))
        file_list.append(file)
        
    if (num_files > 0):
      file_list = alphabetizer(file_list)
      hash_list = comparator(file_list)

    client_hash_list = []
    while True:
        message = client_socket.recv(1024)
        if message:
            iv, tag, ciphertext = message[:12], message[12:28], message[28:]
            decrypted_message = decrypt_message(iv, tag, ciphertext, symmetric_key)
            break

    client_hash_list = decrypted_message.decode().split(", ")
    same, diff = [], []
    if (num_files > 0):
      for i in range(len(hash_list)):
        if (hash_list[i] in client_hash_list):
          same.append(i)
        else:
          diff.append(i)
      if (len(same) == len(hash_list)):
        send_message(client_socket, "[*] All files are the same.\n\n", symmetric_key)
        print("[*] All files are the same.\n\n")
      elif (len(diff) == len(hash_list)):
        send_message(client_socket, "[*] All files are different.\n\n", symmetric_key)
        print("[*] All files are different.\n\n")
      else:
        msg = "[*] The files have been sorted alphabetically. In alphabetical order, file(s) " + str(same) + " are the same. File(s) " + str(diff) + " are different.\n\n"
        send_message(client_socket, msg, symmetric_key)
        print("\n\n")
        print(msg)
        print("On your machine, the following files have a match with the corresponding party:")
        for i in same:
          print(file_list[i])
        print("\n\n")
        print("The following files do not have a match with the corresponding party:")
        for i in diff:
          print(file_list[i])
        print("\n\n")
        print("The corresponding party has been notified of the results.\n\nThese filepaths and its contents are not sent to the corresponding party.\n\n")
  except Exception as e:
    print(e)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8888))
    server_socket.listen(5)
    print("\n\n[*] Waiting to receive data from corresponding party...")

    encoded_public_key, private_key = generate_asymmetric()

    while True:
        client, addr = server_socket.accept()
        print(f"[*] Accepted data from {addr[0]}:{addr[1]}")
        t = threading.Thread(target=accept_client, args=(client, encoded_public_key))
        t.start()
        t.join()
        break
    server_socket.close()
    sys.exit()

