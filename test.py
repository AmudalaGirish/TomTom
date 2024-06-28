import base64

def encode_username(username):
    return base64.urlsafe_b64encode(username.encode()).decode()

def decode_username(encoded_username):
    return base64.urlsafe_b64decode(encoded_username.encode()).decode()

username = 'pawan@'
encoded_username = encode_username(username)
print(encoded_username)

# encoded_username = "cGF3YW5AMTIz"
# username = decode_username(encoded_username)
# print(username)
