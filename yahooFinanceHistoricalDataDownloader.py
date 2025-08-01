'''
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 
'''

URLLISTFILE="config/downloadConfig.json"
COMMANDFILE="config/commands.json"
BROWSERPATH="webproxy/firefox.exe"


#warning, this program is held together by duct tape and prayers
#also, the moment yahoo changes their website, this script will no longer work

from bs4 import BeautifulSoup
from bs4 import element
from bs4 import Tag
import json
import playwright.sync_api
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
from datetime import timezone
import base64
import hashlib
#i cant believe I have to use this lib
import gc

def antiSnifferRandomDelay(start,end,message=False)->None:
    #this function looks more complicated than it is
    
    wait=0
    #if start and end are the same, dont try to randomize the integer and add the floating point to it
    if(start==end):
        wait=start+random.random()
    #otherwise do the random range with the random float
    else:
        wait=random.randint(int(start),int(end))+random.random()

    #if its too small add half a second
    if(wait<0.5):
        wait+=0.5
    #if we are supposed to print a waiting message, run the version where we do that
    if(message):
        easyCLI.fastPrint("waiting "+f"{wait:.1f}"+" second anti-antibot delay...")
        time.sleep(wait)
        easyCLI.fastPrint("done.")
    else:#otherwise only sleep
        time.sleep(wait)
        

def shuffle(inputList:list[tuple[str,date]])->tuple[list[tuple[str,date]],list[int]]:
    #make a copy of our input
    copyList=inputList.copy()
    #create a list of indexes
    randomPosList=list(range(len(copyList)))
    #shuffle it
    random.shuffle(randomPosList)
    #put the items in copyList in the shuffled order
    scrambledList = [copyList[i] for i in randomPosList]
    return (scrambledList,randomPosList)


def typeDelay()->None:
    #delay specifically optimized for typing mimicry
    delay=(1/float(random.randint(6,10)+random.random()))
    time.sleep(delay)


def configurePageForLoading(page:playwright.sync_api.Page, startDate:date, downloadStartTimeout:float)->None:
    
    #avoid bot sniffers
    antiSnifferRandomDelay(1,2,True)

    easyCLI.fastPrint("configuring webpage for dataset download...")

    #open the menu we want to use, and wait for it open
    page.click("button.tertiary-btn.fin-size-small.menuBtn.rounded.yf-1epmntv")
    #these are just to add human like random delay
    antiSnifferRandomDelay(1,1)
    

    #click the box we want
    page.click("input[name='startDate']")

    #more waiting to trip up bot sniffers
    antiSnifferRandomDelay(0,1)

    #build our month string in an inefficient and paranoid way
    month=str(startDate.month) 
    if(len(month)==1):
        month="0"+month

    day=str(startDate.day)
    if(len(day)==1):
        day="0"+day

    year=str(startDate.year)
    if(len(year)<4):
        zeros="0"*(4-len(year))
        year=zeros+year
    
    #make voltron, i mean the full date string
    stringedDate=month+day+year

    #go through every character and type it with a delay
    for char in stringedDate:
        page.keyboard.type(char)
        typeDelay()
        

    
    


    doneButton = page.locator("button.primary-btn.fin-size-small.rounded.yf-1epmntv", has_text="Done")
    doneButton.wait_for(state="attached")

    #simulate waiting to click delay
    antiSnifferRandomDelay(1,2)
  
    #error handling and special casing
    errorText="Date shouldn't be prior to"
    section = page.locator("section[slot=\"content\"].container.yf-1th5n0r")

    if(errorText in " ".join(section.all_inner_texts())):
        section=page.locator("section[slot=\"content\"].container.yf-1th5n0r",has_text=errorText)
        text=section.text_content()
        if(type(text)==str):
            errorText=datetime.strptime(text.split("\"")[1],"%b %d, %Y").date().strftime("%m/%d/%Y")
        else:
            raise Exception("error: fatal error, section has no text.")
        
        
        #handle edge case, because the website has an off by one error
        if(datetime.strptime(errorText,"%m/%d/%Y").date()==startDate):
            #if we have this very specific edge case, we basically do the same thing, but click a different button
            #grab said button
            maxButtonLocator=page.locator("button.tertiary-btn", has_text="Max")
            maxButtonLocator.wait_for(state="attached")
            easyCLI.fastPrint("configuration complete.")
            easyCLI.fastPrint("requesting dataset from server...")
            maxButtonLocator.click()
    
        else:
            easyCLI.waitForFastWriterFinish()
            raise Exception("error: start date error, start date for url: "+page.url+" is invalid.\nprovided date: "+startDate.strftime("%m/%d/%Y")+" minimum date: "+errorText)
    else:
        #click the done button if the date is valid
        easyCLI.fastPrint("configuration complete.")
        easyCLI.fastPrint("requesting dataset from server...")
        doneButton.click()
    
    page.wait_for_selector('section[slot="content"].container.yf-1th5n0r', state='hidden',timeout=downloadStartTimeout)
    antiSnifferRandomDelay(1,1)
   



    




