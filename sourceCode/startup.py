   
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
import sys
from sourceCode.backEnd import RENDERERDIR



#need to modify to just use the actual internal api, and doesn't automatically quit. 
# also make sure it actually saves it to the right place.
def downloadPageRenderer():
    easyCLI.uiHeader()
    print("preparing to download...")
    #we do this here because this is the only time we use sh util and internal playright code
    import shutil
    #i know this is awful practice, but what was i supposed to do?!
    from playwright.__main__ import main as playwrightMain

    
    
    #if the browser exists, remove it, so we can replace it.
    global RENDERERDIR
    downloadDir=os.path.abspath(RENDERERDIR)
    if(os.path.exists(downloadDir)):
        shutil.rmtree(downloadDir)
    os.mkdir(downloadDir)

    #set up download and download
    print("starting page renderer download...")
    pathBackup=os.environ.get("PLAYWRIGHT_BROWSERS_PATH",None)
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = downloadDir
    argumentBackup = sys.argv[:]  # backup original args
    sys.argv = ["playwright", "install", "firefox"]
    
  
    #attempt to install browser, while preventing auto exit so we can clean up after
    try:
        playwrightMain()  
    except SystemExit:
        print("download stage completed.")
    except Exception as cause:
        raise Exception("error: download failed! an error occurred during the download process.\nroot cause: "+str(cause))
    finally: 
        print("cleaning up...")
        if(not(pathBackup is None)):
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = pathBackup
        else:
            os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
        sys.argv=argumentBackup

    #remove the folders and files we dont care about
    rendererFolderContents=os.listdir(downloadDir)
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
    
    foundFolderContents=os.listdir(os.path.join(downloadDir,searchDir))
    if("firefox" in foundFolderContents):
        shutil.copytree(os.path.join(downloadDir,searchDir,"firefox"),os.path.join(downloadDir,"firefox"))
    else:
        raise Exception("error: download failed! could not find downloaded folder.")
    
    for unneeded in rendererFolderContents:
 
        shutil.rmtree(os.path.join(RENDERERDIR,unneeded))

    print("download completed successfully!")


#configureLicense(scrambledList: str, indexMap: list[int])
def cleanUpString(brokenString: str, repairList: list[int]) -> str:
    restored = [""] * len(repairList)
    listedScrambledEggs=tuple(brokenString)
    for scrambledIndex, originalIndex in enumerate(repairList):
        restored[originalIndex] = listedScrambledEggs[scrambledIndex]
    return "".join(restored)

#check First File (integrity 1, integrity 2, folder and license, )
def verifyNimbleFile(source1,source2,source3,source4,source5)->tuple[tuple,tuple,tuple,tuple]|bool:
    pathCache=""
    if(os.path.exists(base64.b85decode(cleanUpString(source3[2],source3[3])).decode())):
        pathCache=base64.b85decode(cleanUpString(source3[2],source3[3])).decode()
    elif(os.path.exists(os.path.join(base64.b85decode(cleanUpString(source3[0],source3[1]).encode()).decode(),base64.b85decode(cleanUpString(source3[2],source3[3])).decode()))):
        pathCache=os.path.join(base64.b85decode(cleanUpString(source3[0],source3[1]).encode()).decode(),base64.b85decode(cleanUpString(source3[2],source3[3])).decode())
    else:
        return False

    temp1=source4
    temp2=source5
    
    with open(pathCache,"rt") as toCheck:
        hasher=hashlib.sha256()
        hasher.update(toCheck.read().encode())
        hasher.update(cleanUpString(temp2[1],temp1[1]).encode())
        if(base64.b85encode(hasher.hexdigest().encode()).decode()!=cleanUpString(temp2[0],temp1[0])):
            return False
        temp1=source2
        temp2=source1
    
    return (temp1,temp2,(None,),(None,))
        
        
            
            

