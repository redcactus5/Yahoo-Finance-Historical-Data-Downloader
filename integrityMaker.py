import hashlib
import base64
import random
import string
import os
def makeSalt():
    saltMine=list("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~")

    random.shuffle(saltMine)
    mineLen=len(saltMine)-1

    salt=[saltMine[random.randint(0,mineLen)] for char in range(86)]
    random.shuffle(salt)
    
    salt="".join(salt)
    return salt.encode()

def makeSillyString():
    fileNames=os.listdir("LICENSES/")
    for i in range(len(fileNames)):
        fileNames[i]="LICENSES/"+fileNames[i]
    fileNames.extend(["LICENSE.txt",])
    print("\n")
    hashes=[""]*(len(fileNames)*3)
    
        


    


    
    
    writeIndex=0
    for file in fileNames:
        hashes[writeIndex]=(base64.b85encode(file.encode()).decode())
        writeIndex+=1
        with open(file, 'r') as current:
            #i would like to apologize to my ram
            hasher=hashlib.sha256()
            text=current.read().encode()
            digisalt=makeSalt()
            hasher.update(text)
            hasher.update(digisalt)
            hashes[writeIndex]=base64.b85encode(hasher.hexdigest().encode()).decode()
            writeIndex+=1
            hashes[writeIndex]=digisalt.decode()
            writeIndex+=1

    

    
    print("[",end="")
    for index,name in enumerate(hashes):
        print("\""+name+"\"",end="")
        if(index<(len(hashes)-1)):
            print(", ",end="")
    print("]")
    
    print("\n"*2)

def makeFileString():
    files=os.listdir("renderer/firefox")
    interestedExtensions=[".dll","dll","exe",".exe"]
    interestedFiles=[]
    for file in files:
        if(os.path.isdir(file)):
            interestedFiles.append(file)
        else:
            extention=os.path.splitext(file)[1]
            if(extention in interestedExtensions):
                interestedFiles.append(file)

    displayList=["("]
    for index,file in enumerate(interestedFiles):
        displayList.append("\"")
        displayList.append(file)
        displayList.append("\"")
        if(index<len(interestedFiles)-1):
            displayList.append(", ")
        else:
            displayList.append(")")
    
    print("".join(displayList))
        
makeFileString()
#makeSillyString()