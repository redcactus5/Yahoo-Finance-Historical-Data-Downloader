   
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
    lookup=("206", "134", "223", "363", "135", "445", "16", "21", "361", "536", "255", "81", "436", "635", "435",
        "448", "269", "503", "227", "580", "632", "17", "261", "280", "273", "141", "37", "578", "500", "408",
        "507", "589", "239", "414", "333", "62", "68", "543", "65", "264", "200", "370", "615", "144", "300",
        "324", "95", "72", "298", "6", "323", "169", "76", "380", "113", "41", "411", "577", "505", "517",
        "664", "373", "618", "535", "320", "601", "77", "542", "556", "539", "4", "222", "364", "388", "426",
        "97", "486", "163", "398", "10", "327", "607", "354", "643", "527", "396", "133", "668", "581", "650",
        "170", "640", "78", "609", "644", "682", "157", "538", "402", "154", "160", "80", "351", "573", "488",
        "557", "475", "137", "593", "325", "428", "619", "236", "605", "390", "91", "183", "413", "165", "420",
        "524", "376", "561", "574", "290", "374", "670", "130", "282", "464", "217", "564", "437", "104", "308",
        "140", "487", "341", "179", "496", "54", "38", "190", "382", "303", "59", "105", "263", "508", "614",
        "649", "460", "456", "254", "467", "510", "439", "67", "26", "139", "240", "509", "109", "666", "620",
        "409", "218", "319", "608", "551", "106", "353", "349", "553", "646", "235", "185", "391", "5", "358",
        "15", "405", "345", "489", "612", "256", "678", "491", "195", "466", "186", "647", "639", "229", "617",
        "360", "463", "338", "367", "146", "309", "85", "604", "299", "96", "662", "127", "69", "142", "658",
        "306", "454", "447", "301", "192", "403", "562", "220", "36", "493", "502", "128", "451", "569", "392",
        "352", "379", "585", "421", "479", "119", "267", "526", "366", "313", "362", "480", "570", "523", "35",
        "636", "506", "272", "47", "676", "50", "176", "64", "657", "75", "171", "121", "667", "547", "2",
        "275", "651", "638", "211", "19", "665", "461", "555", "633", "566", "521", "340", "111", "389", "24",
        "531", "103", "652", "305", "312", "622", "540", "347", "201", "203", "18", "115", "149", "58", "599",
        "610", "660", "497", "174", "501", "546", "14", "416", "321", "55", "205", "375", "225", "116", "595",
        "424", "151", "187", "492", "368", "565", "326", "331", "193", "423", "329", "153", "32", "262", "550",
        "182", "677", "671", "355", "100", "40", "430", "648", "520", "356", "394", "274", "386", "419", "511",
        "43", "318", "92", "213", "348", "237", "590", "385", "422", "623", "7", "637", "126", "83", "108",
        "164", "412", "311", "381", "514", "383", "74", "472", "672", "189", "336", "48", "249", "131", "61",
        "242", "681", "446", "71", "427", "407", "245", "278", "332", "378", "289", "112", "629", "457", "611",
        "594", "284", "576", "401", "453", "215", "33", "31", "504", "175", "606", "455", "224", "642", "202",
        "335", "293", "288", "377", "216", "613", "125", "184", "591", "27", "51", "147", "252", "194", "484",
        "552", "522", "11", "44", "473", "429", "13", "23", "79", "226", "243", "346", "209", "515", "337",
        "631", "533", "314", "295", "266", "117", "602", "525", "315", "563", "655", "372", "257", "88", "673",
        "654", "603", "395", "634", "544", "60", "350", "674", "558", "304", "549", "433", "365", "268", "415",
        "251", "241", "150", "425", "250", "344", "46", "145", "450", "359", "661", "410", "659", "246", "310",
        "518", "481", "87", "29", "114", "626", "143", "271", "129", "297", "198", "512", "238", "86", "393",
        "28", "138", "101", "8", "334", "598", "470", "286", "438", "168", "579", "181", "230", "458", "575",
        "283", "53", "469", "532", "191", "621", "247", "656", "384", "70", "534", "474", "57", "442", "628",
        "559", "294", "482", "476", "485", "529", "417", "669", "431", "277", "545", "279", "210", "616", "596",
        "94", "118", "567", "197", "123", "219", "494", "316", "244", "188", "89", "387", "233", "90", "162",
        "630", "490", "645", "513", "462", "234", "177", "161", "322", "582", "330", "152", "276", "9", "259",
        "597", "214", "231", "166", "339", "49", "285", "82", "498", "459", "178", "66", "342", "516", "136",
        "253", "568", "270", "25", "287", "397", "653", "328", "120", "260", "156", "0", "584", "292", "281",
        "30", "232", "1", "317", "495", "441", "627", "530", "449", "444", "541", "471", "265", "432", "406",
        "180", "167", "302", "98", "680", "600", "307", "571", "221", "56", "52", "443", "212", "258", "204",
        "468", "291", "93", "583", "483", "3", "586", "418", "248", "440", "560", "99", "42", "159", "45",
        "663", "343", "107", "155", "124", "296", "537", "73", "400", "110", "434", "22", "132", "158", "208",
        "528", "39", "554", "572", "675", "122", "641", "624", "499", "228", "548", "20", "587", "196", "399",
        "34", "478", "102", "12", "452", "207", "173", "63", "84", "477", "679", "172", "465", "371", "404",
        "625", "199", "148", "588", "357", "369", "519", "592")
    easyCLI.uiHeader()
    rawMessage=("p", "7", "V", "*", "W", "E", "%", "Y", "l", "i", "b", "&", "l", "V", "E", 
        "T", "w", "B", "4", "M", "s", "p", "i", "a", "H", "Z", "o", "#", "c", "o",
        "<", "w", "U", "k", "O", "(", "{", "o", "Z", "U", "b", "M", "W", "H", "W",
        "|", "W", "%", "1", "a", "M", "5", ">", "A", "#", "=", "a", "f", "A", "i",
        "C", "&", "o", "O", "c", "k", "%", "$", "!", "U", "v", "H", "O", "V", "Y",
        "{", "-", "l", "Q", "Z", "{", ")", "5", "c", "y", "-", "(", "o", "N", "E",
        "W", "3", "Z", "c", "G", "?", "g", "p", "4", ">", "3", "a", "5", "`", "=",
        "l", "X", "U", ";", "E", "w", "e", "*", "E", "b", "0", "Q", "?", "V", "d",
        "$", "_", "J", "J", "W", "i", "L", "V", "N", "I", "r", "$", "f", "G", "R",
        "b", ")", "J", "N", "$", "E", ";", "Q", "k", "X", "h", "W", "p", "s", "C",
        "L", "Y", ">", "!", "3", "V", "6", "^", "{", "G", "W", "~", "0", "i", "L",
        "L", "P", "7", "}", "D", "g", "}", "Y", "n", "#", "Z", "N", "8", "Q", "M",
        "a", "P", "b", "j", "-", "Z", "x", "k", "c", "<", "k", "!", "~", "}", "3",
        "E", "j", "$", "f", "a", "3", "V", "7", "F", "o", "-", "8", "D", "8", "}",
        "g", "b", "8", "F", ";", "p", "$", "A", "G", "_", "u", "c", "}", "z", "K",
        "Y", "w", "E", "3", ">", "L", "$", "`", "l", ";", "o", "b", "E", "T", "W",
        "Q", "R", "^", "d", "J", "X", "%", "L", ")", "X", "o", "g", "3", "-", "(",
        "W", "k", "p", "R", "V", "W", ";", "b", "M", "P", "k", "M", "F", "6", "{",
        "A", "8", "a", "Z", "V", "$", "P", "s", "0", "b", "s", "b", "V", "K", "K",
        "Y", "Y", ";", "I", "y", "a", "5", "F", "|", "b", "W", "E", "X", "9", "Y",
        "R", "=", "c", "c", "#", "V", "k", "c", "R", "!", "H", "z", "F", "4", "E",
        "{", "{", "q", "c", "Z", "X", "M", "T", "E", "x", "i", "B", "-", "K", "R",
        "z", "H", "B", "P", "M", "O", "A", "Y", "0", "$", "T", "y", "9", "p", "a",
        "i", "-", "g", "}", "Q", ";", "=", "5", "$", "W", "q", "f", "a", "s", "*",
        "Z", "S", "_", "(", "@", "$", "W", "-", "8", "T", "X", "T", "B", "c", "+",
        "x", "W", "l", "i", "6", "A", "k", "Q", "x", "a", "i", "O", "T", "<", "B",
        "L", "b", "b", "8", "a", "e", "b", "w", "}", "0", ">", "N", "y", "x", "u",
        "9", "S", "g", ">", "!", "#", "d", "7", "O", "L", "g", "R", "2", "X", "$",
        "R", "M", "y", "b", "E", "5", "a", "V", "B", "&", "E", "U", "B", "C", "$",
        "7", "X", "O", "u", "L", "Z", "B", "g", "{", "2", "k", "X", "E", "o", "E",
        "Q", "^", "X", "Z", "V", "B", "7", "b", "A", "l", "+", "b", "c", "p", "Z",
        "A", "7", "n", "0", "I", "J", ")", "Y", "P", "c", "6", "?", "!", "Q", "`",
        "I", "8", "*", "`", ">", "*", "X", "0", "#", "0", "6", "k", "C", "T", "E",
        "(", "U", "#", "=", "$", "q", "X", "i", "x", "E", "J", "+", "5", "U", "x",
        "K", "2", "d", "=", "E", "9", "d", "e", "o", "*", "b", "2", "b", "i", "<",
        "U", "k", "j", "u", "i", "D", "W", "4", "{", "_", "3", "w", "Z", "b", "%",
        "b", "N", "b", "6", "0", "j", "C", "Q", "%", "U", "G", "7", "n", "M", "D",
        "O", "N", "v", "R", "g", "A", "b", "K", "R", ">", "W", "*", "{", "=", "F",
        "p", "}", "A", "V", "B", "W", "X", "s", "W", "O", "7", "M", "i", "i", "(",
        "V", "z", "N", "u", "Q", "N", "{", "G", "w", "i", "E", "=", "P", "c", "E",
        "X", "L", "T", "s", "b", "E", "g", "i", "a", "1", "4", "&", "c", "K", "X",
        "K", "p", "Y", "&", "_", "2", "_", "C", "S", "M", "V", "I", "7", "b", "b",
        "e", "x", "u", "b", "}", "R", "4", "m", "O", "W", "-", "*", "&", "Z", "b",
        "b", "|", "{", "x", "M", "u", "L", "g", "x", "a", "?", "A", "8", "y", "O",
        "-", "z", "_", "g", "k", "i", "n", "A", "H", "7", "B", "~", "P", "N", "U",
        "M", "X", "n", "T", "`", "6", "3", "k")
            


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

