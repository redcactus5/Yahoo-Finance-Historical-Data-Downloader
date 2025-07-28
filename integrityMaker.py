import hashlib
import base64
import random


def makeSillyString():
    
    fileNames=["LICENSES/BeautifulSoup-MIT-LICENSE.txt","LICENSES/easyCLI-GPL3-LICENSE.txt","LICENSES/Nuitka-Apache-2.0-LICENSE.txt","LICENSES/Playwright-Apache-2.0-LICENSE.txt","LICENSES/Python-PSFL-2-LICENSE.txt","LICENSES/Mozilla-Public-License-2.0-LICENSE.txt","LICENSE.txt"]
    new=[]
    for name in fileNames:
        new.append(str(base64.b85encode(name.encode())))
    #remember to remove trailing ' and preceeding b'
    print("☺".join(new))
    print("\n")
    hashes=[]
    hashSalter=random
    for file in fileNames:
        with open(file, 'r') as current:
            #i would like to apologize to my ram
            hasher=hashlib.sha256()
            text=current.read().encode()
            hasher.update(text)
            hashes.append(base64.b85encode(hasher.hexdigest().encode()).decode())

    print("☺".join(hashes))

    input()
