import sys
import socket

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from utils.generator import generate_asymmetric
from utils.encryption import encrypt_message, decrypt_message
from utils.comparator import comparator
from utils.alphabetizer import alphabetizer

def start_client():
    num_files = int(input("\n\nEnter number of files: "))
    print("\n\nOn macOS, you can drag and drop a file into the terminal window to get its filepath.\nOn Windows, you can right click on a file, hold shift, and click on \"Copy as path\" to get its filepath.\n\n")
    print("Else, you can enter the filepath manually.\n\n")
    
    file_list = []
    for i in range(num_files):
        file = str(input("Enter filepath of file " + str(i+1) + ": "))
        file_list.append(file)
    print("\n\n[*] Awaiting corresponding party to upload files for comparison...")
        
    if (num_files > 0):
      try:
        file_list = alphabetizer(file_list)
        hash_list = comparator(file_list)
        hash_list = ", ".join(hash_list)
      except Exception as e:
        print(e)
  
    pem_public_key, private_key = generate_asymmetric()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8888))

    client_socket.send(pem_public_key)
    client_socket.recv(1024)

    encrypted_symmetric_key = client_socket.recv(1024)
    symmetric_key = private_key.decrypt(
        encrypted_symmetric_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None))

    client_socket.setblocking(False)
    
    if num_files > 0:
      client_message = num_files
      iv, tag, ciphertext = encrypt_message(str(client_message).encode(), symmetric_key)
      client_socket.send(iv + tag + ciphertext)
      
    if hash_list:
      client_message = str(hash_list)
      iv, tag, ciphertext = encrypt_message(client_message.encode(), symmetric_key)
      client_socket.send(iv + tag + ciphertext)
        
    while True:
        try:
          incoming_message = client_socket.recv(1024)
          if incoming_message:
            iv, tag, ciphertext = incoming_message[:12], incoming_message[12:28], incoming_message[28:]
            decrypted_message = decrypt_message(iv, tag, ciphertext, symmetric_key)
            decrypted_message = decrypted_message.decode()
            
            print(f"\n\n{decrypted_message}")
            if "All" not in decrypted_message:
              same_index = decrypted_message.index("file(s) [")
              same_index2 = decrypted_message.index("] are the same.")
              same = decrypted_message[same_index+9:same_index2]
              same = same.split(", ")
            
              diff_index = decrypted_message.index("File(s) [")
              diff_index2 = decrypted_message.index("] are different.")
              diff = decrypted_message[diff_index+9:diff_index2]
              diff = diff.split(", ")
            
              print("On your machine, the following files have a match with the corresponding party:")
              for i in same:
                print(file_list[int(i)])
              print("\n\n")
              print("The following files have no match with the corresponding party:")
              for i in diff:
                print(file_list[int(i)])
              print("\n\n")
              print("These filepaths and its contents are not sent to the other party.\n\n")
            break
        except:
          pass
        
    client_socket.close()
    sys.exit()
