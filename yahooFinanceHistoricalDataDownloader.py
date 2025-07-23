'''
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 
'''

URLLISTFILE="config/stockLinkConfig.json"
COMMANDFILE="config/commands.json"
BROWSERPATH="webproxy/Playwright.exe"
DOWNLOADRETRYLIMIT=5


from bs4 import BeautifulSoup
from bs4 import element
from bs4 import Tag
import json
from playwright.sync_api import sync_playwright
import time
import random
import dependencies.easyCLI as easyCLI
import csv
import os
from datetime import datetime
from datetime import date
from datetime import timedelta
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import bisect
from typing import Any

def shuffle(inputList:list):
    #make a copy of our input
    copyList=inputList.copy()
    #create a list of indexes
    randomPosList=list(range(len(copyList)))
    #shuffle it
    random.shuffle(randomPosList)
    #put the items in copyList in the shuffled order
    scrambledList = [copyList[i] for i in randomPosList]
    return (scrambledList,randomPosList)


def retrieveWebPages(links:list[str],downloadStartTimeout:float,downloadCompletionTimeout:float):
    #grab our constants
    global BROWSERPATH
    global DOWNLOADRETRYLIMIT
    easyCLI.fastPrint("starting webpage retrieval...\n")
    #make a list for what we download
    pages=[None]*len(links)
    #shuffle our links to throw bot detectors off our scent
    scrambled=shuffle(links)
    links=scrambled[0]#type: ignore
    ogPos=scrambled[1]

    #the print statements explain most of it
    with sync_playwright() as p:
        easyCLI.fastPrint("launching retriever proxy...")
        browser = p.webkit.launch(executable_path=BROWSERPATH,headless=True)
        try:
            
            easyCLI.fastPrint("done.\n")
            #loop through links
            lenString=str(len(links))
            for urlIndex, url in enumerate(links):
                #keep track of retries
                tryCount=1
                while(True):
                    easyCLI.fastPrint("page "+str(urlIndex+1)+" of "+lenString)
                    easyCLI.fastPrint("requesting page from server...")
                    page = browser.new_page()
                    try:
                        page.goto(url,wait_until="domcontentloaded",timeout=downloadStartTimeout)


                        easyCLI.fastPrint("starting page load...")

                        #wait for the table to load
                        page.wait_for_selector("table.table.yf-1jecxey",timeout=downloadCompletionTimeout)
                        #wait for the title to load
                        page.wait_for_selector("h1.yf-4vbjci",timeout=downloadCompletionTimeout)
                        #wait for the table to load its data
                        page.wait_for_selector("td.yf-1jecxey loading",timeout=downloadCompletionTimeout, state="detached")
                        page.wait_for_selector("td.yf-1jecxey .loading",timeout=downloadCompletionTimeout, state="detached")
                        page.wait_for_selector("td.yf-1jecxey",timeout=downloadCompletionTimeout)
                        
                        
                        #wait extra time just to be safe
                        wait=1+random.randint(0,1)+random.random()
                        easyCLI.fastPrint("waiting "+f"{wait:.1f}"+" seconds for load completion...")
                        time.sleep(wait)

                        easyCLI.fastPrint("saving data...")
                        content = page.content()  # get rendered HTML
                        #reverse the scrambling to put the data in the correct order
                        pages[ogPos[urlIndex]]=content#type: ignore
                        easyCLI.fastPrint("cleaning up...")
                        page.close()
                        easyCLI.fastPrint("page download complete")
                        wait=1+random.randint(0,3)+random.random()
                        easyCLI.fastPrint("waiting "+f"{wait:.1f}"+"  second antiantibot delay...")
                        time.sleep(wait)
                        easyCLI.fastPrint("done\n")
                        break

                    #detect the page randomly not loading, clean up, and try again
                    except PlaywrightTimeoutError:
                        #cleanup the fail
                        page.close()
                        tryCount+=1
                        if(tryCount>DOWNLOADRETRYLIMIT):#if we go past our retry limit, give up
                            raise Exception("download error: retry limit exceeded for url: "+str(links[urlIndex]))
                        easyCLI.fastPrint("\ndownload timed out")
                        easyCLI.fastPrint("retrying...\n")
                        easyCLI.fastPrint("starting attempt "+str(tryCount)+"...")


            
            easyCLI.fastPrint("cleaning up retriever proxy...")
            browser.close()
            easyCLI.fastPrint("done\n")
        #if there is an error first close the browser then crash, so we dont leave resources running
        except Exception as E:
            browser.close()
            raise(E)
    
  
    easyCLI.fastPrint("all page retrievals complete.\n\n")
    return pages






