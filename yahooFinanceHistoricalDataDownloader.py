'''
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 
'''

linkConfigFile="config/stockLinkConfig.json"
commandFile="config/commands.json"
browserPath="webproxy/Playwright.exe"
tryLimit=5


from bs4 import BeautifulSoup
from bs4 import Tag
import json
from playwright.sync_api import sync_playwright
import time
import random
import dependancies.easyCLI as easyCLI
import csv
import os
import datetime
from datetime import timedelta
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import bisect


def shuffle(inputList:list):
    #make a copy of our input
    copyList=inputList.copy()
    #create an empty list to hold the scambled values
    scrambledList=[None]*len(copyList)
    #create a list to store the origonal positions of our scrambled values
    newToOldLookupTable=[]
    #create a list of indexes
    randomPosList=list(range(len(copyList)))
    #shuffle it
    random.shuffle(randomPosList)
    
    #put the items in copylist in the shuffled order, and save teir origonal positions
    for item in range(len(copyList)):
        scrambledList[item]=copyList[randomPosList[item]]
        newToOldLookupTable.append(randomPosList[item])
        
        
    

    return (scrambledList,newToOldLookupTable)


def retrieveWebPages(links:list[str]):
    #grab our constants
    global browserPath
    global tryLimit
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
        browser = p.webkit.launch(executable_path=browserPath,headless=True)
        try:
            
            easyCLI.fastPrint("done.\n")
            #loop through links
            lenstring=str(len(links))
            for urlIndex, url in enumerate(links):
                #keep track of retries
                tryCount=1
                while(True):
                    easyCLI.fastPrint("page "+str(urlIndex+1)+" of "+lenstring)
                    easyCLI.fastPrint("requesting page from server...")
                    page = browser.new_page()
                    try:
                        page.goto(url,wait_until="domcontentloaded",timeout=30000)


                        easyCLI.fastPrint("starting page load...")

                        #wait for the table to load
                        page.wait_for_selector("table.table.yf-1jecxey")
                        #wait for the title to load
                        page.wait_for_selector("h1.yf-4vbjci")
                        #wait for the table to load its data
                        page.wait_for_selector("td.yf-1jecxey loading", state="detached")
                        page.wait_for_selector("td.yf-1jecxey .loading", state="detached")
                        page.wait_for_selector("td.yf-1jecxey")
                        
                        
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
                        if(tryCount>tryLimit):#if we go past our retry limit, give up
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






def retrieveTableAndName(htmlText):
    
    #create a beautiful soup object for this raw page so we can parse it
    scraper=BeautifulSoup(htmlText, "html.parser")

    
    #find the name
    name=scraper.find("h1",class_="yf-4vbjci")
    
    if(name is None):
        raise Exception("error, no stock name found in page.")
    
    name=name.get_text()#type: ignore

    #find the table in the page
    table=scraper.find("table")


    if(table is None):
        raise Exception("error, no tables found in page.")
  
    
    return (name,table)


def retrieveHtmlListTablesAndName(htmlDataList):
    rawDataList=[]
    easyCLI.fastPrint("extracting tables...\n")
    
    for pagenumber, page in enumerate(htmlDataList):
        print("extracting table "+str(pagenumber+1)+" of "+str(len(htmlDataList)))
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
    #also a dictionary to store asociated dates and indexes of datalist they are for
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

        ValidatorRowStringsLen=len(ValidatorRowStrings)
        #go through every row
        for rowIndex, row in enumerate(rows):
            lineData={}
            #extract the cells
            rowData:list[Tag]=row.find_all("td")#type: ignore
            #if this is a row we arent suppposed to ignore
            
            if(len(rowData)==ValidatorRowStringsLen):#type: ignore


                #go through its collumns
                for pointIndex, point in enumerate(rowData):
                    #if this is the date index
                    if(pointIndex==0):#do the special case for saving date
                        parsedDate = datetime.datetime.strptime(point.get_text(strip=True), "%b %d, %Y")
                        fixedDate = parsedDate.strftime("%m/%d/%Y")
                        dates[fixedDate]=rowIndex
                    else:#otherwise save it like normal
                        lineData[datapointOptionList[pointIndex]]=str(point.get_text(strip=True))#type: ignore
                #save what we extracted
                dataList.append(lineData)
    else:
        raise Exception("error, invalid table")
    

    easyCLI.fastPrint("done.\n")
    
    
    #return the data we extracted
    return {"name":str(retrievedData[0]),"data":dataList,"dates":dates}