def retrieveWebPages(links:list[tuple[str,date]],downloadStartTimeout:float,downloadCompletionTimeout:float,downloadRetryLimit:int)->list[str]:
    #grab our constants
    global BROWSERPATH

    easyCLI.fastPrint("starting webpage retrieval...\n")
    #make a list for what we download
    pages=[""]*len(links)
    #shuffle our links to throw bot detectors off our scent
    scrambled=shuffle(links)
    #one is the shuffled links, the other is lookup table we use to put them back in order
    links=scrambled[0]#type: ignore
    ogPos=scrambled[1]

    #the print statements explain most of it
    with playwright.sync_api.sync_playwright() as p:
        desktopUserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        easyCLI.fastPrint("launching retriever proxy...")
        browser=None
        context=None
        page=None
        try:
            #launch firefox, so we can client side render scrape. fucking web 2.0. also do it headless so we dont have windows pooping up scaring people
            browser = p.firefox.launch(executable_path=BROWSERPATH,headless=True)
            #the user agent we are spoofing
            context=browser.new_context(user_agent=desktopUserAgent,viewport={'width': 1920, 'height': 1080},device_scale_factor=1,is_mobile=False)
            easyCLI.fastPrint("done.\n")

            
            
            #precalculate how long the url list is for speed
            lenString=str(len(links))
            #loop through all our links
            for urlIndex, url in enumerate(links):
                #keep track of retries
                tryCount=1
                #retry loop
                while(True):
                    easyCLI.fastPrint("dataset "+str(urlIndex+1)+" of "+lenString)
                    #make a new tab
                    page = context.new_page()
                    
                    #catch errors
                    try:
                        easyCLI.fastPrint("requesting source webpage from server...")
                        #request the page from the server
                        response=page.goto(url[0],wait_until="domcontentloaded",timeout=downloadStartTimeout)

                        #handle common errors
                        if(isinstance(response,playwright.sync_api.Response)):
                            if(response.url=="https://finance.yahoo.com/?err=404"):
                                raise Exception("error: the requested page \""+str(url)+"\" was unable to be retrieved from the answering server.")
                            elif(response.status==404):
                                raise Exception("error: network error 404, webpage \""+str(url)+"\" not found, check your connection.")
                            elif(response.status==500):
                                raise Exception("error: requesting \""+str(url)+"\" returned network error 500, internal server error.")
                            #if we get here the request was successful
                        elif(response is None):
                            raise Exception("error: network request for page \""+str(url)+"\" returned no response.")
                        else:
                            raise Exception("error: catastrophic internal program error for \""+str(url)+"\" during download process.")
                        
                        #run the configure script
                        configurePageForLoading(page,url[1],downloadStartTimeout)


                        easyCLI.fastPrint("downloading dataset...")

                        
                        #basically a bunch of checks to make sure we are fully loaded before saving our data
                        #wait for the table to load
                        page.wait_for_selector("table.table.yf-1jecxey",timeout=downloadCompletionTimeout)
                        #wait for the title to load
                        page.wait_for_selector("h1.yf-4vbjci",timeout=downloadCompletionTimeout)
                        #wait for the table to load its data
                        page.wait_for_selector("td.yf-1jecxey loading",timeout=downloadCompletionTimeout, state="detached")
                        page.wait_for_selector("td.yf-1jecxey .loading",timeout=downloadCompletionTimeout, state="detached")
                        page.wait_for_selector("td.yf-1jecxey",timeout=downloadCompletionTimeout)
                        
                        
                        #wait extra time just to be safe, the only reason we aren't using the dedicated function is because 
                        #of the custom message
                        wait=1+random.randint(0,1)+random.random()
                        easyCLI.fastPrint("waiting "+f"{wait:.1f}"+" seconds for download completion...")
                        time.sleep(wait)
                        easyCLI.fastPrint("saving data...")

                        content = page.content()  # get rendered HTML
                        #reverse the scrambling to put the data in the correct order
                        pages[ogPos[urlIndex]]=content#type: ignore


                        easyCLI.fastPrint("cleaning up...")
                        page.close()


                        easyCLI.fastPrint("page download complete.")

                        antiSnifferRandomDelay(0,3,True)
                        easyCLI.fastln()

                        break

                    #detect the page randomly not loading, clean up, and try again
                    except PlaywrightTimeoutError:
                        #cleanup the fail
                        page.close()
                        tryCount+=1
                        if(tryCount>downloadRetryLimit):#if we go past our retry limit, give up
                            easyCLI.waitForFastWriterFinish()
                            raise Exception("download error: retry limit exceeded for url: "+str(links[urlIndex]))
                        easyCLI.fastPrint("\ndownload timed out.")
                        easyCLI.fastPrint("retrying...\n")
                        easyCLI.fastPrint("starting attempt "+str(tryCount)+"...")


            
            easyCLI.fastPrint("cleaning up retriever proxy...")
            context.close()
            browser.close()

            easyCLI.fastPrint("done.\n")
        #if there is an error first close the browser then crash, so we dont leave resources running
        except Exception as E:
            if(not(page is None)):
                page.close()
            if(not(context is None)):
                context.close()
            if(not(browser is None)):
                browser.close()
            easyCLI.waitForFastWriterFinish()
            raise(E)
        
        except KeyboardInterrupt as E:
            if(not(page is None)):
                page.close()
            if(not(context is None)):
                context.close()
            if(not(browser is None)):
                browser.close()
            easyCLI.waitForFastWriterFinish()
            raise(E)


    
  
    easyCLI.fastPrint("all page retrievals complete.\n\n")
    return pages