def retrieveTableAndName(htmlText)->tuple[str,Tag]:
    
    #create a beautiful soup object for this raw page so we can parse it
    scraper=BeautifulSoup(htmlText, "html.parser")

    
    #find the name
    name=scraper.find("h1",class_="yf-4vbjci")
    
    if(name is None):
        raise Exception("error: no stock name found in page.")
    
    name=name.get_text()#type: ignore

    #find the table in the page
    table=scraper.find("table")
    

    if(table is None):
        raise Exception("error: no tables found in page.")
    
    if(isinstance(table,Tag)):
        return (name,table)
    else:
        raise Exception("error: table in page is corrupted.")


def retrieveHtmlListTablesAndName(htmlDataList):
 
    rawDataList=[]
    easyCLI.fastPrint("extracting tables...\n")
    
    for pageNumber, page in enumerate(htmlDataList):
        easyCLI.fastPrint("extracting table "+str(pageNumber+1)+" of "+str(len(htmlDataList)))
        rawDataList.append(retrieveTableAndName(page))
        
    easyCLI.fastPrint("done.\n\n")
    return rawDataList



def parseDataSet(retrievedData):
    easyCLI.fastPrint("parsing table for "+str(retrievedData[0])+"...")

    table:Tag=retrievedData[1]
    for span in table.select("span"):
        span.decompose()
    #find all the rows
    rows=table.find_all("tr")
    #make an array to store the data for this table
    dataList=[]
    #also a dictionary to store associated dates and indexes of dataList they are for
    dates={}


    #safety check to make sure the table is populated
    if(len(rows)<1):
        raise Exception("error, table is empty.")
    

    #validate to make sure the table is actually the one we want. if it fails, yahoo changed their website, or the link was wrong
    ValidatorRowStrings=["Date","Open","High","Low","Close","Adj Close","Volume"]
    #a nice set of lookup tables we need
    datapointOptionList=["date","open","high","low","close","adj close","volume"]
    
    
    headerRow=rows[0].find_all("th")#type: ignore
    

    if((len(headerRow)>0) and all((datapoint.get_text(strip=True).strip() == ValidatorRowStrings[index]) for index, datapoint in enumerate(headerRow))):
        #if this is what we want
        rows.pop(0)
        ValidatorRowStringsLen=len(ValidatorRowStrings)
        
        #because we dont add some rows, we use this variable to avoid desync. I tried using an index counter, but we desync when we skip an index.
        rowCount=0
        #go through every row
        for row in rows:
            lineData={}
            #extract the cells
            rowData:list[Tag]=row.find_all("td")#type: ignore
            #if this is a row we aren't supposed to ignore
            
            if(len(rowData)==ValidatorRowStringsLen):#type: ignore


                #go through its columns
                for pointIndex, point in enumerate(rowData):
                    #if this is the date index
                    if(pointIndex==0):#do the special case for saving date
                        parsedDate = datetime.strptime(point.get_text(strip=True), "%b %d, %Y").date()

                        dates[parsedDate]=rowCount
                    else:#otherwise save it like normal
                        lineData[datapointOptionList[pointIndex]]=str(point.get_text(strip=True))#type: ignore

                #save what we extracted
                dataList.append(lineData)
                #increment rowcount since we found a row
                rowCount+=1
    else:
        raise Exception("error, invalid table")
    

    easyCLI.fastPrint("done.\n")
    

    #return the data we extracted
    return {"name":str(retrievedData[0]),"data":dataList,"dates":dates}






def parseDataSets(rawDataList,sortAlphabetical):
    easyCLI.fastPrint("starting dataset parsing...\n")

    parsedData:list[dict]=[parseDataSet(dataSet) for dataSet in rawDataList]
    
    #if alphabetical sorting mode is on
    if(sortAlphabetical):
        parsedData=sorted(parsedData, key=lambda dataSet: dataSet["name"])
    
    easyCLI.fastPrint("parsing complete.\n\n")
    return parsedData






