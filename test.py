import os

file_path = 'tomtom/private_key.pem'
if os.path.isfile(file_path):
    print(f"File '{file_path}' exists.")
    with open(file_path, 'rb') as f:
        vapid_private_key = f.read()
    print(vapid_private_key)
else:
    print(f"File '{file_path}' does not exist.")