def retrieveTableAndName(htmlText)->tuple[str,Tag]:
    
    #create a beautiful soup object for this raw page so we can parse it
    scraper=BeautifulSoup(htmlText, "lxml")

    
    #find the name
    name=scraper.find("h1",class_="yf-4vbjci")
    
    if(name is None):
        easyCLI.waitForFastWriterFinish()
        raise Exception("error: no stock name found in page.")
    
    name=str(name.get_text())

    #find the table in the page
    table=scraper.find("table")
    

    if(table is None):
        easyCLI.waitForFastWriterFinish()
        raise Exception("error: no tables found in page.")
    
    if(isinstance(table,Tag)):
        return (name,table)
    else:
        easyCLI.waitForFastWriterFinish()
        raise Exception("error: table in page is corrupted.")


def retrieveHtmlListTablesAndName(htmlDataList:list[str])->list[tuple[str,Tag]]:
 
    rawDataList:list[tuple[str,Tag]]=[("",Tag(name="dummy"))]*len(htmlDataList)
    easyCLI.fastPrint("extracting relevant data...\n")
    
    for pageNumber, page in enumerate(htmlDataList):
        easyCLI.fastPrint("extracting dataset "+str(pageNumber+1)+" of "+str(len(htmlDataList))+"...")
        rawDataList[pageNumber]=retrieveTableAndName(page)
        
    easyCLI.fastPrint("done.\n\n")
    return rawDataList



def parseDataSet(retrievedData)->dict:
    easyCLI.fastPrint("parsing data for "+str(retrievedData[0])+"...")

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
        easyCLI.waitForFastWriterFinish()
        raise Exception("error: data table is empty.")
    

    #validate to make sure the table is actually the one we want. if it fails, yahoo changed their website, or the link was wrong
    ValidatorRowStrings=["Date","Open","High","Low","Close","Adj Close","Volume"]
    #a nice set of lookup tables we need
    
    
    
    headerRow=rows[0].find_all("th")#type: ignore
    

    if((len(headerRow)>0) and all((datapoint.get_text(strip=True).strip() == ValidatorRowStrings[index]) for index, datapoint in enumerate(headerRow))):
        #if this is what we want
        rows.pop(0)
        ValidatorRowStringsLen=len(ValidatorRowStrings)
        
        #because we dont add some rows, we use this variable to avoid desync. I tried using an index counter, but we desync when we skip an index.
        rowCount=0
        #go through every row
        for row in rows:
            
            #extract the cells
            rowData:list[Tag]=row.find_all("td")#type: ignore
            #if this is a row we aren't supposed to ignore
            
            if(len(rowData)==ValidatorRowStringsLen):

                lineData={}
                #go through its columns
                for pointIndex, point in enumerate(rowData):
                    #if this is the date index
                    if(pointIndex==0):#do the special case for saving date
                        parsedDate = datetime.strptime(point.get_text(strip=True), "%b %d, %Y").date()

                        dates[parsedDate]=rowCount
                    else:#otherwise save it like normal
                        lineData[pointIndex]=str(point.get_text(strip=True))

                #save what we extracted
                dataList.append(lineData)
                #increment rowcount since we found a row
                rowCount+=1
    else:
        easyCLI.waitForFastWriterFinish()
        raise Exception("error: invalid data table.")
    

    easyCLI.fastPrint("done.\n")
    

    #return the data we extracted
    return {"name":str(retrievedData[0]),"data":dataList,"dates":dates}






def parseDataSets(rawDataList,sortAlphabetical)->list[dict]:
    easyCLI.fastPrint("starting dataset parsing...\n")

    parsedData:list[dict]=[parseDataSet(dataSet) for dataSet in rawDataList]
    
    #if alphabetical sorting mode is on
    if(sortAlphabetical):
        parsedData=sorted(parsedData, key=lambda dataSet: dataSet["name"])
    
    easyCLI.fastPrint("parsing complete.\n\n")
    return parsedData






