import hashlib
import base64
import random
import string

def makeSillyString():
    
    fileNames=["LICENSES/BeautifulSoup-MIT-LICENSE.txt","LICENSES/easyCLI-GPL3-LICENSE.txt","LICENSES/Nuitka-Apache-2.0-LICENSE.txt","LICENSES/Playwright-Apache-2.0-LICENSE.txt","LICENSES/Python-PSFL-2-LICENSE.txt","LICENSES/Mozilla-Public-License-2.0-LICENSE.txt","LICENSE.txt"]
    new=[]
    for name in fileNames:
        new.append(base64.b85encode(name.encode()).decode())
    #remember to remove trailing ' and preceeding b'
    print("☺".join(new))
    print("\n")
    hashes=[]
    
    saltMine=list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~")

    random.shuffle(saltMine)
    mineLen=len(saltMine)-1

    salt=[saltMine[random.randint(0,mineLen)] for char in range(86)]
    random.shuffle(salt)
    
    salt="".join(salt)
    digisalt=salt.encode()
    for file in fileNames:
        with open(file, 'r') as current:
            #i would like to apologize to my ram
            hasher=hashlib.sha256()
            text=current.read().encode()
            hasher.update(text)
            hasher.update(digisalt)
            hashes.append(base64.b85encode(hasher.hexdigest().encode()).decode())

    hashes.append(salt)

    
    print("☺".join(hashes))
    print("\n")
  

makeSillyString()