def parseDataSets(rawDataList,sortAlphabetical):
    easyCLI.fastPrint("starting dataset parsing...\n")

    parsedData:list[dict]=[parseDataSet(dataSet) for dataSet in rawDataList]
    
    #if alphibetical sorting mode is on
    if(sortAlphabetical):
        parsedData=sorted(parsedData, key=lambda dataSet: dataSet["name"])
    
    easyCLI.fastPrint("parsing complete.\n\n")
    return parsedData






def loadLinks() -> tuple[list[str],bool] | bool:
    print("loading target stocks...")
    #create a dictionary for our link config and load its location string
    global linkConfigFile
    jsonDict:dict=dict()
    #create our template
    template={
        "links":["put historical data links here"],"sort alphabetical":"set to true if you want your stocks sorted aphibetically"
    }
    #if we cant find the list, save our template in its place, then exit
    if(not os.path.exists(linkConfigFile)):
        easyCLI.clear()
        easyCLI.uiHeader()
        print("no yahoo finance historical data page link file found!")
        print("now generating template file...")
        with open(linkConfigFile,"w") as config:
            json.dump(template,config)
        print("successful.\n\n")
        print("please enter your historical data links into the \""+linkConfigFile+"\" then restart the program to download data.\n\n")
        input("press enter to finish")
        return False
    

    #load the links file
    with open(linkConfigFile) as config:
        jsonDict=json.load(config)

    #create a list for our links
    links:list[str]=[]

    #validation step
    try:
        links=jsonDict.get("links")#type:ignore
        #check if the template is found
        if(len(links)==1):
            if(links[0]=="put historical data links here"):
                #if so, print a message then exit
                easyCLI.clear()
                easyCLI.uiHeader()
                print("found link file is the template file!")
                print("please enter your historical data links into the \""+linkConfigFile+"\" then restart the program to download data.\n\n")
                input("press enter to finish")
                return False

    
    except Exception:
        raise Exception("config error: config links list corrupted or not found")

    #make a variable for the sorting variable 
    shouldSort=False
    #do error detection
    try:
        #save our should sort value
        shouldSort=jsonDict.get("sort alphabetical")
    except:
        raise Exception("config error: config links sort value corrupted or not found")
    #more error detection
    if(type(links)!=list):
        raise Exception("config error: config links list corrupted or not found")
    if(type(shouldSort)!=bool):
        raise Exception("config error: config sort value corrupted or not found")

    #some link shenanagins to grav the data for the current date
    endID="period2="
    #loop through the links
    for link in range(len(links)):
        if(type(links[link])!=str):#check if the link actually exists
            raise Exception("link error: non string link found")
        #look for the part we are interested in
        idpos=links[link].find(endID)
        #if we find it, overwrite the old unix time value with the current one
        if(idpos!=-1):
            links[link]=links[link][0:idpos+len(endID)]+str(int(time.time()))
    
    print("done.\n\n")
    return (links,shouldSort)






def loadCommands():
    print("loading commands...")
    #create our main varaibles
    global commandFile
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
    if(not os.path.exists(commandFile)):
        #save our template in its place then exit
        easyCLI.clear()
        easyCLI.uiHeader()
        print("no command file found!")
        print("now generating template file...")
        with open(commandFile,"w") as config:
            json.dump(template,config)
        print("successful.\n\n")
        print("please enter your commands into the \""+commandFile+"\" then restart the program to download data.\n\n")
        input("press enter to finish")
        return False
    

    #load our file 
    with open(commandFile,"r") as config:
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
                                easyCLI.clear()
                                easyCLI.uiHeader()
                                print("found command file is the template file!")
                                print("please enter your commands into the \""+commandFile+"\" then restart the program to download data.\n\n")
                                input("press enter to finish")
                                return False

    except Exception:
        raise Exception("config error: config command list corrupted or not found")


    #safety check
    if(type(commandList)!=list):
        raise Exception("config error: config command list corrupted or not found")
    print("done.\n")
    return commandList





        
def findLine(dataset:dict,date:str)->dict|bool:
    #use our date and dataset values smarktly to find the exact line we want then return it
    #grab our dates dict
    lookup:dict=dataset["dates"]
    #brab the dataList index for this date
    rawIndex=lookup.get(date)
    #if that date doesnt exist, send back that information
    if(rawIndex is None):
        return False
    index:int=rawIndex
    #otherwise grab the dataset
    dataList:list=dataset["data"]
    #and extract the index of that line from it
    line=dataList[index]
    return line