def loadLinks() -> tuple[list[tuple[str,date]],bool,float,float,int] | bool:

    #create a dictionary for our link config and load its location string
    global URLLISTFILE
    jsonDict:dict=dict()
    #create our template
    template={
        "URLs":["put historical data links here. if you want data from a date, make sure it is included in the page you link. this can be done by changing the starting date in yahoo finance before copying the link."],
        "sort alphabetical":"set to true if you want your stocks sorted alphabetically.",
        "page load begin timeout":"put the time in seconds you want to give the page to start loading here (a value of zero means no timeout).",
        "page load completion timeout":"put the time in seconds you want to give the retrieval to complete here (used for all 6 completion checks) (a value of zero means no timeout).",
        "download retry limit":"put the number of download retry attempts you want to allow here."
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
        input("press enter to finish.")
        return False
    

    #load the links file
    with open(URLLISTFILE) as config:
        jsonDict=json.load(config)

    #create the variables we will put what we load into
    links:list[str]=[]
    shouldSort=False
    startTimeout=-1
    endTimeout=-1
    retryLimit=-1

    #validation steps and loading. that literally is everything this massive block of try catches does
    try:
        links=jsonDict.get("URLs")#type:ignore
    except Exception:
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: downloadConfig \"URLs\" list corrupted or not found.")

    try:
        shouldSort=jsonDict.get("sort alphabetical")
    except:
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: downloadConfig \"should sort\" value corrupted or not found.")
    
    try:
        #save our start timeout value
        startTimeout=jsonDict.get("page load begin timeout")
    except:
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: downloadConfig \"page load begin timeout\" value corrupted or not found.")


    try:
        endTimeout=jsonDict.get("page load completion timeout")
    except:
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: downloadConfig \"page load completion timeout\" value corrupted or not found.")


    try:
        retryLimit=jsonDict.get("download retry limit")
    except:
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: downloadConfig \"download retry limit\" value corrupted or not found.")

    

    #more error detection
    if(not isinstance(links,list)):
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: config \"URLs\" list corrupted or not found.")
    elif(len(links)==0):
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: config \"URLs\" list is empty!")
    

    #check if the template is found
    if(len(links)==1):
        if(links[0]=="put historical data links here. if you want data from a date, make sure it is included in the page you link. this can be done by changing the starting date in yahoo finance before copying the link."):
            if(shouldSort=="set to true if you want your stocks sorted alphabetically."):
                if(startTimeout=="put the time in seconds you want to give the page to start loading here (a value of zero means no timeout)."):
                    if(endTimeout=="put the time in seconds you want to give the retrieval to complete here (used for all 6 completion checks) (a value of zero means no timeout)."):
                        if(retryLimit=="put the number of download retry attempts you want to allow here."):
                            easyCLI.waitForFastWriterFinish()
                            #if so, print a message then exit
                            easyCLI.uiHeader()
                            print("found link file is the template file!")
                            print("please enter your historical data links into the \""+URLLISTFILE+"\" then restart the program to download data.\n\n")
                            input("press enter to finish.")
                            return False


    #finish our error detection:
    if(not isinstance(shouldSort,bool)):
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: config \"should sort\" value corrupted or not found.")
    elif(not isinstance(startTimeout,(float,int))):
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: config \"page load begin timeout\" value corrupted or not found.")
    elif(isinstance(startTimeout,(float,int))and(startTimeout<0)):
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: config \"page load begin timeout\" value must be 0 or greater!")
    elif(not isinstance(endTimeout,(float,int))):
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: config \"page load completion timeout\" value corrupted or not found.")
    elif(isinstance(endTimeout,(float,int))and(endTimeout<0)):
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: config \"page load completion timeout\" value must be 0 or greater!")
    elif((not isinstance(retryLimit,int))):
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: config \"download retry limit\" value corrupted or not found.")
    elif(isinstance(retryLimit,float)):
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: \"download retry limit\" value must be an integer!")
    elif(isinstance(retryLimit,int)and(retryLimit<0)):
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: \"download retry limit\" value must be 0 or greater!")
    else:
        #all safety checks passed, convert the timeouts to millisecond format
        startTimeout=float(startTimeout*1000)
        endTimeout=float(endTimeout*1000)


    newLinks=[]


    endID="/history/"
    unixStartID="period1="
    unixEpoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

    #ok, here we are just parsing the provided urls to extract the base url, and if there, the start date. 
    # we do this becuase yahoo finance is finicky about direct access, so we have to access a base url we 
    # know it is ok with direct access to, then navigate to where we want from there. i know, its a pain.
    for linkIndex, link in enumerate(links):

        if(type(link)!=str):#check if the link actually exists
            easyCLI.waitForFastWriterFinish()
            raise Exception("URL error: non string URL found. provided url: "+str(link))
        
        #look for the end of the base url
        idPos=link.find(endID)
        #if we dont find it, panic
        if(idPos==-1):
            raise Exception("config error: invalid or corrupted url found. the url "+link+" is not a yahoo finance historical data page. \nthe url must be for a yahoo finance historical data page.")
            
        else:
            #calculate the actual end of the base url
            trueLinkEndIndex=idPos+(len(endID)-1)
            #extract the base url
            trueLink=link[0:trueLinkEndIndex]
            #find the start date unix timecode in the link
            startUnixIndex=link.find(unixStartID)

            #if it is there
            if(startUnixIndex!=-1):
                #calculate the start of it
                trueStartUnixIndex=startUnixIndex+len(unixStartID)
                #isolate it from everything before there
                importantPart=link[trueStartUnixIndex:]
                #find the character we know delimits the end
                endIndex=importantPart.find("&")
                #if we find dont find the end, panic
                if(endIndex==-1):
                    raise Exception("config error: invalid or corrupted url found. the url "+link+" is not a yahoo finance historical data page. \nthe url must be for a yahoo finance historical data page.")
                
                stringUnixStartTime=importantPart[0:endIndex]
                unixStartTime=-1
                #otherwise extract the timecode and integer cast it
                try:
                    unixStartTime=int(stringUnixStartTime)
                except:
                    raise Exception("config error: config error: invalid or corrupted url found. the url "+link+" has a non numeric start date value.")
                try:
                    #convert that timecode to a date
                    startDate=(unixEpoch+timedelta(seconds=unixStartTime)).date()
                    #append the stuff we extracted to the newlinks list (not to be confused with a linked list)
                    newLinks.append((trueLink,startDate))
                except:
                    raise Exception("config error: config error: invalid or corrupted url found. the url "+link+" has a corrupted start date value.")



            else:
                #if there is no unix time code, alert the user
                easyCLI.fastPrint("no start date found for: "+link+" using default of one year.")
                #get the current date, subtract a year from it, then convert it to a date object
                startDate=(datetime.now()-timedelta(days=365)).date()
                #append the base url and the start date we made to newlinks as a tuple
                newLinks.append((trueLink,startDate))


            
    

    return (newLinks,shouldSort,startTimeout,endTimeout,retryLimit)






