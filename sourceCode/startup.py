   
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



def configureLicense(scrambledList: str, indexMap: list[int]) -> str:
    restored = [""] * len(indexMap)
    listedScrambledEggs=tuple(scrambledList)
    for scrambledIndex, originalIndex in enumerate(indexMap):
        restored[originalIndex] = listedScrambledEggs[scrambledIndex]
    return "".join(restored)



def licenseCheck()->int:
    integrity1=("i6E#_&9ET6Wf8nMH6lN>MwupUNhr^L",
        "kYzhKWWV&LBvM$V#&Z4jGmb}WPsfCsjHDncolW<!GIGoj(H*Tu5#GpHMViv4BV8=1n-WZ8b<^5H0F@`P", "?4Wyb7A%M9lf!Jz<IY=J&-HC7#azWqpnBR%Vvuh3<M5<{z~3ekV=Y({Ex+Zaop7)!+f#7GqwnlD$}^5BV~-EuL", "O-P6aOvO-o$|wib-LVQYp?EWE4ZPU", "L~)QwF4g6>GIRowVVaHH2fq{IAkHmmMGgbGOc?sK;3W5+IHvWW7IMIRMj~V8ueGk-s=dERkM)Ac-QX5B",        
        ";LT``u4Uu@@`nHv$sf2BAyCra{_<dcb47qdhZV46^07UOAs_;Qbuk5rDc<_vJM7-%C{=wPuov&yVl)vAG8y0nz", "bOi-QOwYiWP`b?L84$K-Vpoa-OEU6", "b8e4jW;Z!|m)Hh2H*^lhKUVLGHEj8W`UW*GZ2?ILPI7HfKWK=UG>ViV`A@#Nq?RV`5BVbI3qIy{HUiAV", ">SoV7g5}HpR#)Dm!ga9P(1)eUjVu^H!KYHKMe=JV3pOHTY$x!`l1-yT-)V80dlvEz|T#w2|5UcXKG)lp`Gc{l-",  
        "BJ)-X$bEYY}7Ckaieg*K$c<Lo{MiWxE+3eONq", "@_|c*?#jW7KHVBo0=56He1HHrVIVewk{SWYGIGG|IlZ`4nF5tKRdm&qH}I}F=10YX!WPVf}`zWWUe0mD", "G<G_&O9T|!C8Ekx8@PvX}-Y?t<3BA90?Bx^3Ds8%CX-NDh3%h)PL2&3Wd%n68Hx5f-ACL()pfuL6PO2O;<kT?)", "+ycT>3uX0W=#cY7_$-kd=jX<x>!j7sz>;=5)PKcNOQ;ERbI_",
        "m>Vbbc9VVVH<ZFmUPKNBpGa5Gl&AEG?KIH$C6I!3bBhH+nk@A6IsHFV7=?b<sk`K}Gw8VmIf5il=^GgS", "I9#<u<E&h5i7Vx-C`*XCabKlNn{gCKpvyeHsL%H-~W<%Q19KPe9<>u|rhV3im0G<|3!Ina6m{lN9<&HgbrHT@9", "gL?Y;;MhWaiAL$NuPJ);xxBY9qIBN$f|f2bF{", "ZUI}HIBCk)59zWG9R~ebF}WMP6H557&|Ap7W>Qi78HWI-)G*I+LmB}II_A(XD5I{M2k=%Fgzt#yS6Td=",
        "@g7yD`;fK~;O8^=}pZ66K^Vs|<|}z(O4$WC>Qs~5{$RJkX?VD#!4FI_WPGh@Kq{9u>C*_I`0|ye`S3j(H=N3ia", "bm|NF2W$Pi6&xu+J;;GcZl{;mqD>9XL;XLB$BaMAgf", "HfB)6G5AVPHcFmAN(6=HGh~)<f+F+VFVDfZWF*^Vp?i>GAR`b0WHdjltI6>$W!mGAq3jVHtAVHNf>Hpm", "Ff{V)5;r_+WsVL;}4xpb)JwRl<It87*e-ncqEy?j)BO-zL4p+2R%e2rj;ynJ`svG2fF~=<|fs^y-lB%kO<Nc#Y",
        "MBb<Q$g6D*PZ{D&xL$D$c|eG{=JFJNAq", "TBK9Dgb;|oWZccKVUHar4p8m-VNW9mHsGH@i2$WqHAl?N5nG1uWfABiHG?%hF#Fn`4CGQT&3{Vq&K?-I", "kvZ-BRA`T?57n>ZHFfg#6+hL<_nX{UVcVLOqjFQ|f`<{9!K<Jr;cghNu#=LzhPM0}%9Hnpd?S$4Bmvx%?y$X=k")
    
    integrity2=([24, 9, 25, 18, 26, 23, 4, 15, 28, 8, 0, 17, 27, 1, 20, 12, 19, 16, 14, 13, 10, 29, 3, 2, 22, 21, 7, 6, 11, 5],
        [12, 72, 42, 14, 47, 35, 25, 55, 51, 21, 32, 53, 36, 23, 20, 61, 7, 63, 9, 79, 10, 19, 68, 77, 45, 38, 57, 76, 39, 34, 24, 43, 41, 26, 2, 54, 62, 0, 73, 49, 50, 65, 11, 44, 67, 27, 30, 13, 18, 59, 66, 31, 70, 37, 40, 17, 48, 1, 64, 22, 71, 15, 8, 58, 69, 29, 6, 5, 28, 33, 74, 78, 3, 52, 60, 4, 75, 46, 16, 56],
        [0, 11, 37, 83, 5, 19, 67, 32, 51, 30, 84, 46, 22, 62, 9, 42, 54, 53, 50, 26, 77, 70, 76, 55, 82, 2, 20, 79, 68, 72, 12, 40, 6, 41, 4, 69, 35, 36, 28, 43, 52, 85, 75, 81, 21, 73, 33, 10, 44, 78, 25, 58, 45, 56, 31, 66, 80, 39, 1, 74, 64, 7, 17, 38, 49, 65, 71, 29, 57, 14, 24, 48, 61, 34, 15, 47, 18, 27, 63, 23, 8, 59, 16, 13, 3, 60],
        [14, 27, 7, 4, 26, 10, 9, 15, 1, 23, 22, 8, 2, 16, 25, 11, 24, 3, 13, 0, 18, 28, 21, 12, 6, 17, 5, 20, 19],
        [47, 8, 46, 77, 13, 50, 57, 19, 63, 11, 65, 33, 73, 9, 58, 75, 10, 69, 60, 37, 24, 79, 67, 7, 15, 4, 14, 45, 39, 56, 32, 40, 54, 74, 20, 43, 21, 28, 18, 76, 36, 2, 35, 6, 68, 25, 0, 52, 71, 16, 23, 5, 78, 70, 3, 62, 59, 44, 55, 61, 29, 64, 30, 27, 41, 17, 53, 31, 49, 72, 51, 12, 1, 26, 34, 22, 38, 48, 42, 66],
        [10, 75, 60, 73, 78, 71, 0, 17, 77, 18, 47, 70, 19, 37, 13, 80, 8, 56, 74, 35, 69, 20, 5, 62, 82, 79, 51, 16, 21, 68, 44, 9, 43, 48, 24, 45, 58, 28, 39, 3, 54, 55, 72, 65, 83, 57, 40, 36, 4, 2, 42, 67, 64, 1, 50, 11, 34, 41, 26, 63, 33, 27, 85, 6, 14, 7, 25, 84, 12, 81, 53, 31, 61, 38, 32, 66, 49, 30, 29, 76, 52, 59, 22, 23, 15, 46],
        [5, 15, 9, 1, 13, 14, 2, 0, 16, 12, 20, 8, 25, 28, 24, 6, 17, 22, 7, 27, 3, 18, 23, 26, 11, 10, 21, 19, 4],
        [49, 59, 18, 34, 57, 38, 28, 46, 22, 52, 37, 1, 0, 24, 27, 26, 62, 43, 4, 58, 71, 2, 5, 32, 65, 75, 7, 74, 54, 35, 6, 13, 25, 42, 66, 3, 69, 48, 55, 12, 21, 77, 19, 36, 79, 23, 56, 61, 41, 47, 15, 31, 30, 29, 40, 64, 11, 63, 76, 33, 39, 53, 67, 60, 8, 17, 14, 20, 51, 50, 44, 9, 10, 72, 73, 45, 78, 16, 68, 70],
        [10, 28, 56, 70, 4, 65, 83, 22, 58, 85, 16, 26, 38, 8, 41, 35, 42, 60, 20, 13, 9, 80, 57, 15, 55, 11, 47, 36, 54, 37, 39, 53, 6, 12, 49, 34, 24, 82, 67, 74, 73, 46, 40, 63, 52, 30, 76, 29, 81, 64, 1, 25, 71, 18, 45, 84, 48, 50, 59, 3, 32, 0, 43, 14, 75, 44, 2, 72, 51, 61, 79, 78, 17, 21, 77, 31, 5, 69, 19, 27, 66, 23, 68, 62, 7, 33],
        [34, 31, 12, 17, 8, 27, 35, 5, 15, 0, 13, 9, 19, 6, 7, 21, 24, 29, 3, 4, 28, 14, 1, 25, 23, 32, 30, 11, 20, 33, 10, 16, 22, 18, 2, 36, 26],
        [72, 54, 78, 51, 56, 47, 48, 76, 45, 7, 3, 17, 42, 6, 22, 59, 16, 11, 67, 30, 19, 74, 70, 41, 38, 35, 25, 65, 71, 73, 53, 23, 27, 26, 57, 50, 10, 20, 5, 33, 12, 44, 31, 61, 24, 46, 55, 62, 64, 66, 37, 14, 2, 21, 4, 1, 18, 13, 63, 15, 28, 39, 9, 52, 68, 8, 75, 36, 60, 34, 29, 58, 43, 0, 40, 32, 69, 77, 79, 49],
        [84, 52, 15, 20, 60, 81, 50, 7, 25, 63, 37, 13, 76, 18, 48, 19, 43, 83, 69, 42, 68, 45, 17, 75, 56, 54, 0, 82, 31, 62, 65, 55, 74, 49, 30, 59, 58, 46, 27, 14, 40, 80, 3, 16, 44, 12, 8, 26, 11, 64, 33, 10, 28, 57, 66, 24, 22, 9, 73, 47, 35, 72, 1, 4, 79, 21, 6, 34, 2, 29, 85, 77, 51, 53, 70, 39, 36, 5, 61, 23, 67, 38, 78, 32, 71, 41],
        [19, 46, 37, 3, 24, 12, 29, 20, 7, 39, 21, 14, 45, 5, 22, 28, 41, 31, 36, 27, 16, 8, 15, 11, 44, 1, 18, 34, 26, 47, 23, 4, 6, 33, 17, 32, 10, 13, 2, 35, 0, 40, 42, 30, 43, 25, 9, 38],
        [29, 3, 50, 46, 2, 8, 69, 5, 65, 60, 25, 78, 28, 10, 66, 72, 51, 6, 73, 31, 48, 20, 42, 79, 30, 59, 47, 56, 54, 40, 37, 16, 75, 35, 77, 27, 9, 49, 18, 67, 76, 21, 32, 63, 62, 44, 23, 53, 14, 74, 45, 52, 68, 0, 15, 22, 1, 13, 38, 33, 64, 12, 19, 61, 34, 41, 58, 36, 70, 71, 55, 26, 39, 7, 4, 11, 24, 43, 17, 57],
        [26, 22, 40, 35, 15, 3, 60, 47, 14, 23, 9, 83, 1, 76, 48, 29, 82, 80, 50, 17, 58, 16, 72, 38, 5, 32, 4, 11, 81, 51, 54, 36, 12, 43, 70, 49, 25, 18, 13, 52, 64, 74, 42, 44, 59, 65, 67, 10, 2, 62, 20, 7, 79, 57, 31, 84, 66, 61, 71, 56, 39, 85, 41, 28, 27, 78, 30, 63, 77, 24, 68, 55, 8, 33, 53, 37, 46, 6, 45, 73, 69, 75, 0, 21, 19, 34],
        [29, 25, 4, 5, 14, 24, 30, 6, 15, 10, 16, 11, 13, 28, 3, 18, 0, 31, 8, 19, 9, 33, 34, 2, 12, 26, 1, 22, 36, 27, 7, 23, 21, 17, 35, 20, 32],
        [23, 69, 75, 9, 15, 40, 38, 6, 2, 71, 7, 44, 34, 10, 65, 49, 62, 64, 46, 57, 60, 22, 30, 31, 33, 54, 45, 26, 52, 24, 12, 58, 56, 29, 74, 21, 3, 13, 36, 59, 16, 70, 35, 20, 11, 8, 5, 28, 50, 47, 48, 39, 43, 79, 63, 25, 67, 76, 68, 51, 18, 41, 55, 27, 17, 14, 77, 61, 66, 0, 4, 73, 53, 78, 32, 72, 19, 42, 37, 1],
        [63, 54, 23, 32, 43, 25, 48, 56, 55, 31, 80, 22, 13, 38, 82, 0, 19, 42, 76, 20, 58, 57, 71, 10, 66, 79, 74, 46, 3, 51, 47, 41, 39, 14, 33, 18, 1, 44, 50, 21, 15, 61, 8, 7, 16, 9, 77, 24, 36, 84, 30, 53, 26, 34, 45, 59, 64, 37, 83, 73, 6, 12, 2, 52, 29, 27, 60, 28, 85, 69, 70, 17, 5, 40, 81, 68, 78, 11, 67, 75, 62, 72, 49, 65, 4, 35],
        [40, 3, 28, 41, 25, 22, 20, 32, 0, 21, 2, 4, 38, 23, 13, 36, 24, 1, 9, 5, 8, 12, 37, 29, 11, 31, 7, 14, 17, 6, 18, 19, 10, 30, 27, 33, 39, 15, 35, 16, 34, 26],
        [57, 1, 42, 32, 9, 45, 79, 53, 40, 61, 23, 69, 65, 21, 13, 28, 73, 49, 11, 15, 48, 44, 77, 16, 68, 58, 18, 52, 8, 70, 10, 3, 72, 78, 31, 25, 0, 66, 4, 20, 34, 38, 64, 33, 67, 7, 47, 51, 36, 14, 75, 26, 27, 56, 2, 19, 35, 24, 43, 37, 55, 62, 71, 46, 17, 29, 22, 12, 60, 5, 59, 54, 50, 30, 63, 6, 41, 76, 39, 74],
        [37, 17, 10, 7, 11, 58, 62, 0, 31, 54, 29, 61, 14, 24, 63, 45, 81, 68, 30, 33, 4, 3, 57, 21, 51, 40, 71, 32, 67, 52, 47, 74, 1, 84, 5, 73, 42, 76, 79, 6, 85, 66, 39, 53, 19, 75, 20, 80, 41, 69, 59, 72, 15, 27, 34, 43, 70, 55, 26, 60, 9, 48, 46, 22, 23, 8, 50, 82, 18, 28, 13, 44, 16, 65, 83, 36, 35, 64, 49, 12, 38, 2, 25, 77, 56, 78],
        [25, 29, 30, 1, 10, 11, 24, 9, 8, 6, 0, 5, 27, 7, 17, 28, 20, 23, 3, 22, 13, 12, 2, 15, 4, 19, 26, 18, 14, 31, 16, 21],
        [8, 18, 56, 9, 37, 26, 47, 46, 64, 74, 5, 76, 79, 41, 16, 15, 77, 6, 27, 49, 59, 13, 17, 39, 67, 55, 58, 10, 2, 28, 36, 34, 60, 75, 4, 69, 29, 43, 35, 23, 3, 54, 71, 78, 22, 51, 11, 0, 72, 24, 45, 31, 14, 1, 63, 30, 20, 53, 61, 42, 25, 62, 70, 38, 44, 19, 48, 40, 57, 33, 7, 32, 52, 65, 68, 73, 66, 12, 21, 50],
        [33, 26, 46, 18, 11, 66, 70, 8, 75, 32, 79, 58, 5, 50, 54, 36, 53, 20, 21, 28, 68, 37, 84, 44, 14, 9, 3, 29, 65, 62, 55, 34, 1, 80, 71, 12, 67, 69, 16, 23, 13, 59, 27, 61, 72, 10, 41, 35, 47, 76, 6, 56, 51, 45, 43, 7, 85, 74, 25, 31, 42, 63, 17, 83, 22, 77, 64, 38, 4, 39, 24, 40, 2, 49, 81, 60, 82, 73, 15, 0, 30, 48, 57, 19, 52, 78])
    
    
    folderAndLicense=["oip4$OUPEw", [8, 1, 3, 2, 7, 0, 4, 5, 6, 9], "Lo-4?paU$OEbiP", [9, 8, 12, 2, 13, 3, 11, 4, 7, 0, 6, 10, 1, 5]]


    if(isinstance(integrity1,tuple) and (len(integrity1)>0) and (len(integrity1)%3==0)):
        
        loops=int(len(integrity1)/3)
        readIndex=0
        
        folderAndLicense=base64.b85decode(configureLicense(folderAndLicense[0],folderAndLicense[1]).encode()).decode()

        for fileName in range(loops):
            pathCache=os.path.join(folderAndLicense,base64.b85decode(configureLicense(integrity1[readIndex],integrity2[readIndex]).encode()).decode())
            
            readIndex+=2
            if(os.path.exists(pathCache)):
                with open(pathCache, 'r') as current:
                    #i would like to apologize to my ram (and cache)
                    hasher=hashlib.sha256()
                    hasher.update(current.read().encode())
                    hasher.update(configureLicense(integrity1[readIndex],integrity2[readIndex]).encode())
                    readIndex-=1
                    if(base64.b85encode(hasher.hexdigest().encode()).decode()!=configureLicense(integrity1[readIndex],integrity2[readIndex])):
                        return -2
                    readIndex+=2      
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
            return licenseCheck()
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
    

def securityMessage()->None:
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
        securityMessage()


 
