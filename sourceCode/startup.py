   
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
    integrity1=([13, 7, 16, 20, 19, 2, 1, 22, 4, 26, 0, 10, 11, 25, 5, 17, 23, 6, 21, 3, 27, 28, 29, 18, 9, 24, 12, 14, 8, 15], 
    [0, 59, 68, 64, 16, 30, 13, 73, 71, 3, 5, 34, 66, 38, 12, 2, 15, 63, 31, 14, 72, 69, 79, 42, 39, 61, 57, 40, 28, 65, 67, 25, 77, 17, 75, 46, 10, 62, 11, 53, 37, 32, 33, 4, 48, 35, 6, 9, 29, 23, 1, 60, 56, 74, 50, 51, 58, 55, 20, 45, 78, 19, 18, 21, 47, 36, 22, 44, 7, 27, 54, 26, 49, 43, 8, 70, 24, 76, 41, 52], 
    [10, 48, 84, 81, 8, 52, 71, 11, 21, 62, 65, 4, 24, 69, 79, 78, 56, 58, 50, 61, 45, 57, 60, 63, 32, 80, 72, 35, 53, 83, 38, 46, 77, 64, 29, 55, 76, 30, 37, 28, 19, 59, 43, 5, 36, 39, 40, 74, 17, 7, 73, 70, 26, 9, 20, 47, 6, 68, 3, 13, 31, 85, 1, 34, 33, 41, 12, 75, 49, 54, 22, 66, 14, 0, 2, 25, 27, 82, 67, 44, 23, 42, 15, 51, 18, 16],
    [23, 22, 8, 11, 1, 6, 4, 7, 19, 17, 12, 13, 9, 0, 20, 26, 15, 21, 10, 5, 2, 14, 3, 24, 28, 18, 16, 27, 25],
    [62, 33, 67, 15, 27, 61, 26, 76, 7, 79, 6, 78, 12, 71, 8, 43, 38, 1, 46, 65, 0, 22, 9, 29, 41, 10, 45, 19, 37, 14, 52, 42, 56, 3, 59, 24, 69, 34, 53, 40, 47, 30, 60, 63, 20, 70, 28, 36, 23, 16, 64, 77, 5, 44, 13, 74, 57, 75, 72, 39, 25, 21, 17, 48, 4, 32, 58, 68, 66, 50, 73, 11, 2, 35, 55, 54, 49, 51, 31, 18],
    [32, 50, 4, 68, 3, 30, 24, 22, 43, 44, 83, 84, 11, 49, 55, 38, 69, 85, 77, 61, 19, 73, 33, 25, 5, 16, 14, 37, 75, 79, 51, 82, 10, 8, 35, 2, 45, 40, 31, 57, 48, 62, 39, 6, 42, 64, 56, 53, 67, 12, 34, 26, 7, 63, 29, 20, 54, 59, 41, 78, 76, 70, 72, 58, 1, 13, 47, 0, 28, 36, 80, 18, 17, 21, 66, 81, 27, 60, 23, 65, 74, 71, 15, 46, 52, 9],
    [23, 9, 3, 11, 14, 6, 12, 7, 28, 21, 25, 19, 8, 18, 5, 1, 27, 26, 17, 4, 10, 24, 13, 2, 15, 0, 20, 16, 22],
    [72, 16, 48, 34, 77, 50, 71, 79, 21, 27, 65, 54, 43, 31, 59, 67, 41, 40, 76, 75, 49, 20, 18, 36, 37, 61, 24, 68, 11, 26, 19, 6, 2, 44, 13, 17, 53, 15, 64, 5, 38, 33, 74, 52, 32, 63, 42, 78, 3, 14, 7, 39, 56, 12, 22, 30, 58, 73, 51, 1, 55, 0, 8, 46, 62, 57, 23, 60, 66, 25, 4, 70, 10, 29, 47, 45, 69, 28, 35, 9],
    [34, 16, 21, 39, 23, 45, 66, 82, 17, 85, 68, 59, 19, 47, 48, 84, 12, 18, 50, 60, 9, 8, 58, 49, 72, 22, 46, 75, 25, 7, 65, 5, 40, 69, 3, 67, 33, 55, 77, 27, 80, 10, 63, 36, 28, 29, 73, 14, 81, 71, 52, 30, 15, 51, 79, 38, 31, 35, 11, 0, 61, 43, 83, 62, 13, 37, 26, 20, 53, 41, 57, 56, 6, 64, 74, 44, 70, 24, 76, 2, 78, 54, 4, 32, 42, 1],
    [5, 33, 14, 10, 22, 4, 3, 36, 35, 7, 25, 18, 29, 32, 12, 20, 9, 19, 21, 30, 13, 31, 24, 0, 6, 8, 23, 26, 16, 27, 1, 15, 2, 11, 28, 17, 34],
    [75, 62, 9, 3, 14, 26, 42, 50, 69, 18, 76, 57, 38, 17, 30, 12, 39, 51, 4, 48, 25, 52, 61, 5, 53, 35, 22, 63, 46, 49, 55, 28, 67, 20, 7, 70, 32, 43, 44, 11, 56, 66, 0, 36, 27, 73, 74, 59, 64, 24, 19, 60, 8, 65, 29, 21, 71, 58, 40, 37, 1, 41, 72, 31, 10, 77, 15, 33, 16, 54, 23, 13, 68, 47, 45, 34, 79, 78, 6, 2],
    [1, 73, 10, 85, 82, 53, 23, 74, 40, 19, 69, 30, 54, 8, 51, 49, 60, 50, 28, 55, 61, 37, 62, 7, 57, 48, 63, 59, 78, 32, 20, 13, 52, 21, 79, 17, 22, 80, 6, 11, 71, 44, 83, 4, 33, 65, 76, 25, 24, 39, 70, 34, 84, 81, 12, 41, 16, 72, 47, 27, 68, 64, 18, 43, 26, 67, 31, 77, 56, 9, 0, 5, 45, 3, 14, 15, 38, 42, 29, 2, 46, 66, 36, 75, 58, 35],
    [10, 16, 6, 3, 24, 13, 46, 12, 35, 23, 0, 5, 2, 36, 34, 11, 43, 27, 40, 14, 30, 38, 32, 7, 39, 44, 17, 42, 29, 18, 41, 31, 15, 33, 37, 28, 21, 47, 45, 1, 8, 25, 26, 20, 19, 22, 4, 9],
    [0, 27, 44, 61, 21, 9, 33, 38, 70, 36, 24, 16, 77, 31, 28, 43, 66, 55, 5, 39, 62, 26, 6, 53, 74, 52, 3, 48, 71, 18, 42, 56, 41, 73, 10, 12, 11, 34, 19, 30, 63, 49, 57, 78, 45, 72, 13, 67, 8, 29, 1, 75, 22, 25, 35, 60, 15, 59, 20, 14, 17, 65, 68, 4, 51, 79, 2, 7, 58, 46, 64, 23, 69, 40, 32, 50, 47, 54, 76, 37],
    [7, 75, 3, 12, 17, 66, 78, 56, 68, 14, 43, 25, 13, 5, 82, 80, 38, 34, 77, 72, 70, 8, 41, 22, 44, 21, 6, 32, 64, 36, 23, 26, 59, 30, 81, 84, 16, 9, 67, 2, 42, 85, 1, 71, 53, 39, 55, 4, 27, 51, 37, 0, 10, 74, 54, 45, 52, 83, 49, 62, 18, 15, 19, 79, 57, 11, 48, 76, 63, 31, 29, 50, 46, 65, 73, 47, 35, 40, 20, 60, 33, 24, 61, 69, 58, 28],
    [32, 17, 13, 28, 36, 27, 12, 10, 15, 4, 19, 9, 34, 31, 8, 1, 18, 24, 5, 16, 20, 33, 29, 26, 14, 25, 7, 2, 0, 22, 3, 35, 23, 11, 30, 6, 21],
    [74, 25, 70, 26, 9, 38, 78, 37, 77, 31, 24, 28, 27, 16, 1, 2, 61, 49, 21, 45, 29, 8, 35, 10, 56, 6, 13, 47, 57, 71, 62, 11, 59, 64, 79, 44, 73, 43, 66, 19, 42, 75, 20, 32, 68, 22, 14, 5, 36, 4, 48, 34, 18, 41, 76, 54, 7, 40, 50, 55, 72, 39, 12, 0, 67, 53, 60, 15, 3, 30, 51, 33, 46, 52, 69, 58, 65, 23, 63, 17],
    [24, 56, 37, 43, 61, 12, 54, 75, 72, 67, 59, 62, 35, 80, 20, 52, 74, 66, 84, 28, 76, 2, 14, 71, 47, 78, 79, 51, 64, 82, 60, 3, 25, 58, 49, 11, 39, 55, 15, 1, 44, 63, 42, 22, 40, 36, 45, 6, 50, 31, 32, 34, 21, 30, 26, 10, 16, 46, 33, 4, 68, 7, 0, 41, 8, 57, 85, 5, 9, 38, 18, 81, 17, 27, 73, 53, 23, 83, 77, 69, 65, 13, 29, 19, 70, 48],
    [2, 33, 32, 29, 5, 14, 24, 25, 16, 19, 21, 40, 34, 7, 31, 9, 37, 11, 6, 15, 0, 13, 10, 23, 26, 17, 41, 8, 20, 30, 4, 3, 22, 35, 28, 27, 1, 12, 36, 18, 39, 38],
    [69, 63, 40, 54, 67, 19, 52, 30, 12, 57, 32, 6, 1, 22, 41, 43, 16, 78, 75, 50, 70, 26, 49, 59, 73, 47, 17, 65, 39, 7, 4, 77, 61, 20, 51, 14, 46, 72, 53, 27, 60, 9, 37, 18, 2, 62, 56, 35, 71, 28, 3, 38, 33, 10, 58, 44, 13, 45, 79, 64, 11, 31, 36, 21, 25, 68, 34, 76, 24, 5, 42, 55, 48, 15, 66, 0, 74, 29, 8, 23],
    [77, 8, 59, 57, 15, 12, 36, 72, 28, 65, 2, 84, 76, 47, 48, 69, 83, 54, 60, 19, 22, 16, 21, 13, 73, 56, 74, 68, 9, 20, 14, 25, 44, 66, 27, 49, 55, 53, 63, 26, 46, 0, 29, 31, 52, 5, 79, 41, 4, 81, 43, 35, 10, 39, 11, 18, 34, 67, 51, 6, 62, 64, 85, 23, 45, 33, 42, 1, 40, 80, 82, 30, 37, 38, 75, 7, 17, 32, 71, 78, 3, 70, 61, 58, 50, 24],
    [28, 11, 2, 12, 5, 27, 9, 20, 10, 25, 4, 21, 16, 7, 17, 13, 1, 18, 26, 29, 0, 14, 30, 19, 24, 31, 6, 23, 8, 3, 15, 22],
    [49, 72, 47, 42, 10, 78, 26, 0, 40, 18, 53, 9, 69, 61, 58, 71, 62, 36, 8, 17, 1, 65, 30, 39, 38, 73, 68, 52, 67, 34, 31, 44, 51, 35, 3, 28, 19, 63, 32, 4, 22, 57, 25, 70, 75, 76, 56, 59, 24, 15, 6, 77, 33, 54, 37, 46, 64, 45, 12, 21, 74, 2, 50, 66, 79, 43, 27, 41, 55, 13, 23, 11, 5, 29, 48, 20, 14, 60, 16, 7],
    [61, 17, 66, 80, 41, 15, 5, 21, 58, 6, 49, 43, 83, 44, 10, 59, 85, 1, 16, 48, 9, 56, 54, 24, 38, 78, 65, 71, 73, 25, 79, 62, 76, 3, 40, 11, 45, 75, 19, 30, 2, 13, 23, 39, 50, 28, 14, 7, 60, 52, 0, 8, 51, 18, 47, 42, 77, 12, 74, 20, 35, 46, 37, 55, 64, 26, 36, 72, 67, 69, 84, 32, 29, 34, 4, 22, 27, 57, 68, 82, 53, 33, 81, 70, 63, 31])
    
    integrity2=(">hlM6pnU9_WM^ELf&rNu8Tw#6iHN6E",
        "WAjFiIakBaVnax;wWdAi7k5wFAvWkHIF`TV5Gd%BPLT8BIm~XanI>YVPfVGI6{}&lXeE3%i)7m4Gm_Mr", "@@!u~54--fMn8!9{8sOjW=TBVj^3r_9p3iVbj(mx(;c7t1rVoArovrhdO###kpICoB@C`G<`^r{G|>^GLa64rh", "o$|--E6PU4WQvYPaOEOZwOVL?pi-b", "IGWV+aBAxCDa3P$PkHXHW{6ZlHIz@XhiBcjA`e+V5HHvVV?(}`nUHf<jsI!oGqX$wNjx8GK8vHGY8BDG",
        "`gxVtQI?>LXdUS)c)7^1BFdDNh45(RK=OZn>Mr*<LtWj!q_U&lxfU47T}$Ra)p!%rfJzP=pS(jNPH=uJbbC30>", "oiV-O8WK?EbU`pb--a46OLQwOYPi$", "}-?kDH5Zl#G5Gi~Y8H&GVVHPZWhOo50K95!~VWDVB>v9T+V3ynOiK9pW!f#@VWj8;X#I-IDIWmCHCyVf", "gkAMGIV<~BrrI@woi?A4#@@?zmt67QzD82#U0#i>pL#yiYxrTP8)xfl@CIH2&C~!cUOi*Tr=1ik!}v%3%yAMOo",
        "ExcE3K*NbaLeg{)W7CiM}JeYkXoq+$<YOi$-B", "HJh|_=RWmJ#-<(Gv_-}zF?jH)FsD%ZV7xHoWhCYkP!GkaK4kHF2WyHh#iHI&BWvBFaH<!A?<;zGY7qZz", "fnr8PQ?zfhuV2^6%iBr?ZL;8KSs|YIz>y_6mJ839JLUwQq~Fr>7HMhOy$Uig!ZVZK#au}MEoeo5AZT-idCPY^d", "P=;T>Ky3NzOYckj<RdQ#E_)0Wx5;u!$-X=c_=sc>jb7X+7>I",  
        "V7tGAb8{V#raHKF-bWFpZc=E98-c`pIH@aHa#8oV|}eWFe$%-AKWmIHGHpIBRI3{K2p8zg^r7WzV95jA", "OFO$nO8zNbl|uZrB)9Y9?5Yr<76ZS9<iX^;}94~fWj^@-&nx6O3m8L}%Rbhn5wn2pjX117&dcNj64-`{PMbrz<", "{2L$N$9aW?;xBJ)Iu;YiFxgq;LfYPBNb|AMhf", "AHH#4xtRR`m8Tai~ZFhH6VVVM5NCpDwmu|873ed1RHG56tAIPCgsS5#$0IWWP2CWDeHHlV@=fKhAG&30",
        "y9p)lAhuk|3Nmd>q&-K#Mb`p=m#{g)_r<IHm5Uga3z(ws5M$UFUtrH~4?SY6gAlKN3HhovhI%3`}XU~!-_EP$Q", "6$$;c>;FA;ibgDqG{mXaP+Xuf9NZWL&m2M|B;lJLBx", "pQVd{W(H1yRi@Gm3WWVHHB8hU$RIev9daG!khn3-H|-CIT=G83s6mFyxvG3DlaBiG>h>iWWV_IWWfdA8", "0a#X{F+zuX;G^E2}t{DV{f#5;WVf9aG}m$Uuy7FXNM`0*4t1(M>IA*LCG}PT#xnfSCx*9XlJf!fp@83+paRqmy",
        "x$e|Z{6LQM{qAD&c<FJBPJb=gN*$DDG$", "}q1(WIeWWR3DEBtB;n`riWWuo?haKw@u=W*nEs9d(GHGWjBXdViS%}w54ID!eTF@v%xMGwIHWr@HlGP?", "@)JK%)DIYz*-RuN=Hg_Ox`^uVm5<8OntY@2YTpXfBE7M10ucp_a~imdstx-T?3!M$6lo&=;C=D%6QXiBga#%{?")
    
    
    folderAndLicense=("o$OU4piwEP", [8, 7, 0, 4, 2, 3, 1, 9, 6, 5], "pEia?oU-4PO$Lb", [3, 6, 1, 11, 13, 8, 4, 12, 2, 5, 0, 7, 9, 10])

    integrity3=([4, 6, 70, 26, 50, 13, 7, 24, 63, 1, 60, 38, 57, 39, 74, 68, 54, 66, 46, 65, 49, 19, 44, 16, 77, 15, 21, 5, 29, 36, 22, 53, 58, 11, 32, 55, 3, 75, 27, 76, 73, 78, 71, 18, 59, 20, 33, 40, 10, 64, 35, 0, 30, 41, 28, 37, 62, 9, 61, 23, 12, 79, 47, 51, 67, 25, 31, 2, 48, 8, 69, 72, 45, 52, 34, 42, 17, 43, 56, 14],
        [56, 59, 81, 39, 3, 16, 64, 47, 26, 69, 50, 21, 61, 19, 42, 71, 43, 54, 41, 28, 68, 77, 79, 22, 33, 0, 11, 6, 53, 29, 35, 51, 70, 18, 8, 38, 60, 1, 9, 85, 75, 2, 62, 78, 73, 72, 37, 30, 10, 7, 25, 82, 74, 76, 17, 20, 55, 5, 15, 52, 36, 40, 84, 48, 46, 83, 34, 49, 45, 44, 57, 80, 24, 32, 23, 58, 67, 65, 27, 12, 66, 14, 13, 31, 4, 63])

    integrity4=("ucGaH0`my;H|jDkgpcqGm26KIVkGbh(sp>IFaFIlvJ&^0FdHV~GWI8X$A4f4oo!a#H5t8Dl5VRiegM*p",
        "pJ%w6M<(Qn95ubnKfN(YDmw7u4PY3_?^WYVa%Qb`xxE@Rr@JKFs!vs)L~6|iP-F2BAa~=Png%-Pz8KaM^`(9S=")


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
        self.vNumber="v1.3.2"
        self.vString="Yahoo Finance Historical Data Downloader "+self.vNumber+" by redcacus5"+"\n\n"

    def drawUIHeader(self):
        easyCLI.clear()
        print(self.vString)
    
