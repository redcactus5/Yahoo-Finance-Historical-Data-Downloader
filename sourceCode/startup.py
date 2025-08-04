   
'''
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 
'''

import base64
import hashlib
import sourceCode.backEnd as backend
import time
import dependencies.easyCLI as easyCLI
import os
from sourceCode.backEnd import browserLaunchFail

from sourceCode.backEnd import RENDERERDIR




def downloadPageRenderer():
    #we do this here because this is the only time we use subproccess and sh util
    import subprocess
    import shutil
    global RENDERERDIR
    easyCLI.uiHeader()
    print("preparing to download...")
    #if the browser exists, remove it, so we can replace it.
    if(os.path.exists(RENDERERDIR)):
        shutil.rmtree(RENDERERDIR)
    os.mkdir(RENDERERDIR)

    #set up download and download
    print("starting page renderer download...")
    environmentVariables = os.environ.copy()
    environmentVariables["PLAYWRIGHT_BROWSERS_PATH"] = RENDERERDIR
    subprocess.run(["playwright", "install", "firefox"], env=environmentVariables, check=True)
    #remove the folders and files we dont care about
    print("cleaning up...")
    rendererFolderContents=os.listdir(RENDERERDIR)
    #find the top level firefox folder
    success=False
    searchDir=""
    for content in rendererFolderContents:
        if("firefox-" in content):
            success=True
            searchDir=content
            
            break
    
    if(not success):
        raise Exception("error: download failed! could not find downloaded folder.")
    
    foundFolderContents=os.listdir(os.path.join(RENDERERDIR,searchDir))
    if("firefox" in foundFolderContents):
        shutil.copytree(os.path.join(RENDERERDIR,searchDir,"firefox"),os.path.join(RENDERERDIR,"firefox"))
    else:
        raise Exception("error: download failed! could not find downloaded folder.")
    
    for unneeded in rendererFolderContents:
        shutil.rmtree(os.path.join(RENDERERDIR,unneeded))

    print("download completed successfully!")