#license check
def furtherVerifyBrowser()->int:
    integrity1=((19, 26, 4, 25, 7, 0, 20, 3, 23, 6, 12, 14, 16, 11, 22, 9, 10, 28, 5, 1, 18, 29, 15, 17, 2, 13, 24, 8, 27, 21),
        (63, 76, 21, 10, 4, 27, 11, 20, 30, 52, 12, 43, 45, 29, 77, 14, 51, 47, 64, 57, 75, 48, 67, 31, 55, 24, 35, 0, 79, 49, 5, 17, 46, 54, 33, 60, 7, 22, 9, 6, 69, 36, 71, 28, 41, 72, 37, 74, 13, 32, 66, 8, 16, 68, 25, 61, 34, 42, 19, 59, 15, 73, 58, 44, 26, 78, 65, 50, 56, 2, 53, 23, 39, 3, 62, 18, 38, 1, 70, 40),
        (49, 37, 5, 39, 58, 41, 79, 4, 65, 51, 19, 82, 30, 50, 75, 16, 54, 21, 78, 57, 64, 67, 10, 12, 33, 34, 40, 35, 83, 20, 13, 43, 46, 74, 22, 38, 31, 36, 48, 42, 52, 45, 44, 25, 76, 3, 62, 29, 56, 1, 73, 11, 8, 69, 70, 84, 7, 60, 63, 15, 2, 59, 6, 72, 81, 9, 68, 66, 47, 26, 61, 24, 23, 32, 28, 71, 53, 17, 85, 18, 55, 0, 27, 14, 77, 80),
        (27, 11, 5, 8, 21, 19, 23, 16, 28, 4, 18, 0, 6, 2, 25, 14, 20, 15, 7, 13, 10, 17, 24, 1, 22, 26, 3, 9, 12),
        (77, 28, 37, 62, 66, 64, 72, 24, 51, 58, 26, 55, 76, 29, 50, 0, 18, 45, 39, 38, 53, 41, 73, 79, 40, 47, 12, 2, 30, 32, 61, 36, 54, 1, 33, 17, 60, 4, 44, 43, 78, 75, 19, 31, 23, 63, 13, 10, 52, 59, 14, 6, 22, 65, 49, 70, 67, 8, 9, 21, 42, 34, 25, 57, 74, 69, 46, 71, 20, 5, 68, 48, 7, 15, 56, 35, 27, 3, 16, 11),
        (55, 23, 48, 65, 29, 45, 4, 58, 47, 39, 80, 75, 79, 82, 9, 77, 49, 63, 71, 19, 36, 25, 5, 72, 38, 21, 46, 62, 83, 59, 69, 20, 3, 51, 35, 0, 31, 74, 40, 84, 12, 57, 28, 66, 8, 16, 81, 50, 22, 6, 30, 11, 1, 7, 13, 33, 43, 68, 18, 60, 61, 53, 10, 37, 17, 76, 34, 15, 85, 32, 41, 2, 73, 67, 54, 52, 78, 56, 70, 26, 44, 42, 64, 24, 14, 27),
        (5, 20, 22, 1, 13, 3, 14, 24, 0, 7, 19, 17, 25, 10, 15, 28, 2, 6, 9, 27, 21, 8, 23, 12, 11, 26, 18, 16, 4),
        (60, 51, 53, 24, 76, 62, 40, 26, 39, 9, 3, 78, 17, 28, 65, 15, 44, 5, 49, 4, 10, 37, 2, 21, 32, 63, 68, 12, 74, 45, 72, 18, 55, 77, 64, 7, 22, 13, 33, 20, 52, 75, 38, 25, 0, 34, 36, 61, 47, 19, 59, 58, 50, 31, 54, 70, 57, 69, 41, 16, 48, 14, 11, 6, 67, 43, 46, 35, 30, 42, 27, 29, 73, 56, 23, 1, 8, 79, 71, 66),
        (41, 26, 56, 11, 0, 75, 57, 39, 5, 20, 63, 60, 27, 52, 10, 46, 83, 76, 30, 1, 72, 19, 55, 18, 71, 21, 2, 7, 28, 13, 66, 9, 74, 70, 17, 3, 37, 69, 44, 78, 50, 82, 64, 85, 34, 31, 51, 40, 15, 80, 84, 23, 16, 22, 25, 67, 24, 47, 65, 81, 45, 12, 29, 48, 58, 38, 68, 77, 73, 53, 35, 32, 61, 43, 49, 59, 42, 8, 14, 33, 36, 4, 54, 6, 79, 62),
        (31, 13, 10, 18, 0, 5, 4, 20, 9, 30, 11, 22, 19, 26, 29, 28, 21, 1, 3, 15, 2, 24, 34, 14, 36, 12, 35, 23, 32, 6, 16, 33, 7, 25, 27, 8, 17),
        (70, 71, 55, 2, 12, 73, 10, 53, 39, 68, 36, 61, 35, 23, 21, 51, 8, 5, 77, 1, 57, 78, 59, 32, 3, 15, 14, 20, 52, 46, 29, 24, 60, 17, 41, 58, 79, 11, 9, 34, 45, 38, 33, 40, 37, 63, 7, 65, 64, 27, 6, 62, 75, 44, 72, 13, 31, 4, 54, 50, 22, 28, 48, 49, 0, 76, 26, 69, 19, 66, 56, 74, 67, 16, 18, 42, 43, 30, 47, 25),
        (31, 15, 70, 59, 32, 2, 74, 22, 18, 6, 1, 72, 49, 71, 55, 35, 68, 0, 12, 16, 75, 40, 17, 61, 73, 30, 45, 81, 79, 24, 85, 66, 57, 5, 43, 64, 51, 69, 4, 38, 42, 7, 48, 77, 53, 65, 20, 21, 83, 25, 3, 34, 19, 82, 10, 60, 80, 29, 13, 67, 33, 11, 63, 84, 9, 62, 36, 23, 50, 39, 58, 14, 46, 44, 41, 78, 8, 76, 56, 27, 47, 26, 28, 37, 54, 52),
        (1, 44, 25, 32, 39, 12, 20, 29, 14, 46, 23, 6, 16, 36, 2, 11, 10, 22, 42, 38, 24, 30, 31, 17, 45, 33, 47, 27, 21, 5, 18, 3, 15, 26, 28, 0, 37, 19, 7, 8, 9, 43, 34, 13, 40, 4, 35, 41),
        (6, 49, 45, 48, 77, 71, 58, 55, 43, 66, 41, 40, 22, 12, 35, 78, 75, 26, 15, 36, 0, 47, 1, 23, 34, 7, 63, 62, 28, 60, 32, 69, 19, 2, 37, 65, 39, 73, 42, 29, 8, 72, 68, 74, 53, 30, 11, 24, 79, 17, 54, 76, 67, 10, 64, 56, 21, 46, 57, 52, 5, 61, 27, 4, 38, 14, 51, 33, 25, 31, 59, 50, 3, 9, 18, 44, 20, 70, 13, 16),
        (17, 57, 31, 61, 66, 55, 84, 42, 10, 73, 24, 16, 45, 48, 78, 62, 83, 46, 30, 36, 37, 74, 34, 28, 54, 41, 19, 27, 33, 85, 44, 15, 63, 72, 2, 1, 40, 53, 39, 8, 21, 25, 51, 81, 67, 35, 26, 60, 65, 6, 20, 58, 47, 38, 82, 14, 18, 50, 3, 70, 0, 79, 9, 4, 43, 76, 5, 13, 7, 32, 12, 52, 59, 23, 11, 49, 56, 29, 68, 80, 77, 75, 69, 22, 71, 64),
        (15, 34, 27, 31, 19, 24, 25, 9, 18, 5, 10, 6, 33, 28, 2, 35, 13, 17, 7, 36, 1, 29, 30, 21, 12, 26, 22, 20, 11, 0, 3, 4, 32, 16, 8, 14, 23),
        (42, 69, 43, 28, 65, 51, 13, 16, 64, 18, 29, 39, 33, 60, 71, 70, 35, 12, 5, 67, 15, 8, 14, 79, 23, 75, 73, 34, 63, 59, 66, 53, 26, 44, 4, 62, 9, 25, 38, 41, 10, 58, 52, 61, 50, 68, 55, 40, 11, 49, 17, 45, 72, 19, 74, 3, 0, 7, 56, 27, 22, 48, 76, 32, 77, 31, 47, 46, 1, 36, 6, 54, 21, 57, 20, 30, 2, 37, 24, 78),
        (37, 62, 6, 85, 25, 71, 59, 20, 52, 80, 15, 45, 78, 3, 7, 51, 29, 17, 47, 35, 44, 8, 28, 2, 57, 4, 0, 38, 14, 27, 41, 64, 53, 82, 31, 68, 69, 11, 60, 84, 1, 58, 16, 73, 55, 72, 49, 42, 13, 32, 77, 79, 30, 76, 12, 70, 34, 43, 26, 36, 24, 74, 63, 18, 22, 9, 10, 33, 21, 46, 61, 23, 81, 67, 39, 40, 56, 54, 66, 65, 83, 50, 19, 5, 75, 48),
        (41, 18, 12, 33, 15, 29, 5, 7, 20, 25, 30, 16, 17, 2, 6, 1, 28, 37, 9, 23, 32, 4, 31, 0, 34, 21, 22, 3, 13, 36, 11, 26, 27, 10, 40, 8, 19, 38, 35, 39, 24, 14),
        (77, 18, 67, 61, 74, 16, 32, 3, 14, 41, 46, 54, 23, 49, 40, 35, 25, 72, 42, 76, 31, 57, 37, 24, 62, 36, 56, 58, 51, 79, 1, 2, 78, 29, 21, 28, 11, 63, 34, 53, 30, 13, 69, 71, 39, 65, 0, 43, 7, 52, 5, 44, 17, 45, 19, 66, 50, 38, 59, 12, 47, 6, 10, 55, 22, 73, 68, 27, 70, 20, 48, 15, 33, 75, 4, 64, 26, 60, 8, 9),
        (51, 70, 47, 8, 46, 3, 78, 10, 22, 72, 45, 11, 38, 56, 84, 14, 29, 85, 32, 64, 76, 43, 50, 26, 40, 62, 7, 52, 12, 28, 4, 16, 37, 74, 20, 82, 31, 79, 25, 1, 17, 65, 18, 6, 24, 21, 42, 0, 39, 57, 58, 83, 60, 61, 13, 48, 2, 27, 59, 81, 63, 15, 75, 71, 67, 5, 19, 35, 44, 41, 49, 80, 33, 68, 34, 54, 77, 55, 36, 73, 30, 66, 23, 69, 53, 9),
        (27, 22, 14, 26, 2, 12, 7, 5, 10, 37, 34, 18, 31, 16, 32, 36, 24, 33, 1, 29, 30, 25, 17, 0, 38, 35, 19, 13, 15, 20, 23, 4, 11, 21, 3, 9, 6, 28, 8),
        (61, 76, 25, 21, 18, 27, 74, 75, 33, 28, 49, 73, 59, 50, 44, 70, 22, 7, 43, 45, 1, 14, 47, 64, 10, 63, 4, 39, 57, 67, 56, 3, 13, 54, 9, 35, 46, 23, 19, 42, 12, 40, 53, 32, 8, 72, 2, 15, 60, 41, 51, 36, 48, 65, 5, 52, 30, 58, 79, 69, 71, 77, 16, 0, 20, 24, 38, 26, 62, 6, 66, 78, 29, 37, 34, 31, 68, 55, 17, 11),
        (67, 70, 32, 21, 36, 62, 25, 4, 3, 73, 60, 10, 14, 42, 9, 69, 23, 46, 6, 29, 45, 85, 24, 43, 13, 74, 58, 66, 51, 15, 59, 1, 48, 12, 64, 47, 22, 82, 84, 65, 76, 17, 79, 56, 37, 27, 57, 81, 50, 30, 18, 52, 80, 72, 77, 53, 68, 39, 2, 0, 44, 38, 34, 83, 40, 63, 26, 55, 19, 28, 33, 20, 16, 31, 41, 11, 7, 49, 54, 71, 78, 75, 35, 5, 61, 8),
        (5, 23, 0, 22, 28, 9, 19, 29, 15, 8, 3, 14, 17, 13, 2, 16, 7, 24, 20, 1, 12, 31, 4, 27, 6, 30, 21, 18, 10, 25, 11, 26),
        (79, 21, 4, 78, 1, 5, 13, 56, 34, 11, 33, 69, 53, 46, 40, 24, 9, 52, 6, 74, 70, 63, 62, 20, 55, 18, 75, 66, 16, 28, 72, 35, 3, 67, 54, 17, 37, 73, 42, 23, 30, 27, 51, 41, 61, 14, 15, 22, 0, 77, 29, 49, 57, 38, 76, 50, 32, 71, 45, 26, 10, 39, 36, 47, 64, 58, 7, 59, 48, 44, 19, 25, 65, 8, 68, 60, 2, 43, 31, 12),
        (43, 42, 2, 54, 13, 12, 75, 79, 21, 82, 5, 64, 14, 52, 71, 53, 47, 57, 23, 25, 56, 83, 15, 65, 78, 45, 80, 28, 1, 40, 17, 9, 72, 16, 44, 46, 60, 35, 85, 11, 55, 38, 31, 24, 74, 37, 61, 27, 0, 30, 32, 63, 3, 49, 59, 70, 58, 22, 6, 10, 29, 20, 51, 81, 19, 18, 50, 7, 76, 41, 8, 69, 34, 77, 62, 84, 36, 73, 67, 4, 39, 26, 33, 66, 48, 68))    


    integrity2=("6_9EhWMu&rHNl^U6MTLn#wEfp>i68N",
        "0o!F5bkHH&)FIrBdHad#WUUDIYFHIgF^50tHA(ilX=W^;l1rgoZ#=+F8tS`lVByv=kHW5nH65VD!w8IW", "azn|Rw6V=FLQkeVg_|yk5FwM)jYb_fkt#e&d(>iR(9k79uph*aj^m4&ezSPOY7pB4c&lOdcOVwVUZ=_Q-$8|!5", "--Z|EUoi?6pYEwbOPOPQO4L-$aVvW", "=0>B=$QmP6%H5ZVWiF6ZR5c8IYvII<@iA@|4WEdLfIpbUbZIrynbnF3Wj(q8RuGcr4*;HIJ}kV)W`*rb",
        "q$T?f>RjfQ5==SU*4lh_1Z7bLMD`E7)$iYmTLo!0?QKmSI1CKkeWB;8j@uW;?$Rq!}OZZJS>6iJ0gn_Gk>L*v7", "bP$-QVOLYKU4bOO?w8i-E`oW-api6", "Iovt*jVesjJ<=nVFnWp4W1-&bYWnUVhnGh1Mp%~G9F9HG0j5RVlXWW9FnsPfuCiM-QPWI-)n(&5BTd*q", ";S12IR5iZ`Q}o-t-tM8}UXf_=@gUXRjGQ4K@r|+K4#x5y#%11MCoo@xVx?$9D(!go*xptFbIrUPS~{nhYii1;#",
        "J}EeYEKW7Mi3Cqg$i<*YOeBcN)bo{k+xaL$X-", "IXW3e#HB5Id5GKai~Wd8ANp5+V|H&)76I_dFt8hjFSPGV=cH|AHAW056-bkWTwSPHHlc88jnVKHN;G%F", "Z1+bhL1k@ICu<n3ex+Wu3r=d1E`amOsiC*$HeCD>cZ4<Vx2+!9^qjqV(Q&!k)nlP}yNEedWkYkC6YwZ(pX=^pc", ">xb)W3Xu#yz;=kc<P7;_>E-5c=sd=Y!TX7_Oc+0jIRjKQ>N$",  
        "ekVVzH&I*PXIOeHRHkI!GZdr8@5c4IxB4VwV|$N4qM)r`HM`D;3DaW1AKl&7H5(j3BgtFeJFUptgVWgW", "xYX5S^va%J$Q(E-=`kd*Wf{a=F<oj#)-@@GcEtOhRg{s?uCG1g#bSpj!c>406SObI%=J%(gyd6##Yo993{C@9d", "WB$J;;LxuYahx$YbL2fNIgMf9qBFAPN?{i);|", "a1)vGdJ#{QG9AGHWI(H5HQ2ApV+kZ7da)8msuHnPHiVcGyWV!~cGV5nTWT;d&XrR6GE-i5albHIG~jH7",
        "C}+8N*YU&%fK97XG;;$CD8Er_Wl(a@F{lMd?g@hd92Sb<)@ElP4a(wk|ObdWg*i@Jlv@rav;xe$H<bV<S8^NmO", "NLl$a;cDWFLA96X;|{Gu$&qPgi2m+JmfBXbZ;xMB;>", "Q6$Z!cEM}jj7d3WVI2S;X!4lnL=h;F#9uDajK0m!I-e@FGHI^iHu-WchW@ipH8VV9V&vWHWGyW3ZbH21", "jX(0jV_BXE;6YzE<$drW{gMt<ai_`0Tc)*MQY=>EW2!+~^Qz^06UdTFjf-W>n&PB+B9Fzp(|1n@XhlPX?z_%}s",
        "4r@i3#2XQ-LTEk$acoCUPOka?b!HEbAZ$#E*>pV", "qdFl+PBGT<D+cIHFgJVW-cylIN`en^8@d8jHMraBjWC00JuFVob#SHW}FOnolM*WV?Ugr;ZRZ0`*5HYW", "Ie*ZRCDBh%+~KxCzz*$C;UsdyOcOW@tv(n_VdWo{c}6)3Ih4yuP8sF8${=AC-F%!xJEXT3t4yuoZ(X-fz|>;O#", "Z$P$x6=BGDDJ&ceADgL<|N{{*bqFQM$J",
        "D)1`8WskaB0nz>I8vSI3V;SHF~V*GVpW1#3<8>k+GNAb=4GSH51o@l`I4lV-GCj2pm1e~rkGFIvFV+ds", "vFs!2<no4{V<S+qZckp;ZTEkXR%bE(7))_Gs)2Jju!s9GlE7ob2F0o%ox_l<^&QvUEtk@_81|b6G#c8`+{TT?S")
            


    folderAndLicense=("UipPEow4O$", [4, 1, 3, 5, 6, 8, 9, 2, 0, 7], "4pEoPab$iU-LO?", [2, 3, 6, 8, 5, 11, 10, 7, 1, 4, 12, 9, 0, 13])

    integrity3=((24, 74, 57, 13, 63, 73, 14, 10, 21, 72, 20, 16, 7, 31, 23, 51, 37, 52, 26, 12, 53, 78, 54, 68, 18, 1, 8, 5, 55, 46, 39, 27, 36, 9, 44, 76, 41, 62, 40, 0, 48, 71, 58, 32, 49, 77, 42, 30, 66, 6, 35, 64, 45, 70, 75, 29, 11, 2, 56, 69, 43, 38, 34, 3, 25, 59, 19, 79, 67, 28, 50, 4, 61, 60, 15, 47, 33, 17, 22, 65),
        (23, 65, 27, 19, 34, 74, 46, 22, 56, 33, 0, 18, 81, 8, 40, 47, 58, 69, 63, 43, 6, 31, 75, 76, 30, 68, 59, 62, 44, 82, 50, 72, 14, 60, 79, 21, 37, 85, 32, 9, 20, 41, 15, 2, 52, 25, 78, 54, 71, 16, 26, 49, 10, 5, 84, 35, 38, 57, 11, 64, 77, 66, 17, 42, 13, 12, 24, 39, 45, 48, 67, 36, 55, 7, 73, 4, 28, 29, 80, 61, 51, 83, 3, 1, 70, 53))
    

    integrity4=("wt9Tcf1WMMW=A%4#70Z&YW7wM&$FF)ToB69r5vIG6`6_8DsG)=G6HVVoiwl1znhRH`5l1;Hd>VFc|RgH",
        "1-%0MCa4u3K|>1Kogd<wu>XnbUlx`@|3^<;0+))ZEdBsKe&~oPz}5E7>BFXmEg~D!ns`UYFJ$Ecz9i*TR^IK!1")


    if(isinstance(integrity1,tuple) and (len(integrity1)>0) and (len(integrity1)%3==0)):
        
        validationResult=verifyNimbleFile(integrity1,integrity2,folderAndLicense,integrity3,integrity4)
        if((type(validationResult)==bool)and(validationResult==False)):
            return -2
        elif((isinstance(validationResult,tuple)) and all(isinstance(res,tuple) for res in validationResult)):
            if((len(validationResult[2])==1)and(len(validationResult[3])==1)and(validationResult[2][0] is None)and(validationResult[3][0] is None)):
                integrity1=validationResult[0]
                integrity2=validationResult[1]
                integrity3=validationResult[2]
                integrity4=validationResult[3]
                validationResult=None
            else:
                return -2
        else:
            return -2

        loops=int(len(integrity1)/3)
        readIndex=0
        
        folderAndLicense=base64.b85decode(cleanUpString(folderAndLicense[0],folderAndLicense[1]).encode()).decode()

        for fileName in range(loops):
            pathCache=os.path.join(folderAndLicense,base64.b85decode(cleanUpString(integrity1[readIndex],integrity2[readIndex]).encode()).decode())
            
            readIndex+=2
            if(os.path.exists(pathCache)):
                with open(pathCache, 'r') as current:
                    #i would like to apologize to my ram (and cache)
                    hasher=hashlib.sha256()
                    hasher.update(current.read().encode())
                    hasher.update(cleanUpString(integrity1[readIndex],integrity2[readIndex]).encode())
                    readIndex-=1
                    if(base64.b85encode(hasher.hexdigest().encode()).decode()!=cleanUpString(integrity1[readIndex],integrity2[readIndex])):
                        return -2
                    readIndex+=2
                    hasher=None      
            else:
                return -2

        return 1
    else:
        return -2