def loadCommands()->list[dict]|bool:

    #create our main variables
    global COMMANDFILE
    jsonDict:dict=dict()
    #create our template
    template={
            "commands":[
                {
                    "command":"set this to either specific dates, date range, or all data",
                    "attributes":["put attributes you want here(the attributes are the categories at the top of the table on the webpage.)"],
                    "dates":["put dates here. how they are used depends on the command, all data ignores this, date range uses it for the start and stop dates (only one pair per command supported for that), and specific dates only retrieves the dates listed here."]
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
        input("press enter to finish.")
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
                    if(commandList[0].get("attributes")[0]=="put attributes you want here(the attributes are the categories at the top of the table on the webpage.)"):#type: ignore
                        if(len(commandList[0].get("dates"))==1):#type: ignore
                            if(commandList[0].get("dates")[0]=="put dates here. how they are used depends on the command, all data ignores this, date range uses it for the start and stop dates (only one pair per command supported for that), and specific dates only retrieves the dates listed here."):#type: ignore
                                #if it is, print a message then exit
                                easyCLI.waitForFastWriterFinish()
                                easyCLI.uiHeader()
                                print("found command file is the template file!")
                                print("please enter your commands into the \""+COMMANDFILE+"\" then restart the program to download data.\n\n")
                                input("press enter to finish.")
                                return False

    except Exception:
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: config command list corrupted or not found.")


    #safety check
    if(type(commandList)!=list):
        easyCLI.waitForFastWriterFinish()
        raise Exception("config error: config command list corrupted or not found.")
    
    
            
                
                
                

    return commandList





        
def findLine(dataset:list,datasetDates:dict,date:date)->dict|bool:
    #use our date and dataset values smartly to find the exact line we want then return it
    
    
    #grab the dataList index for this date
    rawIndex=datasetDates.get(date)
    #if that date doesn't exist, send back that information
    if(rawIndex is None):
        return False
    
    #and extract the index of that line from it
    line=dataset[rawIndex]

    return line

    
    
    



def findDateInsertionPoint(date:date,dates:list[date])->tuple[int,int|bool]:
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

        
    easyCLI.waitForFastWriterFinish()
    raise Exception("error: insertion point search failure, no insertion point found.")




def equalizeListLens(listSet:list[list])->None:
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
    


#make sure all categories exist
def updateCategories(newCategories:list, oldCategories:list, values:list[list])->tuple[bool,dict|None]:
    
    #categoryLookupList={0:"date",1:"open",2:"high",3:"low",4:"close",5:"adj close",6:"volume"}
    #master category list 
    categoryListSet=set(range(7))
    
    categoriesUpdated=False
    
    oldCategoriesSet=set(oldCategories)

    #loop through the categories we are adding
    for cat in newCategories:
        #if this is valid
        if((not(cat in categoryListSet)) or cat==0):
            categoryStringList=["date","open","high","low","close","adj close","volume"]
            easyCLI.waitForFastWriterFinish()
            raise Exception("command error, provided category: "+str(cat)+" is not a valid category\n valid categories "+", ".join(categoryStringList),".")
        
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
    
    return (False,None)
                    


                    
                        




def insertValue(date:date, value:str, category:str, categoryLookupDict:dict, values:list[list])->None:
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
        easyCLI.waitForFastWriterFinish()
        raise Exception("error: value insertion failed, no insertion point found.")


    

        
        
        
        
def generateDateRange(startDate:date,endDate:date)->list[date]:
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
        easyCLI.waitForFastWriterFinish()
        raise Exception("error: date comparison failure, no comparison case hit.")
    #paranoid safety check
    if((start is None)or(end is None)):
        easyCLI.waitForFastWriterFinish()
        raise Exception("error: date range generation failure, internal start and end values corrupted.")
    
    #create a list to store every date in the range, inclusive
    dateRange:list[date]=[]
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
    easyCLI.fastPrint("compiling commands...\n")
    #cache this for later
    rawCommandLen=len(rawCommands)

    #preallocate while shutting up linter
    compiledCommands:Any=[None]*rawCommandLen

    #lookup tables
    masterCategoryList={"date":0,"open":1,"high":2,"low":3,"close":4,"adj close":5,"volume":6}
    commandIDTable={"specific dates":0,"all data":1,"date range":2}


    for commandNumber, command in enumerate(rawCommands):
        easyCLI.fastPrint("".join(("compiling command ",str(commandNumber+1)," of ",str(rawCommandLen),"...")))
        #convert the dates to date objects
        dateList:list[str]=command["dates"]
        newDateList=[]
        if(len(dateList)>0): 
            newDateList=[datetime.strptime(date, "%m/%d/%Y").date() for date in dateList]
            

        commandID=commandIDTable[command["command"]]

        categoryList=command["attributes"]
        newCategoryList=[masterCategoryList[category] for category in categoryList]
        compiledCommands[commandNumber]=(commandID,newCategoryList,newDateList)
        easyCLI.fastPrint("done.\n")


    
    easyCLI.fastPrint("compilation successful.\n")
    
    
    return compiledCommands

        
        

        

   
def validateCommands(commands:list[dict])->bool:
    easyCLI.fastPrint("validating commands...\n")

    validCommands=set(["specific dates","all data","date range"])
    validAttributes=set(["date","open","high","low","close","adj close","volume"])


    for commandNumber, command in enumerate(commands):
        easyCLI.fastPrint("validating command "+str(commandNumber+1)+" of "+str(len(commands))+"...")
        commandDates=command.get("dates")
        if(commandDates is None):
            easyCLI.waitForFastWriterFinish()
            raise Exception("error: invalid command, command "+str(commandNumber+1)+" has no dates value or key value.")
        elif(type(commandDates)!=list):
            easyCLI.waitForFastWriterFinish()
            raise Exception("error: invalid command, command "+str(commandNumber+1)+" has an invalid dates value.")
        for dateIndex, date in enumerate(commandDates):
            if(type(date)!=str):
                easyCLI.waitForFastWriterFinish()
                raise Exception("error: invalid command, date "+str(dateIndex)+" has an invalid value of: "+str(date)+" with a type of "+str(type(date))+".")


        attributes=command.get("attributes")
        if(attributes is None):
            easyCLI.waitForFastWriterFinish()
            raise Exception("error: invalid command, command "+str(commandNumber+1)+" has no attributes value or no key value.")
        elif(type(attributes)!=list):
            easyCLI.waitForFastWriterFinish()
            raise Exception("error: invalid command, command "+str(commandNumber+1)+" has an invalid attributes value.")
        for attributeIndex, attribute in enumerate(attributes):
            if((type(attribute)!=str) or (not(attribute in validAttributes))):
                easyCLI.waitForFastWriterFinish()
                raise Exception("error: invalid command, attribute "+str(attributeIndex)+" has an invalid value of: "+str(attribute)+" with a type of "+str(type(attribute))+".")

        
        parseCommand=command.get("command")
        if(parseCommand is None):
            easyCLI.waitForFastWriterFinish()
            raise Exception("error: invalid command, command "+str(commandNumber+1)+" has no command value or no key value.")
        elif(type(parseCommand)!=str):
            easyCLI.waitForFastWriterFinish()
            raise Exception("error: invalid command, "+str(commandNumber+1)+" has an invalid command value.")
        elif(not (parseCommand in validCommands)):
            easyCLI.waitForFastWriterFinish()
            raise Exception("error: invalid command, has an invalid value of: "+str(parseCommand)+" with a type of "+str(type(parseCommand))+".")
        easyCLI.fastPrint("done.\n")
    easyCLI.fastPrint("validation complete.\n\n")


    return True




def executeCommand(stockData:list,stockDates:dict,dates:list[date],attributes:list[int],categoryLookupDict:dict[int,int],values:list[list])->None:
   
    for date in dates:
        #find the line for this date
        rawLine=findLine(stockData,stockDates,date)
        #if it doesn't exist, skip it
        if(rawLine is False):
            easyCLI.fastPrint("\nno data for date: "+date.strftime("%m/%d/%Y"))
            easyCLI.fastPrint("skipping...\n")
        elif(type(rawLine)==dict):
            line:dict=rawLine
            #otherwise, loop through all the attributes the command wants
            for attribute in attributes:
                #and grab their values for the line, then write them to the buffer for this stock
                insertValue(date,line.get(attribute),attribute,categoryLookupDict,values)#type: ignore




def processStocks(commands:list[tuple],stocks:list[dict])->list[dict]:
    easyCLI.fastPrint("executing commands...")

    buffer=[dict()]*len(stocks)
    
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
        stockListLen=str(len(stocks))
        commandsListLen=str(len(commands))
        #loop through our stocks
        for stockNumber, stock in enumerate(stocks):
            #extract name and create a list for the categories, and a 2d list for the values
            easyCLI.fastPrint("".join(("\nprocessing stock: \"",str(stock.get("name")),"\" (stock ",str(stockNumber+1)," of ",stockListLen,")...")))
            name=str(stock.get("name"))
            categories=[0]
            categoryLookupDict:dict[int,int]={0:0}
            values:list[list]=[[]]
            stockDates:dict=stock["dates"]
            stockData:list=stock["data"]
            #create a variable for our progress through this stock
            
            #loop through our commands
            for commandNumber, command in enumerate(commands):
                #do tuple and string magic for our cli
                easyCLI.fastPrint("".join(("\nexecuting command ",str(commandNumber+1)," of ",commandsListLen,"...")))

                #grab and validate the values we need from the command
                
                action:int=command[0]
                commandDates:list[date]=command[2]
                attributes:list[int]=command[1]
                #make sure the lists have the attributes in the command
                possibleNewDict=updateCategories(attributes,categories,values)
                if(possibleNewDict[0] and (not(possibleNewDict[1] is None))):
                    categoryLookupDict=possibleNewDict[1]
                #overwrite the old values with the corrected ones

                #0:specific dates
                #1:all data
                #2:date range
                #use our dispatcher to generate our dates list
                dates = dateDispatcher[action](stockDates, commandDates)
                #then execute the command
                executeCommand(stockData,stockDates,dates,attributes,categoryLookupDict,values)
               

            #convert the dates back to their original format
            fixedDates=[datetime.strftime(date,"%b %d, %Y") for date in values[0]]
            values[0]=fixedDates
            
            
            
            #save this stock's data as a render object
            renderObj={"name":name,"categories":categories,"values":values}
            #put it in our buffer
            buffer[stockNumber]=renderObj
            easyCLI.fastPrint("processing done.\n")
           

    easyCLI.fastPrint("command execution complete.\n\n")
    return buffer


                    

                
def outputRenderedResults(displayList:list[dict],outputFileName:str)->None:
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
        self.vNumber="v1.1.1"
        self.vString="Yahoo Finance Historical Data Downloader "+self.vNumber+" by redcacus5"+"\n\n"

    def drawUIHeader(self):
        easyCLI.clear()
        print(self.vString)
        





def licenseScreen()->None:
    #very simple and self explanatory, not even any logic
    easyCLI.uiHeader()
    print(easyCLI.multilineStringBuilder(["Copyright and Licensing Information:\n",
    "Yahoo Finance Historical Data Downloader © 2025 redcactus5\n",
    "This program is NOT endorsed by, produced by, or affiliated with Yahoo Incorporated, its parent companies,",
    "or its subsidiaries, and was not created with their knowledge, consent, support, or involvement, in any way.\n",
    "Yahoo Finance Historical Data Downloader is free software released under the GNU General Public License,",
    "Version 3 (GPLv3).\n",
    "Powered by:",
    " - Python © 2001-2025 Python Software Foundation",
    " - easyCLI © 2025 redcactus5",
    " - BeautifulSoup © 2025 Leonard Richardson",
    " - Playwright © 2025 Microsoft",
    " - Firefox © 1998-2025 Mozilla and Firefox Contributors",
    " - Nuitka © Copyright 2025 Kay Hayen and Nuitka Contributors\n",
    "This project includes components licensed under the following licenses:",
    " - Python Software Foundation License Version 2",
    " - Apache License 2.0",
    " - GNU General Public License Version 3 (GPLv3)",
    " - Mozilla Public License Version 2.0",
    
    " - MIT License\n",
    "See the LICENSES/ directory for full license texts and details.\n\n"]))
    
    
    time.sleep(5)
    
    print("press enter to agree to the terms of the licenses and continue.")
    input()

    



        


def main(fileName)->bool|str:
    #our main execution function, it mostly just stages out our steps
    #write the header
    easyCLI.fastUIHeader()
    
    easyCLI.fastPrint("beginning setup...\n")
    #startup checks and loading of config files
    easyCLI.fastPrint("loading urls...")
    #create and start our stopwatch
    timer=easyCLI.Stopwatch()
    timer.start()
    rawLinks=loadLinks()
    links:tuple=tuple()
    if((type(rawLinks)==bool)and(rawLinks==False)):
        return False
    elif(type(rawLinks)==tuple):
        links:tuple=rawLinks
        rawLinks=None
    else:
        easyCLI.waitForFastWriterFinish()
        raise Exception("error: url loading failed.")
    
    easyCLI.fastPrint("load successful.\n")
    easyCLI.fastPrint("loading commands...")
    rawCommands=loadCommands()
    commands:list=list()
    if((type(rawCommands)==bool)and(rawCommands==False)):
        return False
    elif(type(rawCommands)==list):
        commands=rawCommands
        rawCommands=None
    else:
        easyCLI.waitForFastWriterFinish()
        raise Exception("error: command loading failed.")
 
    easyCLI.fastPrint("load successful.\n\n")
    
    validateCommands(commands)

    commands=compileCommands(commands)

    easyCLI.fastPrint("\nsetup complete.")
    easyCLI.fastln(4)
    easyCLI.fastPrint("starting data retrieval process...\n\n")
    
    #grab the webpages
    webPages=retrieveWebPages(links[0],links[2],links[3],links[4])
    #extract their raw data
    rawData=retrieveHtmlListTablesAndName(webPages)
    #save ram, free no longer needed values
    webPages=None
    gc.collect()
    #parse that raw data
    dataSets=parseDataSets(rawData,links[1])
    #save ram, free no longer needed values
    rawData=None
    #type ignore to make is calm down about about this manual free
    links=None#type: ignore 
    gc.collect()
    #execute our commands on that parsed data
    displayList=processStocks(commands,dataSets)
    #save ram, free no longer needed values
    dataSets=None
    #type ignore to make is calm down about about this manual free
    commands=None#type: ignore
    gc.collect()
    outputRenderedResults(displayList,fileName)
    #stop the timer
    timer.stop()
    displayList=None
    endTime=timer.getUnitDeviatedTimeString()
    timer=None
    gc.collect()
    return endTime
    






def startup()->None:  
    licenseScreen()
    #if the user wants to download the data
    if(easyCLI.booleanQuestionScreen("would you like to download the configured market data?",None)):
        #have the user the file name they want
        fileName=easyCLI.enterFileNameScreen("please enter the name of the output file.\nwarning, if the file already exists, it will be overwritten.","(do not include the file extension)")+".csv"
        #then start the main program
        endTime=main(fileName)
        if(isinstance(endTime,str)):
            easyCLI.waitForFastWriterFinish()
            print("data retrieval complete!\n")
            print("finished in: "+endTime)
            easyCLI.ln(3)
            input("press enter to finish.")
            easyCLI.ln(3)
    #otherwise
    else:
        easyCLI.clear()
        print("well, thanks anyway!\n")



def integrityCheck()->bool:
    integrity=tuple(["Oi4pUPE$owFG6Kub#!TFb!<~_b#N_BNmMONNkc_WQ$;Rxcys", "VL4)9Wn(#GI5uH7IX5*mHe)qoH!?6cFk@q7WM*YIV`gGxIAbw0G%`13WnnU7W@0yHIW;n7I5uHnVl*=}", "z2n)$3MKl0fDDlZe<G~#A4O@g&ttN7B^SzUEYAD847fU_|Qcm}ipgJU>DjN4=8w*Ug<yvk;uxbRaMgP^c16*^<", "Oi4pUPE$owFJ)nKc|%M|Ek{sHGc8O>Lq$$gMJ{xBbN", "WjHZnI5T81H8f#nIbmUAVlZQ3Vqs=CG-PEsIbt(4V>MwoG&E#kFf(E}WHK-?Ibt(4Gh{F_W;bCsG+{Y7", "vqS7<4-71r<iE<n9C6eZH1swht9fmvPdvv~08PYTz(^6*3-y`5*ymw0v&|8Ez<+SQ<Gyu0R3e{ss&+2mU3OFSI", "Oi4pUPE$owFHUu7bZcQPL2zMXXk{%jE-)=jNkc_WQ$;Rxcys", "GBz<}V=yyiIb>ovW-w)CV=yx~Vm4-CFflM;F=8_^F*svoF)%VXG&yBCH#ah2GdN;4VmUQoVr4ZmVPj%8", "C6AY_s5i334&-10naEb8<oF2#4b+pjstqs4Wi3ex-t`s1^5$m#4c@TnaHphhPeH{QJ)p%9ns^KeVG~{p;`ojxT", "Oi4pUPE$owFHme@d3SPYXJ~XSL2zMXXk{%jE-)=jNkc_WQ$;Rxcys", "Wj8ftGC5^2H8*85Gi5eoGBz<{I5IM2WoBkGIXGcAW;QcpGG${mW;Zf6WI1ADF*G%1G+{VlF*GwXVqrOE", "BMJ<14ON<I8!#T7>0ZlLZSz8j-$NAUu6)WglmRFXH*MKfTILK{OM5*zkY2jO<D57HBM08;(e7QA*f5dU4lh&<U", "Oi4pUPE$owFHm`OXm4&UP*X-sEix@kNkc_WQ$;Rxcys", "H8?S2H#lZwH#Rk4Gh#V8WHw|oVKHMjGBr0iH8Nv1H#TH9F=aDmGh{V3W;HWnIWspmIAu6wWjA6oF*jjk", "mMH%!b58s7-eYfP0_?}}qwSwbSx@Nf)@V-AF&l4oO-aQgjAo6*grgG?CWzh@e)9q-SK~Lh1gU}YJHhO0($6k+9", "Oi4pUPE$owFHLWHX>4p^El_o0Y-wXHOlf0fZgXWVGA=MJOi4pUPE$oLba-?", "H8(LhGBsvpG&DFdGd5y4Gc#c{G&440Fkv}3Vq`EgWHB*eH)AzoFf(E{Ff=w}H#T7~H8V9gW;JAFGBajo", "zEZpn$qfc`PDvN*(jA(N;#Cl>rST;y{raLfHPnMcBCl!Mcpfe1%cesb9Iz>37=7KoZ5_*hkMpcDzN+~7#7p^))", "Oi4pUPE$oLba-?", "IW}Q7G-YBjF*#u}Vl*)|W;Z!xW;SMKHDxd`Ha0h9GG#VqGB`OnVP!QrIAt|BFf=zfF*af{F)}nZV=*;j", "b)zSde|t6_G+t3<6)!v;hDD#({By=c(cIb<d`D}7Uk7_dvstGK?O2@A8%F`^0bun-}xKQ78c58|AGHM3g({csr"])
    
    if(isinstance(integrity,tuple) and (len(integrity)>0) and (len(integrity)%3==0)):
        loops=int(len(integrity)/3)
        readIndex=0
        for fileName in range(loops):
            pathCache=base64.b85decode(integrity[readIndex].encode()).decode()
            readIndex+=2
            if(os.path.exists(pathCache)):
                with open(pathCache, 'r') as current:
                    #i would like to apologize to my ram (and cache)
                    hasher=hashlib.sha256()
                    hasher.update(current.read().encode())
                    hasher.update(integrity[readIndex].encode())
                    readIndex-=1
                    if(base64.b85encode(hasher.hexdigest().encode()).decode()!=integrity[readIndex]):
                        return False 
                    readIndex+=2      
            else:
                return False
        return True
    else:
        return False



if(__name__=="__main__"):
    
    #set the library ui header to the one we just made
    easyCLI.setUIHeader(YahooFinanceGrabberHeader())
    #devious check to make sure no one is doing an illegal thing and distributing without the open source licenses
    print("initializing...")
    if(not integrityCheck()):
        
        easyCLI.uiHeader()
        print(base64.b85decode("MN(2vQaT_^X=7z>b7dfAX>4UEb15KhZ*(ALZ*^{DE(%m=X>%ZOa&KpHVQnC3b0BYUWo{sIZ*_8GWgua0WFT#Ib95kLWgui}b98cPVs&(7WFU8GbZ8)HbaNnVX=7z>b7gZb3Q%liVRL05Wo~nIa%CWNXk{QwNkc_WQ$;Rxcyu6Xb0BbXWpib2bSxlYZe$>IXk{QwNkc_WQ$<rCWNC6`V{~tFc_3+XAPR7DWpib2bRc1FWFTX2ZggR3ZgU`IVRLyyOi3+AP)su|Oi4pUPE$oLba-?uAVOtfb#!TFb!<~_b#N_BNmMONNkc_WQ$;Rxcyufv3Ql!tbZcQPL2zMXXk{%jE-)=jNkc_WQ$;RxcyufvS7l;LX>=`2M^H>HGA=MJLQ_O7Olf0fZgXWWba-?uAYpD~AW&>!d3SPYXJ~XSL2zMXXk{%jE-)=jNkc_WQ$;Rxcyul".encode()).decode())
        input(base64.b85decode("aB^jHb0B4IbY*fNbZ;PLX>MtAXf6".encode()).decode())
        easyCLI.ln(1)
    else:
        startup()
    print("now exiting...")
    easyCLI.ln(1)
    
        
         