def loadLinks() -> tuple[list[str],bool,float,float] | bool:

    #create a dictionary for our link config and load its location string
    global URLLISTFILE
    jsonDict:dict=dict()
    #create our template
    template={
        "links":["put historical data links here"],
        "sort alphabetical":"set to true if you want your stocks sorted alphabetically",
        "page load begin timeout":"put the time in seconds you want to give the page to start loading here (a value of zero means no timeout)",
        "page load completion timeout":"put the time in seconds you want to give the retrieval to complete here (used for all 6 completion checks) (a value of zero means no timeout)"
    }
    #if we cant find the list, save our template in its place, then exit
    if(not os.path.exists(URLLISTFILE)):
        easyCLI.waitForFastWriterFinish()
        easyCLI.uiHeader()
        print("no yahoo finance historical data page link file found!")
        print("now generating template file...")
        with open(URLLISTFILE,"w") as config:
            json.dump(template,config)
        print("successful.\n\n")
        print("please enter your historical data links into the \""+URLLISTFILE+"\" then restart the program to download data.\n\n")
        input("press enter to finish")
        return False
    

    #load the links file
    with open(URLLISTFILE) as config:
        jsonDict=json.load(config)

    #create a list for our links
    links:list[str]=[]

    #validation step
    try:
        links=jsonDict.get("links")#type:ignore
        

    
    except Exception:
        raise Exception("config error: config \"links\" list corrupted or not found")

    #make a variable for the sorting variable 
    shouldSort=False
    #do error detection
    try:
        #save our should sort value
        shouldSort=jsonDict.get("sort alphabetical")
    except:
        raise Exception("config error: config links \"should sort\" value corrupted or not found")
    
    #make a variable for the start timeout
    startTimeout=0

    try:
        #save our start timeout value
        startTimeout=jsonDict.get("page load begin timeout")
    except:
        raise Exception("config error: config links \"page load begin timeout\" corrupted or not found")

    endTimeout=0

    try:
        endTimeout=jsonDict.get("page load completion timeout")
    except:
        raise Exception("config error: config links page load begin timeout corrupted or not found")

    #check if the template is found
    if(len(links)==1):
        if(links[0]=="put historical data links here"):
            if(shouldSort=="set to true if you want your stocks sorted alphabetically"):
                if(startTimeout=="put the time in seconds you want to give the page to start loading here (a value of zero means no timeout)"):
                    if(endTimeout=="put the time in seconds you want to give the retrieval to complete here (used for all 6 completion checks) (a value of zero means no timeout)"):
                        easyCLI.waitForFastWriterFinish()
                        #if so, print a message then exit
                        easyCLI.uiHeader()
                        print("found link file is the template file!")
                        print("please enter your historical data links into the \""+URLLISTFILE+"\" then restart the program to download data.\n\n")
                        input("press enter to finish")
                        return False

    #more error detection
    if(not isinstance(links,list)):
        raise Exception("config error: config \"links\" list corrupted or not found")
    elif(len(links)==0):
        raise Exception("config error: config \"links\" list is empty!")
    elif(not isinstance(shouldSort,bool)):
        raise Exception("config error: config \"should sort\" value corrupted or not found")
    elif(not isinstance(startTimeout,(float,int))):
        raise Exception("config error: config \"page load begin timeout\" value corrupted or not found")
    elif(isinstance(startTimeout,(float,int))and(startTimeout<0)):
        raise Exception("config error: config \"page load begin timeout\" value must be 0 or greater!")
    elif(not isinstance(endTimeout,(float,int))):
        raise Exception("config error: config \"page load completion timeout\" value corrupted or not found")
    elif(isinstance(endTimeout,(float,int))and(endTimeout<0)):
        raise Exception("config error: config \"page load completion timeout\" value must be 0 or greater!")
    else:
        startTimeout=float(startTimeout)
        endTimeout=float(endTimeout)

    #some link shenanigans to grab the data for the current date
    endID="period2="
    #loop through the links
    for link in range(len(links)):
        if(type(links[link])!=str):#check if the link actually exists
            raise Exception("link error: non string link found")
        #look for the part we are interested in
        idPos=links[link].find(endID)
        #if we find it, overwrite the old unix time value with the current one
        if(idPos!=-1):
            links[link]=links[link][0:idPos+len(endID)]+str(int(time.time()))
    

    return (links,shouldSort,startTimeout,endTimeout)






