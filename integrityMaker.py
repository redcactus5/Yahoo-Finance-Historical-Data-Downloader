import hashlib
import base64
import random
import string
import os
import random
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

    decoders=[]
    nuhashes=[]
    for hash in hashes:
        shuffled=shuffle(list(hash))
        decoders.append(shuffled[1])
        nuhashes.append("".join(shuffled[0]))

    
    print("(",end="")
    for index,name in enumerate(hashes):
        print("\""+name+"\"",end="")
        if(index<(len(hashes)-1)):
            print(", ",end="")
        else:
            print(")")

    message5=["("]
    for index, char in enumerate(decoders):
        
        message5.append(str(char))
   
        if(index<(len(decoders)-1)):
            message5.append(", ")
            
            message5.append("\n")
        else:
            message5.append(")")
    print("\n"*2)
    print("".join(message5))

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
        
def shuffle(inputList:list[str])->tuple[list[str],list[int]]:
    #make a copy of our input
    copyList=inputList.copy()
    #create a list of indexes
    randomPosList=list(range(len(copyList)))
    #shuffle it
    random.shuffle(randomPosList)
    #put the items in copyList in the shuffled order
    scrambledList = [copyList[i] for i in randomPosList]
    return (scrambledList,randomPosList)

#makeFileString()
#makeSillyString()
def makeSecurityErrorMessage():
    import dependencies.easyCLI as easyCLI
    errorMessage=easyCLI.multilineStringBuilder(("ERROR: integrity check failed, License file(s) not found.",
                "This program is open source and must be distributed with its licenses.",
                "Please ensure the LICENSE.txt is present in the program's root folder, and", 
                "the LICENSES directory is present and contains: \"easyCLI-GPL3-LICENSE.txt\",", 
                "\"libxml2-MIT-LICENSE.txt\", \"libxslt-MIT-LICENSE.txt\", \"Python-PSFL-2-LICENSE.txt\",", 
                "\"Mozilla-Public-License-2.0-LICENSE.txt\", \"Playwright-Apache-2.0-LICENSE.txt\",", 
                "\"Nuitka-Apache-2.0-LICENSE.txt\", and \"lxml-BSD-3-Clause-LICENSE.txt\"."))
    message2=list(base64.b85encode(errorMessage.encode()).decode())
    
    shuffled=shuffle(message2)
    message2=shuffled[0]
    message4=shuffled[1]
    message4.reverse()
    message3=["("]
    for index, char in enumerate(message2):
        message3.append("\"")
        message3.append(char)
        message3.append("\"")
        if(index<(len(message2)-1)):
            message3.append(", ")
            if(index%20==0):
                message3.append("\n")
        else:
            message3.append(")")
    
    message5=["("]
    for index, char in enumerate(message4):
        message5.append("\"")
        message5.append(str(char))
        message5.append("\"")
        if(index<(len(message2)-1)):
            message5.append(", ")
            if(index%20==0):
                message5.append("\n")
        else:
            message5.append(")")
    print("".join(message3))
    print("\n\n\n")
    print("".join(message5))
makeSecurityErrorMessage()