def integrityCheck()->int:
    global RENDERERDIR
    fireFolder=os.path.join(RENDERERDIR,"Firefox")
    if(os.path.exists(RENDERERDIR) and os.path.exists(fireFolder)):
        folderSet=set(os.listdir(fireFolder))
        pathsToCheck=("AccessibleMarshal.dll", "firefox.exe", "freebl3.dll", "gkcodecs.dll", "lgpllibs.dll", "libEGL.dll", "libGLESv2.dll", "mozavcodec.dll", "mozavutil.dll", "mozglue.dll", "msvcp140.dll", "nmhproxy.exe", "notificationserver.dll", "nss3.dll", "pingsender.exe", "plugin-container.exe", "private_browsing.exe", "softokn3.dll", "updater.exe", "vcruntime140.dll", "vcruntime140_1.dll", "wmfclearkey.dll", "xul.dll")
        
        if(all((path in folderSet) for path in pathsToCheck)):
            return furtherVerifyBrowser()
        else:
            return -1
    else:
        return -1
    


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
    " - psutil © 2009 Jay Loden, Dave Daeschler, Giampaolo Rodola, and psutil Contributors",
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
        self.vNumber="v1.4.0"
        self.vString="Yahoo Finance Historical Data Downloader "+self.vNumber+" by redcacus5"+"\n\n"

    def drawUIHeader(self):
        easyCLI.clear()
        print(self.vString)
    