def loadCommands():

    #create our main variables
    global COMMANDFILE
    jsonDict:dict=dict()
    #create our template
    template={
            "commands":[
                {
                    "command":"set this to either specific dates, date range, or all data",
                    "attributes":["put attributes you want here"],
                    "dates":["put dates here"]
                }
            ]
    }
    #if we cant find the file
    if(not os.path.exists(COMMANDFILE)):
        #save our template in its place then exit
        easyCLI.waitForFastWriterFinish()
        easyCLI.uiHeader()
        print("no command file found!")
        print("now generating template file...")
        with open(COMMANDFILE,"w") as config:
            json.dump(template,config)
        print("successful.\n\n")
        print("please enter your commands into the \""+COMMANDFILE+"\" then restart the program to download data.\n\n")
        input("press enter to finish")
        return False
    

    #load our file 
    with open(COMMANDFILE,"r") as config:
        jsonDict=json.load(config)
    #create a variable for our commands
    commandList:list[dict]=[]
    try:
        #grab our command list
        commandList=jsonDict.get("commands")#type: ignore
        #this massive messy if tree is just checking if the loaded file is our template
        if(len(commandList)==1):
            if(commandList[0].get("command")=="set this to either specific dates, date range, or all data"):
                if(len(commandList[0].get("attributes"))==1):#type: ignore
                    if(commandList[0].get("attributes")[0]=="put attributes you want here"):#type: ignore
                        if(len(commandList[0].get("dates"))==1):#type: ignore
                            if(commandList[0].get("dates")[0]=="put dates here"):#type: ignore
                                #if it is, print a message then exit
                                easyCLI.waitForFastWriterFinish()
                                easyCLI.uiHeader()
                                print("found command file is the template file!")
                                print("please enter your commands into the \""+COMMANDFILE+"\" then restart the program to download data.\n\n")
                                input("press enter to finish")
                                return False

    except Exception:
        raise Exception("config error: config command list corrupted or not found")


    #safety check
    if(type(commandList)!=list):
        raise Exception("config error: config command list corrupted or not found")
    
    
            
                
                
                

    return commandList





        
def findLine(dataset:dict,date:date)->dict|bool:
    #use our date and dataset values smartly to find the exact line we want then return it
    #grab our dates dict
    lookup:dict=dataset["dates"]
    #grab the dataList index for this date
    rawIndex=lookup.get(date)
    #if that date doesn't exist, send back that information
    if(rawIndex is None):
        return False
    index:int=rawIndex
    #otherwise grab the dataset
    dataList:list=dataset["data"]
    #and extract the index of that line from it
    line=dataList[index]

    return line

    
    
    



def findDateInsertionPoint(date:date,dates:list[date]):
    #very self explanatory


    #empty list special case
    if(len(dates)==0):
        return(2,0)
       # find insertion index with bisect (assuming dates sorted ascending)
    index = bisect.bisect_left(dates, date)

    

    if ((index < len(dates)) and (dates[index] == date)):
        # date exists
        return (0, index)
    elif (index < len(dates)):
        # insert before this index
        return (1, index)
    elif (index == len(dates)):
        # insert after last item
        return (2, False)

        

    raise Exception("insertion point search error: no insertion point found")




def equalizeListLens(listSet:list[list]):
    #TLDR: make sure the 2d array is a rectangle
    
    #find the longest sublist
    maxLen = max(len(subList) for subList in listSet)

    #go through and make every list that long if it isn't already
    for subList in listSet:
        #if it isn't long enough
        if(len(subList)<maxLen):
            #calculate how much longer it needs to be
            neededSpace=maxLen-len(subList)
            #and extend it with an empty list of that length
            subList.extend([None]*neededSpace)
    
#back up of old version  
'''
#make sure all categories exist
def updateCategories(newCategories:list, oldCategories:list, values:list[list])->tuple[bool,dict]:
    #lookup table of the categories and their orders
    categoryList={"date":0,"open":1,"high":2,"low":3,"close":4,"adj close":5,"volume":6}
    
    
    categoriesUpdated=False
    #loop through the categories we are adding
    oldCategoriesSet=set(oldCategories)
    for cat in newCategories:
        #if this is valid
        if((not(cat in categoryList)) or cat=="date"):
            raise Exception("command error, provided category: "+str(cat)+" is not a valid category\n valid categories "+", ".join(categoryList))
        
            #if we dont need to ignore this one
        elif(not(cat in oldCategoriesSet)):
            categoriesUpdated=True
            #find where in the category list it is supposed to go
            newPos:int=categoryList[cat]
            oldCategoriesSet.add(cat)
            #go through all currently existing categories
            for existing in range(len(oldCategories)):
                #find where in the master category list the old one is
                existingPos:int=categoryList[oldCategories[existing]]
                #if the new category must go behind the one at index zero
                if((existing==0)and(newPos<existingPos)):
                    #insert it there and give it an empty list
                    oldCategories.insert(existing,cat)
                    values.insert(existing,[])
                    break
                    #if the new category must after the end of the one at index zero
                elif((existing==len(oldCategories)-1)and(newPos>existingPos)):
                    #append it there and give it an empty list
                    oldCategories.append(cat)
                    values.append([])
                    break
                #if we are between before and after and not at the start or end
                elif((newPos<existingPos)and(newPos>categoryList[oldCategories[existing-1]])):
                    #insert it here, and give it a list
                    oldCategories.insert(existing,cat)
                    values.insert(existing,[])
                    break
                
    
    
    if(categoriesUpdated):
        newDict={}
        builderList=[(category,index) for index, category in enumerate(oldCategories)]
        newDict.update(builderList)
        return (True,newDict)
    
    return (False,None)#type: ignore
'''



