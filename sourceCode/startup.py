   
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



def configureLicense(scrambledPart:str,orderingList:list[int])->str:
    return "".join([scrambledPart[int(orderingList[index])] for index in range(len(orderingList))])



#not done yet
def licenseCheck()->bool:
    integrity1=("Oi4pUPE$owFJ)nKc|%M|Ek{sHGc8O>Lq$$gMJ{xBbN", "W-?_oFgIg1Vq-NjGBYt^I5sjfFf}nWVKO#2IW;h3He_LAWo0lqW->Q3G-EI}H8U_VG-NY3VmCQ3Vq#@6", "6-vkgl83z?|AW#{}(Ilf$5TxhpI+iqgM-g;4rfmE7|(2F|;+<Xf?n99gskcdDi0)9jv;^rELu{YU5lNkePPA2%", "Oi4pUPE$owFKlUIcx`MlElo*OElf#6MNU&iE_8Tw", "WHT{hG%+<eWi>N2H8o^1Vq;}7V`DcnW-(%9Gc-9lFf}(YIAu98VK8B2G&o^4V`XAAH(@j}Vl_B8W;ioA", 
        "m`ze5x`#A4?pu6fMSCGeEp;0U<lDGTj1=Rm+avRco1j;)KH&Nv+58<E~NR%ABVm)~}ZWm&+{WsbaV>Iw3q?x>P", "Oi4pUPE$owFKlUIcynxYElo*OElf#6MNU&iE_8Tw", "VKg{nF)%POIA%0vG+}0DG-P2lWMgDEI5RUcG-EeoVKX>3IXN^qG&e9aVmCQ8VPQ5mF=I9`G&5mjHf3gH", "nVM=JtwJT(*#OPb-OKppvj#~i)P4kWprN5aFbQJ@9mJohC=jK%)uHT%xNb9?j#q4p}5A1ZFOwrPb6hMbij`7l0", "Oi4pUPE$owFKl>iY%M}lL@hHdLu_Gnb7d_|Nkc_WQ$;Rxcys", 
        "IAS(3F*q|dGh#AiW@KY#F*rG9Gh;I_GdMLcVq!NpH)1z6Wo2b%FgamlF=SyeWHK^2Fg7z~GBG$aH8e6a", "GAm1GjXePDR81iXoUPeWc04usDtHbCoITyU>~1WVHO?LKB(CftC#S*j>EU59)sCqb^1Xqd+w|x~{xIXhOO#uho", "Oi4pUPE$owFHLWHX>4p^El_o0Y-wXHOlf0fZgXWVGA=MJOi4pUPE$oLba-?", "I5#vjW-v1`Fk?7mWn^VyWo0&EH)b<qH8VCiGi5Y4F*P(XV>V)9Gh#3?GBaW|H8^82V=ypeHZn0`Gh{F`", 
        "UXz-OFVKp*_4ptu-9rY2~sc`2sNf}qa0&DzuYb^UbX>&|ImqJ-9D8pGGjyEz@hiuDuZadqM2Y+F|P=^szfBNJH", "Oi4pUPE$owFHUu7bZcQPL2zMXXk{%jE-)=jNkc_WQ$;Rxcys", "HeoqqI5J{kV>vQnG&p2AIWaIdGi5PiVlg*1H)c0DWi>c9I5K8tHf3fvIb~)uIXGoCWimH7IAUaGVmD(l", "P#!_40`w+Q%xG0{C*}PvY_TJUXxVIj4PW5foQY$(!*?c>|>*j|owZGL*$2i8))85!)91u{v*;xhU=a<$K~M49j", 
        "Oi4pUPE$owFHme@d3SPYXJ~XSL2zMXXk{%jE-)=jNkc_WQ$;Rxcys", "H)Jt5GcaW{F*!ClVKibmIAdlqH(@h2W@Ke!WjQorGcaK|W;9_kH90skI59ajWMwxsV=-enIXGixVrDZm", "LK>9e<$<+l-5rsJ1+FZp19=LFdSs>u1d)b2~FC;E3TeXl~AqCh&&ZQV<SCULA@D%)XIG17x9_Xl||9=R4K31gu", "Oi4pUPE$owFHm`OXm4&UP*X-sEix@kNkc_WQ$;Rxcys", "IW#ghWH&T4HaKK7GcYwcH(_ODIb~vDH8(J0F=IGpF)=k`WivN0Wid1~Vl^^0V>L7~WjHxAF*7z{Fk&)e", 
        "cNFVqxlNp(-=kjXiUYs^d4%}vDmHv`l~k$it~0n}#S>IwO5Ke*S_z6e}`06esRD#k83o@GPdf@t^8i1ZtxD!_-", "Oi4pUPE$oLba-?", "I5;<DVPi2fFfwIiWI1JJGdN~6F*Y}4H8n6ZWH2>lGchtZVq-HkWM*VDH)3NkWMMgEF*9K`HezOFVPj%9", "DGfQBx!1ga7#9w$h(kv0s8(vN^qmUS^<8V}$Q>iv@AbU+TZjlLf)c=Y+NONsGGIXyFhG!R4E&=?i|1uM*)e8}w")
    integrity2=([30, 23, 4, 29, 17, 24, 41, 21, 2, 37, 36, 8, 40, 13, 20, 19, 39, 38, 7, 14, 5, 35, 27, 12, 33, 16, 10, 11, 6, 18, 25, 9, 15, 22, 32, 34, 26, 28, 0, 1, 3, 31],
        [8, 12, 43, 13, 56, 38, 63, 35, 14, 7, 32, 79, 51, 41, 68, 1, 46, 74, 6, 57, 52, 61, 54, 5, 64, 66, 67, 19, 71, 0, 60, 76, 65, 77, 37, 17, 33, 21, 36, 24, 48, 2, 50, 75, 69, 26, 31, 73, 10, 40, 29, 53, 62, 44, 23, 39, 55, 9, 49, 18, 42, 27, 72, 45, 59, 15, 11, 20, 47, 16, 30, 22, 58, 3, 78, 28, 70, 4, 34, 25],
        [39, 10, 68, 72, 47, 43, 50, 76, 85, 70, 28, 52, 83, 63, 23, 81, 34, 49, 46, 25, 79, 53, 56, 0, 66, 54, 41, 64, 61, 44, 22, 42, 11, 1, 38, 51, 13, 48, 19, 2, 35, 36, 40, 5, 33, 26, 30, 75, 58, 14, 80, 74, 62, 4, 29, 65, 84, 69, 12, 59, 24, 27, 78, 9, 20, 21, 67, 55, 71, 8, 60, 37, 82, 77, 31, 45, 6, 18, 15, 16, 32, 73, 7, 17, 3, 57],
        [16, 4, 9, 23, 12, 22, 1, 38, 32, 25, 29, 24, 28, 30, 20, 7, 8, 26, 6, 31, 39, 11, 10, 5, 34, 35, 21, 19, 14, 0, 15, 27, 18, 33, 36, 17, 13, 37, 2, 3],
        [54, 75, 38, 53, 76, 44, 50, 59, 45, 28, 20, 16, 31, 13, 66, 22, 5, 18, 43, 23, 30, 46, 11, 78, 32, 52, 14, 29, 72, 3, 25, 0, 2, 35, 17, 4, 36, 61, 77, 63, 33, 71, 60, 62, 74, 67, 69, 42, 26, 58, 7, 21, 37, 57, 65, 70, 19, 73, 1, 79, 51, 40, 34, 24, 47, 49, 9, 12, 15, 10, 48, 39, 55, 56, 41, 64, 27, 6, 8, 68],
        [82, 74, 71, 36, 8, 17, 3, 16, 30, 35, 31, 68, 32, 58, 43, 62, 46, 57, 76, 83, 12, 19, 28, 47, 85, 73, 48, 11, 20, 5, 4, 34, 61, 38, 13, 50, 22, 23, 29, 60, 33, 55, 65, 40, 53, 70, 51, 21, 79, 41, 81, 0, 69, 66, 27, 52, 37, 72, 10, 2, 67, 77, 84, 56, 26, 42, 6, 25, 24, 75, 80, 7, 1, 18, 9, 39, 59, 78, 54, 63, 14, 45, 44, 49, 64, 15],
        [36, 27, 25, 23, 8, 13, 35, 38, 24, 19, 33, 30, 9, 1, 22, 32, 37, 4, 7, 0, 3, 39, 15, 11, 21, 10, 14, 16, 18, 20, 29, 28, 2, 34, 6, 12, 26, 17, 5, 31],
        [23, 55, 67, 48, 53, 66, 75, 45, 7, 17, 18, 46, 56, 49, 5, 28, 27, 71, 39, 68, 20, 34, 65, 13, 10, 14, 47, 0, 52, 43, 25, 37, 1, 57, 64, 70, 6, 22, 11, 33, 30, 59, 54, 38, 21, 69, 78, 12, 61, 42, 73, 36, 79, 77, 19, 62, 8, 63, 24, 2, 29, 15, 41, 74, 50, 16, 40, 35, 76, 4, 26, 58, 32, 72, 31, 9, 3, 51, 60, 44],
        [78, 4, 77, 75, 23, 13, 68, 36, 33, 85, 81, 52, 1, 73, 40, 41, 66, 2, 76, 15, 67, 7, 18, 70, 64, 47, 12, 43, 56, 14, 51, 65, 25, 6, 59, 72, 29, 17, 46, 9, 28, 26, 0, 11, 71, 19, 27, 63, 55, 42, 3, 69, 37, 39, 61, 21, 82, 54, 79, 83, 74, 20, 16, 24, 31, 30, 8, 45, 80, 57, 44, 35, 60, 22, 49, 34, 5, 58, 62, 32, 48, 84, 38, 10, 53, 50],
        [8, 23, 6, 37, 5, 13, 9, 10, 28, 20, 29, 17, 26, 16, 15, 45, 27, 18, 7, 36, 42, 19, 3, 47, 0, 34, 12, 40, 39, 33, 21, 41, 2, 32, 14, 35, 30, 43, 25, 44, 11, 46, 24, 1, 38, 31, 22, 4],
        [49, 18, 55, 69, 10, 24, 54, 13, 3, 71, 72, 33, 12, 29, 22, 76, 50, 44, 46, 30, 34, 52, 7, 26, 17, 61, 63, 35, 65, 41, 74, 37, 15, 78, 62, 68, 39, 6, 4, 21, 43, 59, 58, 73, 38, 19, 66, 67, 14, 23, 77, 60, 1, 31, 48, 75, 25, 9, 36, 8, 47, 57, 53, 32, 5, 64, 16, 40, 11, 51, 20, 45, 0, 28, 79, 2, 42, 27, 56, 70],
        [57, 44, 43, 8, 32, 48, 5, 76, 24, 56, 66, 42, 46, 38, 52, 14, 68, 64, 23, 25, 27, 16, 58, 67, 13, 15, 33, 50, 60, 70, 26, 21, 36, 9, 73, 78, 69, 29, 31, 85, 71, 20, 82, 37, 40, 34, 47, 0, 22, 84, 28, 65, 35, 59, 75, 11, 30, 10, 51, 19, 7, 54, 45, 41, 18, 53, 3, 72, 80, 81, 63, 17, 39, 77, 49, 74, 6, 1, 55, 2, 83, 4, 62, 61, 12, 79],
        [7, 45, 51, 48, 40, 0, 35, 9, 49, 56, 33, 6, 46, 18, 22, 54, 10, 15, 44, 28, 11, 47, 27, 14, 57, 3, 36, 38, 30, 31, 17, 50, 41, 13, 16, 1, 26, 2, 53, 8, 24, 5, 34, 4, 21, 42, 23, 29, 55, 12, 58, 39, 32, 37, 43, 52, 25, 19, 20],
        [44, 52, 18, 79, 39, 67, 0, 61, 71, 25, 32, 51, 42, 66, 14, 9, 60, 12, 3, 1, 45, 6, 7, 23, 17, 59, 41, 29, 33, 50, 48, 78, 69, 26, 5, 63, 2, 56, 36, 62, 65, 70, 40, 11, 34, 10, 73, 27, 24, 22, 68, 72, 28, 53, 8, 64, 75, 30, 77, 20, 19, 35, 38, 46, 49, 47, 74, 4, 43, 57, 16, 13, 58, 76, 54, 15, 37, 55, 21, 31],
        [30, 81, 37, 39, 82, 66, 25, 49, 53, 50, 23, 28, 75, 76, 19, 7, 34, 4, 73, 22, 77, 61, 43, 51, 78, 59, 62, 12, 15, 27, 40, 10, 1, 42, 72, 2, 33, 8, 31, 16, 57, 83, 79, 64, 63, 56, 26, 41, 84, 55, 38, 46, 54, 3, 13, 68, 17, 0, 71, 45, 29, 48, 74, 47, 65, 24, 67, 32, 80, 5, 9, 70, 20, 60, 18, 52, 21, 58, 35, 44, 36, 11, 85, 14, 6, 69],
        [13, 16, 22, 40, 3, 14, 4, 24, 19, 1, 17, 35, 0, 42, 45, 2, 32, 21, 9, 15, 30, 39, 37, 43, 38, 7, 47, 31, 34, 12, 26, 18, 44, 41, 6, 23, 28, 36, 10, 33, 46, 5, 20, 25, 11, 27, 8, 29],
        [7, 8, 16, 78, 18, 14, 19, 34, 69, 72, 66, 63, 9, 42, 11, 68, 37, 32, 74, 57, 10, 21, 49, 28, 39, 55, 12, 22, 47, 20, 65, 25, 0, 48, 58, 45, 64, 79, 30, 56, 3, 36, 41, 70, 4, 26, 44, 51, 38, 2, 40, 53, 15, 5, 52, 13, 46, 27, 31, 35, 67, 77, 1, 54, 75, 43, 33, 50, 71, 6, 17, 62, 60, 59, 23, 61, 29, 24, 76, 73],
        [14, 33, 52, 82, 47, 30, 2, 63, 60, 56, 26, 66, 54, 43, 70, 39, 1, 10, 64, 77, 71, 57, 53, 24, 27, 20, 32, 15, 29, 9, 0, 8, 45, 7, 51, 62, 5, 23, 65, 76, 11, 18, 16, 46, 72, 25, 55, 75, 36, 61, 74, 69, 19, 79, 44, 6, 21, 85, 84, 12, 58, 13, 59, 34, 17, 31, 73, 35, 80, 4, 78, 48, 83, 41, 37, 38, 68, 50, 40, 28, 3, 22, 42, 81, 49, 67],
        [5, 4, 30, 40, 43, 26, 28, 20, 12, 33, 51, 2, 11, 16, 10, 48, 36, 18, 7, 14, 0, 6, 39, 50, 44, 24, 13, 25, 19, 42, 47, 27, 9, 52, 1, 41, 29, 31, 32, 38, 46, 17, 23, 22, 21, 8, 37, 45, 3, 49, 35, 15, 34],
        [10, 40, 28, 6, 36, 46, 34, 25, 49, 43, 64, 5, 35, 18, 9, 74, 61, 15, 62, 52, 55, 11, 48, 39, 24, 16, 66, 58, 73, 51, 37, 79, 12, 65, 31, 60, 53, 7, 44, 54, 13, 2, 38, 29, 3, 1, 67, 0, 19, 56, 69, 21, 63, 70, 78, 42, 27, 4, 72, 59, 76, 45, 23, 47, 20, 71, 8, 14, 32, 50, 57, 41, 30, 26, 22, 77, 68, 75, 17, 33],
        [44, 16, 75, 51, 20, 41, 7, 26, 81, 35, 63, 18, 83, 78, 15, 33, 62, 4, 49, 40, 48, 39, 84, 22, 68, 28, 82, 9, 55, 71, 66, 76, 61, 11, 31, 52, 45, 43, 3, 56, 57, 5, 77, 42, 12, 6, 29, 8, 14, 46, 85, 74, 47, 67, 19, 72, 64, 80, 73, 24, 36, 27, 65, 37, 53, 10, 79, 38, 59, 54, 25, 17, 69, 1, 58, 0, 2, 23, 30, 21, 13, 70, 60, 32, 34, 50],
        [29, 3, 35, 6, 36, 41, 12, 9, 21, 39, 30, 11, 15, 17, 28, 38, 13, 23, 37, 34, 7, 25, 5, 4, 24, 31, 8, 40, 16, 10, 32, 19, 14, 18, 33, 1, 2, 27, 0, 22, 26, 42, 20],
        [12, 33, 32, 36, 27, 18, 78, 26, 52, 50, 1, 4, 59, 68, 38, 61, 6, 31, 45, 2, 57, 46, 7, 65, 24, 43, 0, 62, 66, 60, 23, 48, 28, 74, 10, 16, 53, 51, 34, 47, 40, 41, 35, 44, 70, 37, 11, 21, 69, 25, 14, 73, 13, 15, 56, 49, 72, 30, 55, 54, 19, 63, 67, 8, 3, 76, 39, 75, 58, 64, 22, 77, 9, 79, 42, 17, 29, 5, 71, 20],
        [64, 3, 42, 41, 63, 31, 83, 50, 60, 38, 27, 14, 76, 85, 32, 20, 56, 15, 34, 13, 40, 79, 52, 16, 74, 75, 62, 47, 7, 84, 12, 28, 19, 68, 61, 4, 24, 22, 55, 58, 49, 6, 82, 53, 67, 21, 77, 80, 2, 5, 36, 81, 57, 17, 66, 78, 11, 59, 69, 65, 8, 70, 10, 33, 29, 18, 48, 51, 72, 9, 43, 0, 26, 35, 30, 46, 45, 37, 25, 73, 54, 39, 1, 44, 71, 23],
        [9, 4, 3, 6, 1, 7, 12, 0, 5, 8, 2, 13, 11, 10],
        [32, 30, 4, 22, 26, 57, 72, 6, 24, 1, 67, 79, 37, 54, 41, 53, 21, 75, 7, 52, 28, 34, 0, 9, 70, 46, 31, 23, 43, 15, 71, 48, 51, 11, 18, 8, 73, 19, 58, 44, 27, 56, 74, 2, 14, 63, 16, 59, 65, 29, 64, 38, 12, 78, 50, 61, 69, 49, 25, 36, 3, 5, 40, 76, 13, 33, 62, 55, 42, 68, 45, 77, 17, 35, 66, 20, 47, 39, 60, 10],
        [39, 11, 50, 40, 28, 25, 53, 10, 84, 54, 65, 75, 35, 74, 67, 51, 19, 71, 73, 79, 2, 29, 48, 5, 45, 3, 49, 85, 82, 13, 9, 42, 78, 56, 72, 32, 76, 62, 30, 37, 58, 83, 6, 80, 43, 21, 46, 17, 12, 7, 52, 24, 16, 36, 63, 81, 14, 41, 4, 59, 34, 8, 31, 38, 70, 15, 60, 66, 44, 61, 26, 57, 77, 1, 47, 0, 22, 27, 55, 68, 64, 23, 18, 20, 69, 33])
    if(isinstance(integrity1,tuple) and (len(integrity1)>0) and (len(integrity1)%3==0)):
        loops=int(len(integrity1)/3)
        readIndex=0
        for fileName in range(loops):
            pathCache=base64.b85decode(configureLicense(integrity1[readIndex],integrity2[readIndex]).encode()).decode()
            readIndex+=2
            if(os.path.exists(pathCache)):
                with open(pathCache, 'r') as current:
                    #i would like to apologize to my ram (and cache)
                    hasher=hashlib.sha256()
                    hasher.update(current.read().encode())
                    hasher.update(configureLicense(integrity1[readIndex],integrity2[readIndex]).encode())
                    readIndex-=1
                    if(base64.b85encode(hasher.hexdigest().encode()).decode()!=configureLicense(integrity1[readIndex],integrity2[readIndex])):
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
        self.vNumber="v1.3.1"
        self.vString="Yahoo Finance Historical Data Downloader "+self.vNumber+" by redcacus5"+"\n\n"

    def drawUIHeader(self):
        easyCLI.clear()
        print(self.vString)
    

def securityMessage()->None:
    import sys
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
    

    if(not licenseCheck()):
        securityMessage()
        
    elif(not integrityCheck()):
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
            

    else:
        try:
            commandLineInterface()
        except browserLaunchFail as fail:
            easyCLI.uiHeader()
            print(fail.message)
            easyCLI.ln()
            print("root cause: "+str(fail.getRootError()))
            easyCLI.ln(3)
            input("press enter to finish.")


 
