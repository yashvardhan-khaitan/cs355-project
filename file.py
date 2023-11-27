# hash library containing hash functions
import hashlib

# List of files (array of file names gatherered from user loop and stored in file_name)
file_name = ['random_words.txt', 'file1.txt', 'file2.txt']
hashList = {}

# go through file_name
for file in file_name:
    with open(file, 'rb') as file_to_check:
        # read contents of file
        data = file_to_check.read()    

        # pipe contents of the file through
        hash = hashlib.sha256(data).hexdigest()

        # append hash to list
        hashList.update({file: hash})

        #close file
        file_to_check.close()

# Get list of all hashes for user
print(hashList)