#make sure all categories exist
def updateCategories(newCategories:list, oldCategories:list, values:list[list])->tuple[bool,dict]:
    #lookup table of the categories and their orders
    
    #categoryLookupList={0:"date",1:"open",2:"high",3:"low",4:"close",5:"adj close",6:"volume"}
    categoryListSet=set(range(7))
    
    categoriesUpdated=False
    #loop through the categories we are adding
    oldCategoriesSet=set(oldCategories)


    for cat in newCategories:
        #if this is valid
        if((not(cat in categoryListSet)) or cat==0):
            categoryList={"date":0,"open":1,"high":2,"low":3,"close":4,"adj close":5,"volume":6}
            raise Exception("command error, provided category: "+str(cat)+" is not a valid category\n valid categories "+", ".join(categoryList))
        
            #if we dont need to ignore this one
        elif(not(cat in oldCategoriesSet)):
            categoriesUpdated=True
            #find where in the category list it is supposed to go
            newPos:int=cat
            oldCategoriesSet.add(cat)
            #go through all currently existing categories
            for existing in range(len(oldCategories)):
                #find where in the master category list the old one is
                existingPos:int=oldCategories[existing]
                #if the new category must go behind the one at index zero
                if((existing==0)and(newPos<existingPos)):
                    #insert it there and give it an empty list
                    oldCategories.insert(existing,cat)
                    values.insert(existing,[])
                    break
                    #if the new category must after the end of the one at index zero
                elif((existing==len(oldCategories)-1)and(newPos>existingPos)):
                    #append it there and give it an empty list
                    oldCategories.append(cat)
                    values.append([])
                    break
                #if we are between before and after and not at the start or end
                elif((newPos<existingPos)and(newPos>oldCategories[existing-1])):
                    #insert it here, and give it a list
                    oldCategories.insert(existing,cat)
                    values.insert(existing,[])
                    break
                
    
    
    if(categoriesUpdated):
        newDict={}
        builderList=[(category,index) for index, category in enumerate(oldCategories)]
        newDict.update(builderList)
        return (True,newDict)
    
    return (False,None)#type: ignore
                    


                    
                        




def insertValue(date:date, value:str, category:str, categoryLookupDict:dict, values:list[list]):
    #find where to insert it and make sure that all hte category lists are equal size
    point=findDateInsertionPoint(date,values[0])
    equalizeListLens(values)
    #i am telling you linter, this will be an int, i wrote the code that makes the dict
    categoryIndex:int=categoryLookupDict[category]
    #if we are not creating a new spot for it
    if(point[0]==0):
        #overwrite whatever what there before with value
        values[categoryIndex][point[1]]=value
    #if it is going before the insertion point 
    elif(point[0]==1):
        #make a spot for it
        for column in range(len(values)):
            values[column].insert(point[1],None)
        #write its date
        values[0][point[1]]=date
        #write the data
        values[categoryIndex][point[1]]=value
    #if it is going after the end
    elif(point[0]==2):
        #make a spot for it at the end
        for column in range(len(values)):
            values[column].append(None)
        #write its date
        values[0][len(values[0])-1]=date
        #then write its value
        values[categoryIndex][len(values[0])-1]=value
    else:
        #paranoid doomsday clause. it should never happen, but if it does, we catch it
        raise Exception("insert value error: no insertion point found")


    

        
        
        
        
def generateDateRange(startDate:date,endDate:date):
    #make sure we are generating in ascending order, and if currently not, correct it so that we are
    start:date|None=None
    end:date|None=None
    if(startDate == endDate):
        return [startDate]
    elif(startDate < endDate):
        start=startDate
        end=endDate
    elif(startDate > endDate):
        start=endDate
        end=startDate
    else:
        #paranoid doomsday clause
        raise Exception("date comparison error: no comparison case hit")
    #paranoid safety check
    if((start is None)or(end is None)):
        raise Exception("date range generation error: internal start and end corrupted")
    
    #create a list to store every date in the range, inclusive
    dateRange=[]
    #create our index value, and set index to start
    current=start
    #loop through every date in between, including the start and end, and add that date to the list
    while current <= end:
        #compact the current date into a string in our format
        dateRange.append(current)
        #increment the day
        current = current + timedelta(days=1)
    return dateRange


