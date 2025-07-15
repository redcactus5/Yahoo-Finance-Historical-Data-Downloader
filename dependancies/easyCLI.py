'''
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 
'''


import dependancies.easyCliPrivateConfigBackend as easyCliPrivateConfigBackend
from dependancies.easyCliPrivateConfigBackend import UIHeaderClass
#handy newline function. not necessary just nice to have
from dependancies.easyCliPrivateConfigBackend import ln

#this is easy cli, a simple and easy to use cli framework!

#warning, this library is not thread or multiprocessing safe, though can be used safely if you use best practices

from dependancies.easyCLIStopwatch import Stopwatch
from dependancies.easyCLIStopwatch import EasyCLIStopwatchError






#note: clears the screen as part of the process
def recheckTerminalType():
    easyCliPrivateConfigBackend.__PrivateAnsiCapableHandlerObject__.recheckAnsiCapable()
    easyCliPrivateConfigBackend.__PrivateClearHandlerObject__.reDetermineTerminalClearType()

        
    
        

        
def multilineStringBuilder(lines:list[str])->str:
    return "\n".join(lines)


        

def getAnsiCapable()->bool:
    return easyCliPrivateConfigBackend.__PrivateAnsiCapableHandlerObject__.getAnsiCapable()





#y value zero index is current y, x value zero index is leftmost collumn. there isnt any protection if the screen isnt tall enough. do not enter ansi strings, it breaks things
def overwriteStringAtPos(yRelativeToCursor:int,absoluteXPos:int,text:str):
    if(not getAnsiCapable()):
        raise Exception("error: this function requires an ANSI compliant terminal. \nthe current terminal has been determined to not be ANSI compliant.")


    #uses ansi escape codes

    #safety checks
    if(yRelativeToCursor<0):
        raise ValueError("error: y value argument must be a positive integer!\ngiven y value: "+str(yRelativeToCursor))

    if(absoluteXPos<0):
        raise ValueError("error: x value argument must be a positive integer!\ngiven x value: "+str(absoluteXPos))

    if(chr(27) in set(text)): # type: ignore
        raise ValueError("ANSI escape sequences are not allowed in text.")

    #ansi and tuple and strings? oh my!
    #in all seriouslness this is just an ansi escape code mess, in a tuple with our values so we can use a more readable 
    #format without string concat losses, thanks to the join call on that empty string. aka: SHENANIGANS!
    message="".join(("\x1b[?25l\x1b[s\x1b[", str(yRelativeToCursor),"A\x1b[",str(absoluteXPos+1), "G",text,"\x1b[u\x1b[?25h"))
    
    #print that mess
    
    print(message, end='')
    











#need to add timer class to easy cli and modify it



#need to update ui header system to use a class and object system with a default of none







#self explanitory, it clears the terminal
def clear():
    easyCliPrivateConfigBackend.__PrivateClearHandlerObject__.clear()


def getUIHeader():
    return easyCliPrivateConfigBackend.__currentLoadedUIHeaderDoNotEdit__


def setHeaderScreenName(newName:str):
    if(easyCliPrivateConfigBackend.__currentLoadedUIHeaderDoNotEdit__ is None):
        raise ValueError("error: no ui header has been set! one must be set before changing the screen name!")
    elif((issubclass(type(easyCliPrivateConfigBackend.__currentLoadedUIHeaderDoNotEdit__), UIHeaderClass))):
        if(issubclass(type(newName),str)):
            easyCliPrivateConfigBackend.__currentLoadedUIHeaderDoNotEdit__.setCurrentScreenName(newName)
        else:
            raise ValueError("error: non string argument given for new screen name. \ntype of provided new name: "+str(type(newName))+" value of new name: "+str(newName))
    else:
        raise ValueError("error: loaded ui header is not of a compatible type. type must be a child class of UIHeaderClass.\nclass of loaded ui header: "+str(type(easyCliPrivateConfigBackend.__currentLoadedUIHeaderDoNotEdit__)))

 
        
        

def setUIHeader(UIHeader: UIHeaderClass | None):
    
    if((easyCliPrivateConfigBackend.__currentLoadedUIHeaderDoNotEdit__ is None) or (isinstance(type(easyCliPrivateConfigBackend.__currentLoadedUIHeaderDoNotEdit__), UIHeaderClass))):
        easyCliPrivateConfigBackend.__currentLoadedUIHeaderDoNotEdit__=UIHeader
    else:
        raise ValueError("error: new ui header object is not of a compatible type. type must be none or a child class of UIHeaderClass.\nclass of provided ui header: "+str(type(easyCliPrivateConfigBackend.__currentLoadedUIHeaderDoNotEdit__)))



