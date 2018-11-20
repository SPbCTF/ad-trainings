

def super_secret_hash(data):
    result = 0
    for c in data:
        result += ((ord(c) ^ 0x14) * (ord(c) ^ 0x88))
        result %= 8
    return result