def compileCommands(rawCommands:list[dict])->list[tuple[int,list[int],list[date]]]:
    easyCLI.fastPrint("compiling commands...")
    #cache this for later
    rawCommandLen=len(rawCommands)

    #preallocate while shutting up linter
    compiledCommands:Any=[None]*rawCommandLen

    #lookup tables
    masterCategoryList={"date":0,"open":1,"high":2,"low":3,"close":4,"adj close":5,"volume":6}
    commandIDTable={"specific dates":0,"all data":1,"date range":2}


    for commandNumber, command in enumerate(rawCommands):
        easyCLI.fastPrint("compiling command "+str(commandNumber+1)+" of "+str(rawCommandLen)+"...")
        #convert the dates to date objects
        dateList:list[str]=command["dates"]
        newDateList=[]
        if(len(dateList)>0): 
            newDateList=[datetime.strptime(date, "%m/%d/%Y").date() for date in dateList]
            

        commandID=commandIDTable[command["command"]]

        categoryList=command["attributes"]
        newCategoryList=[masterCategoryList[category] for category in categoryList]
        compiledCommands[commandNumber]=(commandID,newCategoryList,newDateList)
        print("done\n")


    
    easyCLI.fastPrint("compilation successful.\n\n")
    
    
    return compiledCommands

        
        

        

   
def validateCommands(commands:list[dict]):
    easyCLI.fastPrint("validating commands...\n")

    validCommands=set(["specific dates","all data","date range"])
    validAttributes=set(["date","open","high","low","close","adj close","volume"])


    for commandNumber, command in enumerate(commands):
        easyCLI.fastPrint("validating command "+str(commandNumber+1)+" of "+str(len(commands)))
        commandDates=command.get("dates")
        if(commandDates is None):
            raise Exception("command error: command "+str(commandNumber+1)+" has no dates value or key value")
        elif(type(commandDates)!=list):
            raise Exception("command error: command "+str(commandNumber+1)+" has an invalid dates value")
        for dateIndex, date in enumerate(commandDates):
            if(type(date)!=str):
                raise Exception("command error: date "+str(dateIndex)+" has an invalid value of: "+str(date)+" with a type of "+str(type(date)))

        
        
        #convert the dates to date objects
        dateList:list[str]=command["dates"]
        if(len(dateList)>0): 
            newDateList=[datetime.strptime(date, "%m/%d/%Y").date() for date in dateList]
            command["dates"]=newDateList

 



        attributes=command.get("attributes")
        if(attributes is None):
            raise Exception("command error: command "+str(commandNumber+1)+" has no attributes value or no key value")
        elif(type(attributes)!=list):
            raise Exception("command error: command "+str(commandNumber+1)+" has an invalid attributes value")
        for attributeIndex, attribute in enumerate(attributes):
            if((type(attribute)!=str) or (not(attribute in validAttributes))):
                raise Exception("command error: attribute "+str(attributeIndex)+" has an invalid value of: "+str(attribute)+" with a type of "+str(type(attribute)))

        
        parseCommand=command.get("command")
        if(parseCommand is None):
            raise Exception("command error: command "+str(commandNumber+1)+" has no command value or no key value")
        elif(type(parseCommand)!=str):
            raise Exception("command error: command "+str(commandNumber+1)+" has an invalid command value")
        elif(not (parseCommand in validCommands)):
            raise Exception("command error: command has an invalid value of: "+str(parseCommand)+" with a type of "+str(type(parseCommand)))
        easyCLI.fastPrint("done\n")
    easyCLI.fastPrint("validation successful.\n\n")


    return True




def executeCommand(stock:dict,dates:list[date],attributes:list[int],categoryLookupDict:dict[int,int],values:list[list]):
   
    for date in dates:
        #find the line for this date
        rawLine=findLine(stock,date)
        #if it doesn't exist, skip it
        if(rawLine==False):
            easyCLI.fastPrint("\nno data for date: "+date.strftime("%m/%d/%Y"))
            easyCLI.fastPrint("skipping...\n")
        elif(type(rawLine)==dict):
            line:dict=rawLine
            #otherwise, loop through all the attributes the command wants
            for attribute in attributes:
                #and grab their values for the line, then write them to the buffer for this stock
                insertValue(date,line.get(attribute),attribute,categoryLookupDict,values)#type: ignore