def compareDates(date1:str,date2:str):
    
    #2 is date1 is bigger
    #1 is date1 is smaller
    #0 is both dates are the same

    #self explanitory logic, create date objects for the two dates
    date1obj= datetime.datetime.strptime(date1, "%m/%d/%Y")
    
    date2obj=datetime.datetime.strptime(date2, "%m/%d/%Y")

    #then compare them and return the result
    if(date1obj > date2obj):
        return 2
    elif(date1obj < date2obj):
        return 1
    elif(date1obj == date2obj):
        return 0 
    else: 
        raise Exception("date comparison error, no comaprison case hit")
        
    
    



def findDateInsertionPoint(date:str,dates:list[str]):
    #very self explanitory


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

    #go through and make every list that long if it isnt already
    for subList in listSet:
        #if it isnt long enough
        if(len(subList)<maxLen):
            #calculate how much longer it needs to be
            neededSpace=maxLen-len(subList)
            #and extend it with an empty list of that length
            subList.extend([None]*neededSpace)
    
    




#make sure all categories exist
def updatecategories(newcategories:list, oldCategories:list, values:list[list])->tuple[bool,dict]:
    #lookup table of the catigories and their orders
    categoryList={"date":0,"open":1,"high":2,"low":3,"close":4,"adj close":5,"volume":6}
    (categoriesUpdated)=False
    #loop through the catigories we are adding
    oldCategoriesSet=set(oldCategories)
    for cat in newcategories:
        #if this is valid
        if((not(cat in categoryList)) or cat=="date"):
            raise Exception("command error, provided category: "+str(cat)+" is not a valid category\n valid categories "+", ".join(categoryList))
        
            #if we dont need to ignore this one
        elif(not(cat in oldCategoriesSet)):
            (categoriesUpdated)=True
            #find where in the vategory list it is supposed to go
            newPos:int=categoryList[cat]
            oldCategoriesSet.add(cat)
            #go through all currently existing categories
            for existing in range(len(oldCategories)):
                #find where in the master category list the old one is
                existingPos:int=categoryList[oldCategories[existing]]
                #if the new catigory must go behind the one at index zero
                if((existing==0)and(newPos<existingPos)):
                    #insert it there and give it an empty list
                    oldCategories.insert(existing,cat)
                    values.insert(existing,[])
                    break
                    #if the new catigory must after the end of the one at index zero
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
                
    
    
    if((categoriesUpdated)):
        newDict={}
        builderList=[(catagory,index) for index, catagory in enumerate(oldCategories)]
        newDict.update(builderList)
        return (True,newDict)
    
    return (False,None)#type: ignore
                    


                    
                        




def insertValue(date:str, value:str, category:str, categoryLookupDict:dict, values:list[list]):
    #find where to insert it and make sure that all hte catigory lists are equal size
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
        for collumn in range(len(values)):
            values[collumn].insert(point[1],None)
        #write its date
        values[0][point[1]]=date
        #write the data
        values[categoryIndex][point[1]]=value
    #if it is going after the end
    elif(point[0]==2):
        #make a spot for it at the end
        for collumn in range(len(values)):
            values[collumn].append(None)
        #write its date
        values[0][len(values[0])-1]=date
        #then write its value
        values[categoryIndex][len(values[0])-1]=value

    

        
        
        
        
def generateDateRange(startDate:str,endDate:str):
    #make sure we are generating in ascending order, and if currently not, correct it so that we are
    order=compareDates(startDate,endDate)
    if(order==0):
        return [startDate]
    elif(order==1):
        start=startDate
        end=endDate
    else:
        start=endDate
        end=startDate
    #create a list to store every date in the range, inclusive
    dateRange=[]
    #create our end and index value, and set index to start
    endDateObject= datetime.datetime.strptime(end, "%m/%d/%Y")
    current=datetime.datetime.strptime(start, "%m/%d/%Y")
    #loop through every date in between, including the start and end, and add that date to the list
    while current <= endDateObject:
        #compact the current date into a string in our format
        dateRange.append("/".join((str(current.month),str(current.day),str(current.year))))
        #incriment the day
        current = current + timedelta(days=1)
    return dateRange

    

    
def validateCommands(commands:list[dict]):
    easyCLI.fastPrint("validating commands...\n")
    validCommands=set(["specific dates","all data","date range"])
    validattributes=set(["date","open","high","low","close","adj close","volume"])
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


        attributes=command.get("attributes")
        if(attributes is None):
            raise Exception("command error: command "+str(commandNumber+1)+" has no attributes value or no key value")
        elif(type(attributes)!=list):
            raise Exception("command error: command "+str(commandNumber+1)+" has an invalid attributes value")
        for attributeIndex, attribute in enumerate(attributes):
            if((type(attribute)!=str) or (not(attribute in validattributes))):
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