#securityMessage
def badCrash()->None:
    lookup=("463", "21", "367", "105", "306", "338", "446", "664", "304", "563", "111", "379", "41", "633", "12", "20",
        "84", "535", "494", "369", "19", "177", "523", "490", "282", "365", "652", "667", "469", "150", "227",
        "493", "565", "451", "324", "653", "513", "257", "300", "94", "403", "101", "319", "575", "533", "404",
        "637", "461", "397", "26", "328", "567", "192", "325", "321", "444", "202", "53", "155", "578", "465",
        "310", "642", "488", "139", "496", "509", "240", "400", "577", "44", "409", "9", "445", "322", "529",
        "627", "81", "128", "273", "182", "267", "99", "421", "207", "561", "482", "343", "97", "387", "36",
        "118", "210", "93", "268", "46", "330", "619", "436", "122", "242", "361", "661", "681", "466", "235",
        "675", "25", "406", "632", "401", "386", "468", "298", "398", "393", "426", "221", "598", "635", "308",
        "296", "555", "244", "61", "363", "49", "630", "395", "356", "433", "174", "453", "510", "66", "623",
        "583", "549", "464", "424", "434", "615", "148", "326", "366", "103", "279", "350", "671", "620", "332",
        "594", "230", "419", "480", "516", "591", "428", "382", "566", "23", "110", "407", "146", "65", "362",
        "226", "224", "521", "568", "588", "213", "437", "478", "154", "149", "18", "660", "558", "670", "585",
        "140", "631", "62", "528", "173", "171", "504", "574", "218", "354", "610", "219", "4", "679", "241",
        "432", "644", "147", "80", "554", "580", "622", "3", "541", "55", "45", "186", "38", "15", "129",
        "57", "649", "666", "351", "119", "95", "371", "368", "626", "107", "481", "114", "124", "162", "605",
        "238", "624", "292", "503", "370", "270", "359", "646", "559", "640", "120", "215", "378", "35", "538",
        "601", "303", "636", "527", "158", "617", "302", "460", "7", "372", "415", "569", "673", "323", "658",
        "31", "112", "6", "612", "484", "581", "374", "142", "76", "190", "183", "414", "69", "360", "285",
        "497", "411", "274", "427", "278", "209", "676", "412", "531", "389", "441", "82", "185", "506", "629",
        "188", "170", "75", "163", "312", "301", "189", "212", "570", "92", "394", "216", "429", "352", "438",
        "217", "600", "639", "677", "525", "602", "456", "138", "265", "77", "141", "203", "145", "198", "237",
        "413", "655", "560", "608", "331", "313", "657", "443", "249", "264", "33", "56", "266", "256", "132",
        "475", "333", "130", "166", "2", "410", "135", "606", "232", "656", "377", "648", "63", "498", "11",
        "522", "556", "381", "196", "8", "276", "131", "255", "540", "613", "518", "347", "286", "40", "169",
        "211", "459", "201", "603", "514", "545", "5", "254", "184", "607", "72", "500", "654", "467", "511",
        "376", "283", "133", "251", "431", "564", "551", "195", "277", "392", "269", "263", "586", "358", "231",
        "595", "665", "520", "151", "48", "489", "176", "253", "293", "91", "307", "643", "199", "477", "532",
        "317", "420", "634", "457", "651", "236", "165", "315", "175", "16", "435", "214", "316", "87", "452",
        "439", "30", "1", "355", "14", "572", "425", "194", "43", "309", "164", "609", "546", "246", "197",
        "191", "440", "102", "245", "385", "589", "544", "181", "272", "349", "479", "28", "115", "271", "399",
        "487", "678", "534", "153", "34", "462", "67", "22", "625", "341", "680", "592", "86", "223", "88",
        "582", "262", "143", "447", "507", "70", "39", "418", "539", "375", "311", "396", "383", "187", "373",
        "530", "663", "454", "576", "260", "297", "204", "79", "280", "584", "74", "483", "515", "137", "160",
        "474", "650", "647", "291", "391", "552", "448", "17", "109", "113", "64", "524", "348", "327", "233",
        "423", "335", "659", "54", "106", "422", "78", "58", "492", "611", "562", "42", "167", "638", "402",
        "512", "116", "50", "471", "553", "193", "405", "599", "51", "90", "222", "284", "96", "485", "24",
        "416", "161", "117", "259", "495", "508", "289", "200", "47", "125", "339", "60", "234", "616", "305",
        "604", "672", "123", "587", "417", "502", "336", "596", "299", "247", "662", "172", "547", "537", "179",
        "220", "472", "206", "473", "288", "73", "108", "159", "344", "499", "491", "536", "68", "168", "229",
        "239", "334", "501", "597", "261", "258", "526", "178", "144", "384", "71", "571", "52", "486", "388",
        "98", "59", "290", "225", "275", "380", "645", "573", "590", "127", "543", "628", "430", "442", "548",
        "314", "450", "455", "340", "205", "357", "364", "37", "10", "248", "621", "89", "542", "250", "353",
        "682", "243", "32", "294", "641", "329", "345", "550", "121", "104", "29", "27", "593", "337", "342",
        "85", "287", "505", "476", "252", "519", "470", "318", "674", "579", "156", "152", "557", "83", "134",
        "208", "100", "449", "157", "668", "320", "136", "517", "346", "458", "126", "618", "228", "669", "13",
        "390", "281", "0", "295", "180", "408", "614")
    easyCLI.uiHeader()
    rawMessage=("C", "o", "X", "b", "M", "(", "b", "d", "e", "a", "o", "9", "T", "R", "i", "F", 
        "c", "o", "g", "w", "Z", "b", "7", "p", "l", "7", "7", "6", "g", "H", "X",
        "3", "y", "=", "A", "B", "V", "{", "$", ";", "0", "0", "G", "g", "E", "b",
        "H", "L", "2", "F", "g", "?", "}", "V", "$", "3", "q", "S", "Z", "o", "O",
        "`", "W", "M", "O", "A", "y", "?", "U", "M", "x", "o", "8", "A", "`", "b",
        "A", "W", "X", "W", "h", "s", "V", "-", "4", "i", "(", "x", "H", "W", "`",
        "K", "i", "O", "y", ">", "U", "}", "0", "{", "i", "k", "x", "B", "b", "a",
        "m", "b", "!", "p", "5", "A", "N", "4", "-", "~", "-", "X", "F", "<", "q",
        "u", "d", "8", "i", "$", "7", "Z", "i", "j", "Z", "g", "b", "d", "b", "X",
        "s", "Q", "D", "5", "Q", "F", "{", "E", "o", "W", "H", "b", ">", "K", "P",
        "R", "n", "=", "X", "9", "?", "4", "p", "L", "7", "$", "+", "c", "K", "Z",
        "0", "g", "E", "c", "L", "!", "Z", "{", "M", "$", "L", "#", "0", "p", "T",
        "9", "8", "p", "!", "E", "+", "3", "U", "X", "_", "=", "i", "a", "O", "X",
        "c", "O", "l", "b", "e", "G", "&", "c", ";", "-", "g", "E", "U", "C", "|",
        "E", "<", "8", ")", "4", "U", "C", "V", "Q", "k", "b", "J", "M", "*", "^",
        "0", "-", "z", "J", "x", ")", "O", "Y", "b", "I", ">", "Y", "^", "k", "L",
        "w", "Y", "W", "_", "M", "$", "u", "p", "a", "c", "i", "3", "z", "x", "Z",
        "x", "5", "c", "N", "V", "6", "k", "n", "4", "N", "E", "%", "a", "B", "V",
        "*", "k", "c", "u", "d", "u", "=", "7", "X", "c", "g", "0", "b", "p", "%",
        "j", "f", "=", "E", "W", "Y", "v", "M", "_", "p", "w", "K", "*", "c", "D",
        "$", "o", "Q", "(", "(", "_", "R", "3", "7", "c", "%", ")", "w", "!", "Q",
        "b", "Q", "X", "0", ">", "R", "5", "X", "0", "s", "A", "e", "P", "b", "s",
        "n", "`", "y", "}", "!", "S", "g", "R", "A", "T", "8", "i", "z", "i", "W",
        "b", "(", "R", "V", "O", "X", "&", "Z", "E", "1", "k", "U", "a", "&", ")",
        ";", "c", "}", "V", "E", "?", "O", "6", "b", "b", "Z", "%", "P", "8", ">",
        "a", "V", "{", "~", "E", "r", "#", "Y", "#", "a", "i", "B", "E", "c", "W",
        "F", "V", "l", "X", "W", "_", "B", "R", "N", "K", "N", "6", "A", "-", "J",
        "2", "-", "@", "B", "a", ";", "b", "E", "D", "k", "Q", "Q", ">", "8", "i",
        "N", "u", "-", "a", "T", "Q", "}", "M", "$", "z", "E", "U", "T", "Y", "T",
        "3", "Z", "y", "Q", "X", "k", "p", "W", "T", "A", "W", "3", "K", "#", "l",
        "A", "M", "B", "i", "g", "!", "E", "%", "}", "I", "7", "u", "J", "#", "N",
        "W", "L", "5", "i", "L", "5", "P", "a", ";", "k", "b", "b", "E", "2", "$",
        "M", "{", "a", "N", "G", "c", "^", "B", "v", "D", "Y", "5", "P", "J", "x",
        "o", "n", "b", "(", "R", "b", "E", "L", "{", "Y", "s", "V", ">", "z", "f",
        "P", "T", "}", "k", "T", "L", "o", "Z", "a", "$", "W", "7", "P", "k", "w",
        "}", "=", "b", "K", "C", "x", "8", "L", "q", "B", "2", "8", "l", "k", "n",
        "W", "-", "R", "I", "k", "&", "$", "*", "V", "6", "I", "X", "x", "O", "b",
        "A", "*", "*", "{", "b", "R", "R", "V", "*", "a", "Y", "`", "Q", "1", "K",
        "-", "i", "s", "E", "V", "M", "Z", "<", "S", "+", "l", "Z", "u", "l", "e",
        "G", "7", "o", "Y", "b", "k", "G", "w", "{", "x", "d", "J", "i", "3", "I",
        "$", "{", "H", "c", "&", "{", "9", "%", "E", "M", "L", ">", "f", "O", "W",
        "~", "$", "G", "=", "<", "Z", "P", "#", "b", "U", "B", "i", "|", "E", ";",
        "j", "s", "{", "W", ";", "y", "U", "M", "E", "7", "*", "p", "U", "W", "B",
        "6", "X", "|", "}", "V", "_", "4", "X", "#", "3", "a", "E", "N", "N", "T",
        "C", "V", "6", "W", "O", "H", "A", "g", "M", "=", "w", "F", "&", "2", "C",
        "_", "$", "g", "W", "f", "Y", "j")
    message=tuple([rawMessage[int(lookup[index])] for index in range(len(lookup)-1,-1,-1)])
    lookup=None
    rawMessage=None
    print(base64.b85decode("".join(message).encode()).decode())
    easyCLI.ln(3)
    input("press enter to finish.")
    easyCLI.ln(1)
    print("now exiting...")
    easyCLI.ln(1)
    sys.exit()