def processStocks(commands:list[tuple],stocks:list[dict]):
    easyCLI.fastPrint("executing commands...\n")

    buffer=[]
    
    #if we have something to do
    if(len(commands)>0):
        
        
        #preallocate for optimization reasons
        commandDates:list[date]=[]
        stockDates:dict=dict()
        dates=[]
        
        #minor optimization
        dateDispatcher = {
            0: lambda stockDates, commandDates: commandDates,  # specific dates
            1: lambda stockDates, commandDates: list(stockDates.keys()),  # all available dates
            2: lambda stockDates, commandDates: generateDateRange(commandDates[0], commandDates[1]),  # date range
        }

        #loop through our stocks
        for stockNumber, stock in enumerate(stocks):
            #extract name and create a list for the categories, and a 2d list for the values
            name=stock.get("name")
            categories=[0]
            categoryLookupDict:dict[int,int]={0:0}
            values:list[list]=[[]]
            stockDates:dict=stock["dates"]
            #create a variable for our progress through this stock
            
            #loop through our commands
            for commandNumber, command in enumerate(commands):
                #do tuple and string magic for our cli
                easyCLI.fastPrint("".join(("\nexecuting command ",str(commandNumber+1)," of ",str(len(commands))," on stock ",str(stockNumber+1)," of ",str(len(stocks)))))

                #grab and validate the values we need from the command
                
                action:int=command[0]
                commandDates:list[date]=command[2]
                attributes:list[int]=command[1]
                #make sure the lists have the attributes in the command
                possibleNewDict=updateCategories(attributes,categories,values)
                if(possibleNewDict[0]):
                    categoryLookupDict=possibleNewDict[1]
                #overwrite the old values with the corrected ones

                #0:specific dates
                #1:all data
                #2:date range
                #use our dispatcher to generate our dates list
                dates = dateDispatcher[action](stockDates, commandDates)
                #then execute the command
                executeCommand(stock,dates,attributes,categoryLookupDict,values)
               

            #convert the dates back to their original format
            fixedDates=[datetime.strftime(date,"%b %d, %Y") for date in values[0]]
            values[0]=fixedDates
            
            
            
            #save this stock's data as a render object
            renderObj={"name":name,"categories":categories,"values":values}
            #put it in our buffer
            buffer.append(renderObj)
            #increment our command count
           

    easyCLI.fastPrint("command execution done.\n\n")
    return buffer


                    

                
def outputRenderedResults(displayList:list[dict],outputFileName:str):
    easyCLI.fastPrint("rendering results...")
    #create a buffer
    buffer=[]
    categoryLookupList={0:"date",1:"open",2:"high",3:"low",4:"close",5:"adj close",6:"volume"}

    gap=[[None]]*3

    #loop through every render object
    for item in displayList:
        #render the header data
        buffer.append([item["name"],])
        #convert the compiled categories back to human readable ones
        categories=[categoryLookupList[datapoint] for datapoint in item["categories"]]
        buffer.append(categories)
        #grab the data
        values=item["values"]
        categoriesLen=len(categories)
        #loop through the y indexes
        for y in range(len(values[0])):
            #create a variable for the row
            line=[values[x][y] for x in range(categoriesLen)]
            buffer.append(line)
        #write some gaps 
        
        buffer.extend(gap)
    easyCLI.fastPrint("done.\n\n")
    #self explanatory, write the buffer to the file
    easyCLI.fastPrint("saving results as \""+outputFileName+"\"...")
    with open(outputFileName, "w", newline="") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(buffer)
    easyCLI.fastPrint("save successful.\n\n\n")
    


class YahooFinanceGrabberHeader(easyCLI.UIHeaderClass):
    #simple header class required by easy cli
    def __init__(self):
        super().__init__(None)

    def drawUIHeader(self):
        easyCLI.clear()
        print("Yahoo Finance Historical Data Downloader v1 by redcacus5\n\n")
        


#set the library ui header to the one we just made
easyCLI.setUIHeader(YahooFinanceGrabberHeader())



def licenseScreen():
    #very simple and self explanatory, not even any logic
    easyCLI.uiHeader()
    print(easyCLI.multilineStringBuilder(["Copyright and Licensing Information:\n",
    "Yahoo Finance Historical Data Downloader © 2025 redcactus5\n",
    "This program is NOT endorsed by, produced by, or affiliated with Yahoo Incorporated, its parent companies,",
    "or its subsidiaries, and was not created with their knowledge, consent, support, or involvement, in any way.\n",
    "Yahoo Finance Historical Data Downloader is free software released under the GNU General Public License,",
    "Version 3 (GPLv3).\n",
    "Powered by:",
    " - Python ©2001-2025 Python Software Foundation",
    " - easyCLI © 2025 redcactus5",
    " - BeautifulSoup ©2025 Leonard Richardson",
    " - Playwright © 2025 Microsoft",
    " - WebKit © 2025 Apple Inc.",
    " - Nuitka © Copyright 2025 Kay Hayen and Nuitka Contributors\n",
    "This project includes components licensed under the following licenses:",
    " - Python Software Foundation License Version 2",
    " - Apache License 2.0",
    " - GNU General Public License Version 3 (GPLv3)",
    " - GNU Library General Public License Version 2 (LGPLv2)",
    " - BSD 2 clause license",
    " - MIT License\n",
    "See the LICENSES/ directory for full license texts and details.\n\n"]))
    
    
    time.sleep(5)
    
    print("press enter to agree to the terms of the licenses and continue")
    input()

    



        