def executeCommand(stock:dict,dates:list[str],attributes:list[str],catagoryLookupDict:dict[str,int],values:list[list]):
    global skipBuffer
    for date in dates:
        #find the line for this date
        rawLine=findLine(stock,date)
        #if it doesnt exist, skip it
        if(rawLine==False):
            easyCLI.fastPrint("\nno data for date: "+str(date))
            easyCLI.fastPrint("skipping...\n")
        elif(type(rawLine)==dict):
            line:dict=rawLine
            #otherwise, loop through all the attributes the command wants
            for attribute in attributes:
                #and grab their values for the line, then write them to the buffer for this stock
                insertValue(date,line.get(attribute),attribute,catagoryLookupDict,values)#type: ignore




def processStocks(commands:list[dict],stocks:list[dict]):
    easyCLI.fastPrint("executing commands...\n")
    #need to update the month reformat logic
    buffer=[]
    #if we have something to do
    if(len(commands)>0):
        
        
        #loop through our stocks
        for stockNumber, stock in enumerate(stocks):
            #extract name and create a list for the catagories, and a 2d list for the values
            name=stock.get("name")
            categories=["date"]
            catagoryLookupDict:dict[str,int]={"date":0}
            values:list[list]=[[]]
            stockDates:dict=stock["dates"]
            #create a variable for our progress through this stock
            
            #loop thorugh our commands
            for commandNumber, command in enumerate(commands):
                #do tuple and string magic for our cli
                easyCLI.fastPrint("".join(("\nexecuting command ",str(commandNumber+1)," of ",str(len(commands))," on stock ",str(stockNumber+1)," of ",str(len(stocks)))))

                #grab and validate the values we need from the command
                
                action:str=command["command"]
                commandDates:list[str]=command["dates"]
                attributes:list[str]=command["attributes"]
                #make sure the lists have the attributes in the command
                possibleNewDict=updatecategories(attributes,categories,values)
                if(possibleNewDict[0]):
                    catagoryLookupDict=possibleNewDict[1]
                #overwrite the old values with the corrected ones
                    

                #self explanitory conditional, we are just checking command ids
                if(action=="specific dates"):
                    executeCommand(stock,commandDates,attributes,catagoryLookupDict,values)

                #check the command id
                elif(action=="all data"):
                    #grab all the dates for this stock
                    dates:list=list(stockDates.keys())
                    
                    executeCommand(stock,dates,attributes,catagoryLookupDict,values)
                    

                #check the command id
                elif(action=="date range"):
                    #generate all the dates for this range
                    dates:list=generateDateRange(commandDates[0],commandDates[1])
                    
                    executeCommand(stock,dates,attributes,catagoryLookupDict,values)


                else:
                    raise Exception("command error, "+str(command)+" is not a valid command")
                

            #convert the dates back to their origonal format (needs to be replaced)
            
            fixedDates=[datetime.datetime.strptime(s, "%m/%d/%Y").strftime("%b %d, %Y") for s in values[0]]
            values[0]=fixedDates
            global skipBuffer
            easyCLI.fastPrintList(skipBuffer)
            skipBuffer=[]
            #save this stock's data as a render object
            renderObj={"name":name,"categories":categories,"values":values}
            #put it in our buffer
            buffer.append(renderObj)
            #incriment our command count
           

    easyCLI.fastPrint("command execution done.\n\n")
    return buffer


                    

                