def startup()->None: 
    #set the library ui header to the one we just made
    easyCLI.setUIHeader(YahooFinanceGrabberHeader())
    #devious check to make sure no one is doing an illegal thing and distributing without the open source licenses
    print("initializing...")
    #do an integrity check 
    
    checkSuccess=0

    checkSuccess+=integrityCheck()
    

    
    if(checkSuccess==-1):
        #something wrong with firefox
        message="critical error: integrity check failed, renderer is corrupted or missing."
        prompt=easyCLI.multilineStringBuilder([
            "this error can likely be fixed by downloading a new copy of the renderer.",
            "this can be performed automatically. please note that the program will", 
            "close automatically after the download. \n",
            "would you like to download the renderer?"
        ])
        userDecision=easyCLI.booleanQuestionScreen(message,prompt)
        if(userDecision):
            downloadPageRenderer()
            easyCLI.ln(2)
            input("press enter to finish.")
            easyCLI.ln(1)
        else:
            easyCLI.uiHeader()
            print("renderer download will not be performed.")
            easyCLI.ln(3)
            

    elif(checkSuccess==1):
        try:
            commandLineInterface()
        except browserLaunchFail as fail:
            easyCLI.uiHeader()
            print(fail.message)
            easyCLI.ln()
            print("root cause: "+str(fail.getRootError()))
            easyCLI.ln(3)
            input("press enter to finish.")
    
    else:
        badCrash()


 