def main(fileName):
    #our main execution function, it mostly just stages out our steps
    #write the header
    easyCLI.fastUIHeader()
    easyCLI.fastPrint("starting data retrieval process...\n\n")
    #create and start our stopwatch
    timer=easyCLI.Stopwatch()
    timer.start()
    #startup checks and loading of config files
    easyCLI.fastPrint("loading urls and raw commands...")
    
    
    rawLinks=loadLinks()
    links:tuple=tuple()
    if((type(rawLinks)==bool)and(rawLinks==False)):
        return False
    elif(type(rawLinks)==tuple):
        links:tuple=rawLinks
        rawLinks=None
    else:
        raise Exception("error: url loading failed")
    

    rawCommands=loadCommands()
    commands:list=list()
    if((type(rawCommands)==bool)and(rawCommands==False)):
        return False
    elif(type(rawCommands)==list):
        commands=rawCommands
        rawCommands=None
    else:
        raise Exception("error: command loading failed")
 
    easyCLI.fastPrint("done.\n\n")
    
    validateCommands(commands)

    commands=compileCommands(commands)
    #grab the webpages
    webPages=retrieveWebPages(links[0],links[1],links[2])
    #extract their raw data
    rawData=retrieveHtmlListTablesAndName(webPages)
    #save ram, free no longer needed values
    webPages=None
    #parse that raw data
    dataSets=parseDataSets(rawData,links[1])
    #save ram, free no longer needed values
    rawData=None
    #execute our commands on that parsed data
    displayList=processStocks(commands,dataSets)
    #save ram, free no longer needed values
    dataSets=None
    outputRenderedResults(displayList,fileName)
    #stop the timer
    timer.stop()
    easyCLI.waitForFastWriterFinish()
    print("data retrieval complete!\n")
    print("finished in: "+timer.getUnitDeviatedTimeString()+"\n\n\n")
    input("press enter to finish")
    easyCLI.ln(3)
    





def startup():  
    licenseScreen()
    #if the user wants to download the data
    if(easyCLI.booleanQuestionScreen("would you like to download the pre-configured market data?",None)):
        #have the user the file name they want
        fileName=easyCLI.enterFileNameScreen("please enter the name of the output file.\nwarning, if the file already exists, it will be overwritten.","(do not include the file extension)")+".csv"
        #then start the main program
        main(fileName)
    #otherwise
    else:
        easyCLI.clear()
        print("well, thanks anyway!\n")








if(__name__=="__main__"):

    #devious check to make sure no one is doing an illegal thing and distributing without the open source licenses
    if((not os.path.exists("LICENSES/BeautifulSoup-MIT-LICENSE.txt"))or(not os.path.exists("LICENSES/easyCLI-GPL3-LICENSE.txt"))or(not os.path.exists("LICENSES/Nuitka-Apache-2.0-LICENSE.txt"))or(not os.path.exists("LICENSES/Playwright-Apache-2.0-LICENSE.txt"))or(not os.path.exists("LICENSES/Python-PSFL-2-LICENSE.txt"))or(not os.path.exists("LICENSES/WebKit-LGPL-2.0-BSD-License.txt"))or(not os.path.exists("LICENSE.txt"))):
        easyCLI.uiHeader()
        print("ERROR: License file(s) not found.")
        print("This program is open source and must be distributed with its licenses.")
        print("Please ensure the LICENSE.txt is present, and the LICENSES directory is \npresent and contains easyCLI-GPL3-LICENSE.txt, BeautifulSoup-MIT-LICENSE.txt, \nNuitka-Apache-2.0-LICENSE.txt, WebKit-LGPL-2.0-BSD-License.txt, and Playwright-Apache-2.0-LICENSE.txt.")
        input("press enter to finish")
    else:
        startup()
        print("now exiting...")
        easyCLI.ln(1)
        
         