def outputRenderedResults(displayList:list[dict],outputFileName:str):
    easyCLI.fastPrint("rendering results...")
    #create a buffer
    buffer=[]
    #loop through every render object
    for item in displayList:
        #render the header data
        buffer.append([item.get("name"),])
        buffer.append(item.get("categories"))
        #grab the data
        values=item["values"]
        #loop through the y indexes
        for y in range(len(values[0])):
            #create a varaible for the row
            line=[values[x][y] for x in range(len(item["categories"]))]
            buffer.append(line)
        #write some gaps 
        
        buffer.extend([[None]]*3)
    easyCLI.fastPrint("done.\n")
    #self explanitory, write the buffer to the file
    easyCLI.fastPrint("saving results as \""+outputFileName+"\"...")
    with open(outputFileName, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(buffer)
    easyCLI.fastPrint("save successful.\n\n")
    


class YahooFinanceGrabberHeader(easyCLI.UIHeaderClass):
    #simple header class required by easy cli
    def __init__(self):
        super().__init__(None)

    def drawUIHeader(self):
        easyCLI.clear()
        print("Yahoo Finance Historical Data Downloader v0.5 by redcacus5\n\n")
        


#set the library ui header to the one we just made
easyCLI.setUIHeader(YahooFinanceGrabberHeader())



def licenceScreen():
    #very simple and self explanitory, not even any logic
    easyCLI.clear()
    easyCLI.uiHeader()
    print(easyCLI.multilineStringBuilder(["Copyright and Licensing Information:\n",
    "Yahoo Finance Historical Data Downloader © 2025 redcactus5\n",
    "This program is NOT endorsed by, produced by, or affiliated with Yahoo Incorporated or its parent companies,\n",
    "and was not created with their knowledge, consent, support, or involvement.\n",
    "Yahoo Finance Historical Data Downloader is free software released under the GNU General Public License Version 3 (GPLv3).\n",
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
    
    
    time.sleep(3)
    
    print("press enter to agree to the terms of the licenses and continue")
    input()
    easyCLI.clear()
    


def waitForPrintFinish():
    waiting=True
    while waiting:
        waiting=(not easyCLI.isFastPrintDone())
        print(easyCLI.isFastPrintDone())
        print(easyCLI.easyCliPrivateConfigBackend._PrivateInternalAsyncPrintThreadOBJDoNotEdit._printQueue.qsize())


def main(fileName,links,commands,sortAlphibetical):
    #our main execution funciton, it mostly just stages out our steps
    #clear the screen
    easyCLI.fastClear()
    #write the header
    easyCLI.fastUIHeader()
    easyCLI.fastPrint("starting data retreival process...\n\n")
    #create and start our stopwatch
    timer=easyCLI.Stopwatch()
    timer.start()
    validateCommands(commands)
    #grab the webpages
    webPages=retrieveWebPages(links)
    #extract their raw data
    rawData=retrieveHtmlListTablesAndName(webPages)
    #save ram, free no longer needed values
    webPages=None
    #parse that raw data
    dataSets=parseDataSets(rawData,sortAlphibetical)
    #save ram, free no longer needed values
    rawData=None
    #execute our commands on that parsed data
    displayList=processStocks(commands,dataSets)
    #save ram, free no longer needed values
    dataSets=None
    outputRenderedResults(displayList,fileName)
    #stop the timer
    timer.stop()
    waitForPrintFinish()
    print("data retreival complete!\n")
    print("finished in: "+timer.getUnitDeviatedTimeString()+"\n\n\n")
    input("press enter to finish")





def startup():
    #startup checks and loading of config files
    canStart=True
    commands=None
    rawLinks=loadLinks()
    links:tuple=tuple()
    if(rawLinks==False):
        canStart=False
    elif(type(rawLinks)==tuple):
        links:tuple=rawLinks
        rawLinks=None
    if(canStart):
        commands=loadCommands()
        if(commands==False):
            canStart=False
    #if we can start
    if(canStart):
        licenceScreen()
        #if the user wants to download the data
        if(easyCLI.booleanQuestionScreen("would you like to download the preconfigured market data?",None)):
            #have the menter the file name they want
            fileName=easyCLI.enterFileNameScreen("please enter the name of the output file.\nwarning, if the file already exists, it will be overwritten.","(do not include the file extention)")+".csv"
            #then start the main program
            main(fileName,links[0],commands,links[1])
        #otherwise
        else:
            easyCLI.clear()
            print("well, thanks anyway!")








if(__name__=="__main__"):

    #devious check to make sure no one is doing an illegal thing and distributing without the open source licenses
    if((not os.path.exists("LICENSES/BeautifulSoup-MIT-LICENSE.txt"))or(not os.path.exists("LICENSES/easyCLI-GPL3-LICENSE.txt"))or(not os.path.exists("LICENSES/Nuitka-Apache-2.0-LICENSE.txt"))or(not os.path.exists("LICENSES/Playwright-Apache-2.0-LICENSE.txt"))or(not os.path.exists("LICENSES/Python-PSFL-2-LICENSE.txt"))or(not os.path.exists("LICENSES/WebKit-LGPL-2.0-BSD-License.txt"))or(not os.path.exists("LICENSE.txt"))):
        easyCLI.clear()
        easyCLI.uiHeader()
        print("ERROR: License file(s) not found.")
        print("This program is open source and must be distributed with its licenses.")
        print("Please ensure the LICENSE.txt is present, and the LICENSES directory is \npresent and contains easyCLI-GPL3-LICENSE.txt, BeautifulSoup-MIT-LICENSE.txt, \nNuitka-Apache-2.0-LICENSE.txt, WebKit-LGPL-2.0-BSD-License.txt, and Playwright-Apache-2.0-LICENSE.txt.")
        input("press enter to finish")
    else:
        startup()
        
         
