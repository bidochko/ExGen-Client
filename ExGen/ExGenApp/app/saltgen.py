import random
def createSalt():
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars=[]
    return (''.join(random.choice(ALPHABET) for i in range(16)))