#securityMessage
def badCrash()->None:
    lookup=("413",
        "160", "453", "296", "405", "215", "202", "506", "291", "208", "369", "554", "121", "77", "1", "140", "387", "435", "544", "549", "153",
        "196", "604", "555", "131", "277", "588", "241", "67", "43", "637", "316", "417", "120", "490", "458", "416", "4", "323", "493", "73",
        "72", "541", "534", "553", "502", "381", "575", "497", "367", "594", "117", "201", "187", "210", "451", "439", "142", "579", "36", "362",
        "454", "228", "480", "444", "106", "613", "585", "213", "174", "462", "337", "164", "638", "366", "340", "265", "146", "590", "508", "75",
        "463", "346", "125", "576", "627", "361", "364", "112", "630", "348", "532", "158", "610", "221", "240", "350", "589", "31", "161", "477",
        "331", "615", "9", "95", "393", "398", "118", "170", "389", "182", "128", "471", "519", "92", "135", "584", "495", "628", "299", "314",
        "467", "408", "15", "459", "122", "356", "341", "235", "326", "509", "552", "328", "10", "264", "24", "443", "119", "236", "180", "600",
        "200", "623", "420", "551", "151", "60", "217", "288", "212", "306", "446", "267", "26", "284", "220", "85", "391", "188", "385", "521",
        "18", "343", "339", "478", "603", "78", "550", "88", "253", "430", "23", "324", "124", "564", "624", "372", "19", "601", "395", "294",
        "13", "169", "441", "494", "528", "147", "162", "543", "98", "181", "394", "177", "83", "111", "62", "486", "412", "539", "80", "312",
        "283", "511", "70", "559", "598", "440", "39", "358", "349", "289", "633", "573", "489", "634", "376", "103", "154", "560", "383", "515",
        "586", "178", "530", "491", "260", "218", "27", "281", "261", "61", "137", "219", "292", "304", "336", "469", "148", "410", "597", "270",
        "0", "90", "321", "403", "605", "419", "250", "223", "35", "382", "406", "303", "276", "392", "527", "3", "113", "89", "192", "302",
        "114", "431", "464", "429", "565", "571", "20", "626", "351", "129", "134", "29", "631", "57", "224", "216", "48", "258", "536", "335",
        "592", "474", "516", "587", "342", "617", "513", "548", "365", "168", "197", "436", "297", "578", "606", "338", "243", "620", "159", "402",
        "30", "537", "239", "520", "558", "510", "285", "238", "378", "101", "152", "531", "259", "204", "371", "257", "574", "198", "591", "229",
        "481", "505", "545", "179", "7", "496", "63", "247", "373", "272", "14", "507", "96", "418", "246", "499", "275", "130", "269", "401",
        "156", "317", "465", "99", "421", "245", "32", "97", "602", "500", "577", "282", "79", "309", "556", "363", "540", "268", "65", "535",
        "167", "596", "608", "404", "567", "105", "424", "635", "561", "614", "21", "93", "482", "542", "360", "278", "311", "379", "447", "445",
        "42", "175", "611", "625", "533", "286", "205", "189", "157", "74", "399", "209", "397", "470", "273", "414", "40", "547", "2", "487",
        "522", "280", "355", "409", "8", "139", "305", "484", "116", "422", "347", "25", "512", "185", "104", "37", "45", "262", "165", "227",
        "194", "438", "375", "28", "46", "207", "308", "248", "411", "44", "629", "230", "428", "632", "433", "16", "71", "407", "580", "110",
        "498", "546", "166", "557", "266", "423", "50", "53", "384", "68", "523", "127", "203", "492", "526", "143", "475", "47", "330", "244",
        "226", "49", "374", "569", "176", "503", "525", "191", "518", "333", "566", "307", "344", "313", "442", "233", "55", "388", "621", "370",
        "102", "195", "357", "263", "133", "386", "612", "17", "183", "319", "562", "461", "479", "144", "252", "87", "457", "472", "315", "34",
        "318", "52", "329", "107", "38", "334", "570", "138", "232", "466", "622", "298", "636", "455", "254", "295", "434", "616", "255", "12",
        "108", "56", "529", "432", "359", "572", "86", "538", "327", "69", "427", "33", "136", "352", "618", "141", "41", "310", "450", "425",
        "460", "91", "368", "199", "582", "293", "320", "476", "390", "345", "287", "149", "332", "214", "242", "211", "94", "225", "249", "595",
        "426", "456", "84", "300", "377", "619", "563", "301", "155", "396", "609", "22", "54", "150", "400", "599", "186", "11", "251", "171",
        "237", "354", "607", "279", "58", "380", "81", "322", "234", "76", "109", "184", "583", "448", "504", "593", "64", "222", "449", "437",
        "568", "488", "231", "115", "145", "415", "353", "274", "452", "473", "290", "325", "485", "206", "483", "132", "126", "100", "256", "172",
        "501", "271", "173", "524", "51", "66", "6", "5", "514", "59", "468", "163", "517", "193", "190", "581", "123", "82")
    easyCLI.uiHeader()
    rawMessage=("K", 
        "i", "N", "Q", "R", "i", "l", "K", "h", "Q", "Q", "a", "*", ">", "$", "n", "Y", "y", "~", "Z", "Z",
        "9", "&", "_", "p", "E", "E", "W", "!", "k", "B", "}", "E", "b", "b", "v", "=", "}", "f", "w", "H",
        "L", "<", "x", "T", "&", "w", "0", ">", "j", "%", "&", "A", "K", "2", "a", "5", "O", "o", "Q", "g",
        "k", "L", "O", "X", "E", "*", "7", "-", "b", "F", "&", "C", "8", "W", "H", ">", "Y", "Z", "a", "X",
        "U", "R", "Z", "N", "8", "V", "B", "b", "b", "=", "c", "b", "U", "X", "#", "0", "Y", "Z", "A", "Z",
        "=", "Z", "e", "Y", "F", "k", "@", "D", "{", "p", "Q", "x", "l", "c", "9", "1", "a", "g", "b", "+",
        "-", "b", "!", "O", "R", "1", "3", "<", "z", "8", "E", ">", ";", "u", "H", "4", "H", "-", "B", "5",
        "c", "n", "y", "H", ">", ";", "$", "7", "Q", "p", ")", "-", "(", "p", "`", "c", "_", "M", "i", "V",
        "b", "Z", "U", ";", "B", "g", "P", "O", "A", "$", "V", "B", "%", "z", "i", "A", "L", "{", "G", "d",
        "X", ")", "`", "c", "b", "8", "T", "{", "x", "U", "X", "!", "E", "l", "R", "a", "R", "W", "M", "$",
        "(", "%", "X", "{", "w", "C", "g", ">", "a", "S", "R", "i", "7", "I", "E", "#", "x", "4", "V", "4",
        "b", "o", "G", "N", "?", "V", "s", "0", "9", "u", "Z", "G", "`", "L", "c", "a", "S", ")", "(", "-",
        "X", "k", "H", "X", "W", "2", "O", "=", "g", "W", "W", "0", "M", "L", "i", "a", "7", "E", "8", "w",
        "g", "-", "E", "$", "d", "Y", "Y", "c", "J", "b", "R", "W", "j", "U", "X", "e", "L", "O", "Z", "o",
        "P", "*", "!", "3", "O", "N", "f", "c", "O", "{", "F", "W", "3", "I", "P", "u", "7", "i", "w", "V",
        "W", "x", "p", "C", "o", "<", "5", "^", "&", "X", "A", "$", "T", "N", "b", "A", "7", "}", "}", "6",
        "J", "B", "N", "X", "D", "A", "7", "*", "T", "!", "b", "V", "{", "E", "U", "4", "V", "4", "b", "W",
        "g", "$", "k", "#", "c", "l", "u", "0", "E", "?", "6", "-", "{", "8", "=", "+", "k", "L", "i", "K",
        "f", "a", "T", "5", "J", "0", "7", "P", "5", "q", "A", "i", "V", "#", "I", "o", "I", "T", ";", "3",
        "#", "2", "y", "K", "n", "X", "E", "k", "W", "V", "V", "K", "E", "p", "|", "b", "M", "A", "$", "b",
        "n", "#", "q", "2", "i", "D", "U", "*", "i", "(", "0", "P", "O", "k", "G", "W", "_", "X", ";", "V",
        ">", "8", "_", "B", "j", "`", "x", "X", "Y", "M", "|", "M", "=", "K", "E", "R", "(", "V", "a", "U",
        "-", "-", "(", "F", "p", "C", "i", "k", "s", "o", "%", "N", "b", "W", "N", "5", "d", "2", "O", "<",
        "V", "U", "e", "$", "}", "|", "7", "M", "p", "C", "E", "Z", "*", "z", "g", "x", "s", "k", "Y", "_",
        "8", "V", "A", "W", "{", "$", "_", "g", "c", "b", "r", "Z", "=", "D", "d", "o", "b", "Y", "X", "*",
        "L", "&", "{", "U", "Z", "s", "9", "~", "k", "Z", "J", "x", "u", ">", "a", "o", "3", "y", "F", "$",
        "Q", "i", "W", "B", "3", "=", "c", "{", "6", "W", "k", "Q", "`", "W", "M", "Y", "c", "7", "Q", "Q",
        "w", "B", "W", "a", "E", "Z", "=", "M", "M", "T", "O", "l", "$", "l", "b", "R", "j", "X", "s", "A",
        "a", "P", "M", "l", "S", "i", "$", "0", "I", "P", "E", "}", "g", "i", "b", "a", "b", "o", "G", "6",
        "8", "6", "}", "b", "c", "0", "5", "b", "f", ";", "E", "}", "u", "n", "J", "E", "%", "m", "_", "M",
        "v", "F", "T", "N", "W", "d", "4", "s", "z", "^", "^", "T", "*", "s", "b", "K", "y", "z", "k", "L",
        "E", "w", "b", "N", "%", "g", "{", "6", "b", "p", "R", "B", "A", "P", "R", "6", "3", "?")
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


 