#not done yet
def licenseCheck()->bool:
    integrity1=tuple(["Oi4pUPE$owFJ)nKc|%M|Ek{sHGc8O>Lq$$gMJ{xBbN", "Vq-HlWHvT4G+|_BW@a-oGch<eHf1znGcsc_H8C<cW;14EW->EmGGjAgVPs=CVL3B6H)b|sV`DimGGk&g", "3t=Pjtq-~6V7dz|+g$w9S5LB<}L}_`~oDwAVoJ8!CJesZsz%n<o}aUdS!r$A$hd6O(qK&>9t-IT2JHm*)?bBZo", "Oi4pUPE$owFKlUIcx`MlElo*OElf#6MNU&iE_8Tw", "V>UHqGGQ<>VKZbhHDoz6V`esFIXPrCH!wJ4W??fhFgGz_W??sFGiEVmIW{siGGZ_`W;r=AVPi2jF*7!1", "%%L?bD@a-Pld7~XBDNND6#rI$afW1B1?@1mq7)I9p2W#FPmlDZfcZ{To?*PGF6r(D_50s~KAjUZ<<zxLXFqu-z", "Oi4pUPE$owFKlUIcynxYElo*OElf#6MNU&iE_8Tw", "He@klFlJ&nI5RakHf3gEGBq?cIW#mdFl9I~IW=T4GBGzZWMgGAH#KEBG%;pjVPY^dW->4{W;bCnW?^D8", "1B@VO^Hgy3j8Mu|p5lVD!wi)4Uu^fdE~X;#HK(eviEkkev`hjS$UJ8&U=C|Ouy}TWu3p=Z~%(45wlU{+NT~yZW", "Oi4pUPE$owFKl>iY%M}lL@hHdLu_Gnb7d_|Nkc_WQ$;Rxcys", "WMpAvVKiblWi?|kFg9gjH#0XdFk&-eVq#=AWjQ%vH8e70GBr42Ic7LyWMMI8Wic^1F<~?{WMO4vVPQFC", "Qv||@6qWerf#}rb1uez90;eD#WO>1;+n^U)UlUwx(S#wGfXF%Kl~t_ro2O`LjQ3q>6#SLs({zssxSdfkU@aGUO", "Oi4pUPE$owFHLWHX>4p^El_o0Y-wXHOlf0fZgXWVGA=MJOi4pUPE$oLba-?", "Wn*SHV>UQpIXN;gGB{ymHD+OCWMnciV>x7IGi6~lGGs6~Ibk<BW;bRsIWuE4G+{D0H8M9jW@I#DH)UdD", "XB(1L_Sy2&P9JZ+J!x-f?(@tn2xv1G$$BzoCDKpY3e#sj+n$z|%}|LGs?z4Vehn(%D7w%YuNWEtKy3TTNu-g+#", "Oi4pUPE$owFHUu7bZcQPL2zMXXk{%jE-)=jNkc_WQ$;Rxcys", "G%+|bWH)0oVly^4Fgal{W;iltIA&opHZw3{IAS?uGdVCcIb$(1HaRwCGhsAgHZ*24GGjM2H8e3~IXO5v", "5r{34hDA762*_sxsAyy=ZeBuwz>gY%;4U_I4;5j-?+ApA%~(ng{VeU4vX&twl*+IbNMU*cR|01m#!iJLcTg~4*", "Oi4pUPE$owFHme@d3SPYXJ~XSL2zMXXk{%jE-)=jNkc_WQ$;Rxcys", "VK+H2Gh#P4W;ZxAF)(IiGh}5lHe+RBHZ?b6FgRpoWi&TpVPR!sIc7IvV=y>0V`E`qVlgyiF=jP5Fkv__", "QcU>Kdbyfb<ySFE@4>+`7!%4SEI|ma2N{yrzO_d)vr^QZhV&WelXJC^O64yBeYUSlQ<JECu^DPR~o(MnRuQCH{", "Oi4pUPE$owFHm`OXm4&UP*X-sEix@kNkc_WQ$;Rxcys", "W-&E3IX5>qG&N;6F=J&oGBh@3W??ZlF*GtbW;kJCH#cE5HfCaCG-5P3IAl0wF*q_bH)b(0Wieu8H8f-}", "ap7*5qy*{YVlyPdw{s$8@^+yT>w&BXRhWlJg8*h$ESDueADR3=&`N`EnQ?C#(U(!^t6{43~rgE|2ZU;~ZI0ZWZ", "Oi4pUPE$oLba-?", "F)=VPG&VP8Wn(!wFlIGkFfw5^VK-xCHDzICGGQ?=Vl`oAWHMnmGcjc|FlI3`GGQ?@VKOmfIWl57Vqsxp", "w#vRqdvQx!OYd!3(ZDRqk4^O0agS{D^=@5BgHj)mf>Mgd-?%W#)et>?6z8FV&SAP`N7PvCW*BBnzP63-8Ye@gJ"])
    if(isinstance(integrity1,tuple) and (len(integrity1)>0) and (len(integrity1)%3==0)):
        loops=int(len(integrity1)/3)
        readIndex=0
        for fileName in range(loops):
            pathCache=base64.b85decode(integrity1[readIndex].encode()).decode()
            readIndex+=2
            if(os.path.exists(pathCache)):
                with open(pathCache, 'r') as current:
                    #i would like to apologize to my ram (and cache)
                    hasher=hashlib.sha256()
                    hasher.update(current.read().encode())
                    hasher.update(integrity1[readIndex].encode())
                    readIndex-=1
                    if(base64.b85encode(hasher.hexdigest().encode()).decode()!=integrity1[readIndex]):
                        return False
                    readIndex+=2      
            else:
                return False

        return True
    else:
        return False


