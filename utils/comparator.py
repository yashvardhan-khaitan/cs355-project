import hashlib

def comparator(file_list):
  hash_list = []
  
  # i = 0
  for file in file_list:
    if (file.index('\'') == 0):
      file = file[1:]
      file = file[:len(file)-1]
    
    with open(file, 'rb') as file_to_check:
      data = file_to_check.read()    
      
      hash = hashlib.sha256(data).hexdigest()
      # hash_list.update({i: hash})
      hash_list.append(hash)
      
      file_to_check.close()
      # i += 1
  return hash_list