#ui header function to save time
def uiHeader():
    clear()
    
    if((isinstance(easyCliPrivateConfigBackend.__currentLoadedUIHeaderDoNotEdit__, UIHeaderClass))):
        easyCliPrivateConfigBackend.__currentLoadedUIHeaderDoNotEdit__.drawUIHeader()
    elif(type(easyCliPrivateConfigBackend.__currentLoadedUIHeaderDoNotEdit__)==None):
        raise ValueError("error: no ui header has been set! one must be set before drawing the header!")
    else:
        raise ValueError("error: loaded ui header is not of a compatible type. type must be a child class of UIHeaderClass.\nclass of loaded ui header: "+str(type(easyCliPrivateConfigBackend.__currentLoadedUIHeaderDoNotEdit__)))

 


def multipleChoiceScreen(message:str,prompt:str|None, optionsMessage:tuple, options:tuple, accuracy:int, accuracyMode:int):
    #this function has multiple accuracy modes, so accuracy mode is used to select the one you want
    #0 is exact mode, it ignores the accuracy argument and compares input to option exactly
    #1 is trim mode, it trims the user input to the length of the accuracy variable, then compares that to the options list
    #2 is adaptive mode, it dynamically adjusts the accuracy value to the length of the input if it is lower than accuracy, and trims both the input and the option strings to the same length, then compares those. this can result in incorrect selections being made, so use with caution
    if(accuracyMode<0 or accuracyMode>2):
        #put error throwing code here
        raise ValueError("argument error: invalid accuracy mode argument. argument: {"+str(accuracyMode)+"} given, \nonly inclusive integer values between 0 and 2 supported")
        

    while True:
        uiHeader()
        print(message)
        if(not((prompt=="")or(type(prompt)==None)or(prompt is None))):
            ln(2)
            print(prompt)

        ln()
        for m in optionsMessage:
            print(m)
        ln()

        selection=input("please enter selection:")

        if(len(selection)>=1):

            if(accuracyMode==0):#exact mode
                for i in range(len(options)):
                    if(selection==str(options[i])):
                        return i
                    

            elif(accuracyMode==1):#trim mode
                if(accuracy>len(selection)):
                    accuracy=len(selection)

                for i in range(len(options)):
                    if(selection[:accuracy]==str(options[i])):
                        return i
                    

            elif(accuracyMode==2):#adaptive mode
                if(accuracy>len(selection)):
                    accuracy=len(selection)

                for i in range(len(options)):
                    if(selection[:accuracy]==str(options[i])[:accuracy]):
                        return i




        uiHeader()
        print("syntax error: bad input. please enter one of the provided options")
        ln(2)
        input("press enter to continue")




            

def booleanQuestionScreen(message:str,prompt:str|None):
    choice=multipleChoiceScreen(message,prompt,("(y)es","(n)o"),("yes","no"),1,2)
    if(choice==0):
        return True
    return False







def textEntry(message:str,prompt:str):
    while True:
        uiHeader()
        
        print(message)

        if(not((prompt=="")or(type(prompt)==None)or (prompt is None))):
            ln(2)
            print(prompt)
        ln()

        text=input()

        if(multipleChoiceScreen("is \""+text+"\" correct?",None,("(c)onfirm","(r)e-enter"),("confirm","re-enter","reenter"),1,2)==0):
            return text




def enterFileNameScreen(message:str,prompt:str):
    while True:
        uiHeader()
        
        print(message)
        if(not((prompt=="")or(type(prompt)==None)or(prompt is None))):
            ln(2)
            print(prompt)
        ln()

        fileName=input("file name:")

        if(multipleChoiceScreen("is \""+fileName+"\" correct?",None,("(c)onfirm","(r)e-enter"),("confirm","re-enter","reenter"),1,2)==0):
            return fileName




def errorScreen(errorMessage:str):
    uiHeader()
    print(errorMessage)

    ln()
    print("now returning to the main menu")
    ln(2)
    input("press enter to continue")





def finishedScreen(finishedMessage:str, completionTime:float):
    uiHeader()

    print(finishedMessage)
    print("finished in "+str(completionTime)+" second(s)")
    ln()
    print("now returning to the main menu")
    ln(2)
    input("press enter to continue")





def terminalExportScreen(finishedMessage:str, completionTime:float, exportMessage:str, exportedText:str):
    uiHeader()

    print(finishedMessage)
    print("finished in "+str(completionTime)+" second(s)")
    ln(2)
    print(exportMessage)
    print(exportedText)
    ln()
    print("now returning to the main menu")
    ln(2)
    input("press enter to continue")