def integrityCheck()->bool:
    global RENDERERDIR
    fireFolder=os.path.join(RENDERERDIR,"Firefox")
    if(os.path.exists(RENDERERDIR) and os.path.exists(fireFolder)):
        folderSet=set(os.listdir(fireFolder))
        pathsToCheck=("AccessibleMarshal.dll", "firefox.exe", "freebl3.dll", "gkcodecs.dll", "lgpllibs.dll", "libEGL.dll", "libGLESv2.dll", "mozavcodec.dll", "mozavutil.dll", "mozglue.dll", "msvcp140.dll", "nmhproxy.exe", "notificationserver.dll", "nss3.dll", "pingsender.exe", "plugin-container.exe", "private_browsing.exe", "softokn3.dll", "updater.exe", "vcruntime140.dll", "vcruntime140_1.dll", "wmfclearkey.dll", "xul.dll")
        
        if(all((path in folderSet) for path in pathsToCheck)):
            return True
        else:
            return False
    else:
        return False
    


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
    " - lxml © 2004 Infrae and lxml Contributors",
    " - libxml2 © 1998-2012 Daniel Veillard and libxml2 Contributors",
    " - libxslt © 2001-2002 Daniel Veillard and libxslt Contributors",
    " - Playwright © 2025 Microsoft",
    " - Nuitka © Copyright 2025 Kay Hayen and Nuitka Contributors",
    " - Firefox © 1998-2025 Mozilla and Firefox Contributors\n",
    "This project includes components licensed under the following licenses:",
    " - Python Software Foundation License Version 2",
    " - GNU General Public License Version 3 (GPLv3)",
    " - BSD 3 Clause License",
    " - MIT License",
    " - Apache License 2.0",
    " - Mozilla Public License Version 2.0\n",
    "See the LICENSES/ directory for full license texts and details.\n\n"]))
    
    
    time.sleep(5)
    
    print("press enter to agree to the terms of the licenses and continue.")
    input()

    

def commandLineInterface():
    licenseScreen()
    #if the user wants to download the data
    if(easyCLI.booleanQuestionScreen("would you like to download the configured market data?",None)):
        #have the user the file name they want
        fileName=easyCLI.enterFileNameScreen("please enter the name of the output file.\nwarning, if the file already exists, it will be overwritten.","(do not include the file extension)")+".csv"
        #then start the main program
        endTime=backend.main(fileName)

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


class YahooFinanceGrabberHeader(easyCLI.UIHeaderClass):
    #simple header class required by easy cli
    def __init__(self):
        super().__init__(None)
        self.vNumber="v1.3"
        self.vString="Yahoo Finance Historical Data Downloader "+self.vNumber+" by redcacus5"+"\n\n"

    def drawUIHeader(self):
        easyCLI.clear()
        print(self.vString)
    


def startup()->None: 
    #set the library ui header to the one we just made
    easyCLI.setUIHeader(YahooFinanceGrabberHeader())
    #devious check to make sure no one is doing an illegal thing and distributing without the open source licenses
    print("initializing...")
    #do an integrity check 
    

    if(not licenseCheck()):
        easyCLI.uiHeader()
        errorMessage=("ERROR: integrity check failed, License file(s) not found.",
            "This program is open source and must be distributed with its licenses.",
            "Please ensure the LICENSE.txt is present in the program's root folder, and", 
            "the LICENSES directory is present and contains: \"easyCLI-GPL3-LICENSE.txt\",", 
            "\"libxml2-MIT-LICENSE.txt\", \"libxslt-MIT-LICENSE.txt\", \"Python-PSFL-2-LICENSE.txt\",", 
            "\"Mozilla-Public-License-2.0-LICENSE.txt\", \"Playwright-Apache-2.0-LICENSE.txt\",", 
            "\"Nuitka-Apache-2.0-LICENSE.txt\", and \"lxml-BSD-3-Clause-LICENSE.txt\".")
        print(easyCLI.multilineStringBuilder(list(errorMessage)))
        easyCLI.ln(3)
        input("press enter to finish.")
        easyCLI.ln(1)
        return
    elif(not integrityCheck()):
        #something wrong with firefox
        message="critical error: integrity check failed, renderer is corrupted or missing."
        prompt=easyCLI.multilineStringBuilder([
            "this error can likely be fixed by downloading a new copy of the renderer.",
            "this can be performed automatically. please note that the program will.", 
            "have to be restarted after the download.\n",
            "would you like to download the renderer?"
        ])
        userDecision=easyCLI.booleanQuestionScreen(message,prompt)
        if(userDecision):
            downloadPageRenderer()
            easyCLI.ln(2)
            input("press enter to finish.")
    else:
        try:
            commandLineInterface()
        except browserLaunchFail as fail:
            easyCLI.uiHeader()
            print(fail.message)
            easyCLI.ln()
            print("root error: "+str(fail.getRootError()))
            easyCLI.ln(3)
            input("press enter to finish.")


 
