   
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
    integrity1=("|$4%c8{wOKOcBGiHbLnMgU{oNsM$xPq)pkJ>FE|E$J",
        "VW`5pu9H+i6QVw7h_W;MouTIM^(2T4#BZGua;VfmIDdWMEnsQHHK8lAV(Grd48XWXyXGNWH}mZjed-|`", "TKl`zY0#b9;lQ41cb&th1JdFomNkRp}Af(-*1RMWdw$KW<B<6S!zTn(|Kn!ym#7|pAQc9#REaD85LKmT<zn=@l", "MT6pUUcEMfx*$IoOF8E4`lKNiO_ollUEPi&#wElw", "GbPjVWP3qv-jVIGVcI}-x<-w1%alPqGVoWMN!VZ}oW8VM#6oBulogg1V-jW_>HvqttaQit7h6>3VF`B(",
        "{Uf-*%B&S~zH#_cGrJP$&ZIv2rG<(a3}HKj<+VU0gmjcX8yN3gu{{lRal6-o0eaq59Clc)OxiWbDT8)LdA!=`f", "l4cUiwNUilFMTKwoEPfO6yU*l#Oo$EEpYxI&nE_8", "FP;e3EZVBmW-5%i7~7KqlrVlaHIU)IaVnV=BUKcAc~HK5WcZ15AWGjC1TGiwH778-QQ;DIZHli4i(yl~", "V+yjRS?w=LqguEuS7%*AFkPExVt!?MQSRBxch&Wno(v63M(N$!z!7yO|Zjz_w|TlM;S}&y7`YWpo;<I=4M1?TI",
        "_7;KOxsik4_M$LyUw>_QYNHuRl}iE$h%ocb|G@dcnldPWpLF", "h<B3im@cQMVLAhbtU5-GAHP@ZG*!W(;B(MPHI(MuB)Ffy4FG0C%I>Ibek8gnbWzphW7omI|IWtmoVFRv", "n0l?KHFi<wHC?HnbJJ2?N+xT*o-BHqiA4YP(5nlpYEPAhRF9{DE~$awFI_%u8EMHYOd;@AIHB(w9;INcpx@kek", "pEOoPGPAoHFHUigZ_?lL-XXfW^lOOUpW>LH4J04$pEww4fb0-iaMXEoY=V$",
        "!5lWgfGRhfZFVH3HVf%osV8hHPHQVX|Wy00kcfgFmU>GI*Wis*VmWNf(89GAHG8_Fe=jm_H|a>tq3}8D", "E&p_A<+C8V;1GtDt6u^WUB+iJFZE7){q-_oFa=J?4dvya&;y@9YgGAILXF_n!DsXR+`A5bIOK)7_NvHE3}+!?=", "Eo{$sX4FwNcHZz_RPxickMjkuU;EQQ=p7y2XU%WL-bcj)$PO", "GgJ8G6uM{VlFkVHHIfB`6#_nNe@{Bl%{zv(8)1F4}HVV|(Z2Hd03&G{YFZGX?5N`+lXGWVl_ZF?2jh*x",
        "%Olcz6dWd6>Sk8}T+jgknrCpLloH7&c?~Psb6Hc%(dRD9d6Xn!9LV!%ol|u2n5LP{ku9J7K1EK5#Y(6B!3qfZ%", "UxXX_mekcF-X)R;pLQ34YESk2Jwo~S$MXcHO@d%yi{j$WjPN=sEPz", "P$mb83tGlum7>MI0qVlPrqrGWKAPlQLK8hhnGIXH=3i-c8ro4)734XWIGPVWqo#kVqTn2BVI4IHn(_V&", "E@sKRIGn9IqdqO1i+Y)Sx2C6T8@Zj^ZTsF;!sQHkdsNcA9z<0L|{PQJa2`IW9DPt6Fk^c&FVc_{CqjuL4LifoR",
        "wH$sxsc*o;OEUkUQ$O_W4P-E@miFNpRXc`mXyx&P4ik", "jH}@rKrVM#djikV9FtPhdeQ4WG#q43bZMiCf#?FgTV8W84rVGZ)HH$?G}F4HJh)*lhTHyRH(MR7HW0fn", "s>7D;zK&*QY><kT4?qk)|wS)6j9WzN7=;Q)U(|t`|7E3EbE6;kyB`uG349DECAnf>nfFP|@5fyU0;k5b~sm7lK", "O4oLi?bpUaP$-E",
        "i=cA1A+GII|GaG*mYF|}kF$mk{IHFYFHgW0DHVFdG8j-WoU#9qgp3hB?+H)H_F5@c!6DeZp9Ae~J0fHl", "eig4$VH_=A8>PELcbF=1PTUzuDdS;Ma+yjI&-XBQol@l5QSYp4!U5mhmu%VE$my79+=}>Z@o4xbIV0mgLra%71")
    integrity2=([19, 32, 2, 17, 15, 27, 22, 9, 0, 14, 28, 26, 39, 25, 1, 24, 40, 30, 13, 18, 34, 4, 37, 8, 41, 23, 35, 7, 38, 5, 31, 12, 3, 21, 36, 29, 10, 6, 16, 20, 33, 11],
        [65, 56, 51, 22, 79, 57, 59, 5, 47, 73, 54, 72, 15, 68, 53, 14, 77, 0, 71, 41, 64, 34, 48, 20, 42, 63, 23, 78, 33, 29, 31, 11, 6, 10, 32, 12, 36, 50, 38, 49, 55, 4, 61, 70, 1, 58, 27, 74, 43, 30, 45, 66, 26, 76, 19, 75, 2, 60, 39, 7, 17, 24, 21, 40, 52, 3, 18, 28, 62, 35, 25, 9, 69, 37, 44, 46, 13, 67, 8, 16],
        [36, 31, 42, 19, 68, 2, 69, 62, 28, 70, 0, 3, 40, 30, 61, 1, 79, 85, 72, 10, 14, 41, 39, 73, 45, 75, 65, 6, 64, 38, 21, 18, 66, 82, 83, 46, 24, 8, 34, 81, 57, 27, 20, 56, 52, 58, 4, 15, 32, 29, 48, 60, 7, 35, 25, 13, 22, 71, 17, 77, 49, 5, 23, 26, 76, 63, 44, 84, 43, 78, 59, 54, 9, 16, 37, 11, 67, 80, 50, 51, 53, 47, 12, 74, 33, 55],
        [18, 38, 29, 3, 32, 13, 15, 6, 30, 27, 16, 23, 7, 14, 8, 24, 10, 37, 25, 2, 17, 21, 11, 31, 1, 0, 36, 22, 19, 26, 4, 20, 5, 34, 33, 28, 9, 35, 12, 39],
        [65, 21, 16, 11, 70, 55, 71, 77, 61, 22, 6, 72, 25, 20, 30, 45, 18, 50, 4, 73, 28, 37, 66, 24, 78, 48, 2, 64, 46, 59, 5, 15, 23, 51, 27, 68, 41, 60, 63, 79, 58, 10, 14, 35, 56, 52, 54, 13, 74, 39, 3, 69, 33, 1, 38, 44, 17, 47, 7, 43, 26, 40, 42, 36, 53, 8, 32, 12, 34, 19, 29, 67, 49, 76, 9, 75, 0, 62, 31, 57],
        [66, 23, 40, 27, 9, 48, 83, 35, 25, 28, 12, 13, 19, 70, 15, 50, 73, 84, 18, 38, 62, 8, 30, 0, 7, 2, 67, 36, 68, 31, 49, 81, 44, 39, 4, 10, 80, 46, 52, 29, 45, 3, 77, 78, 58, 56, 14, 41, 6, 69, 32, 43, 34, 85, 16, 5, 20, 76, 61, 79, 60, 55, 11, 22, 37, 1, 33, 72, 59, 65, 57, 17, 47, 51, 26, 54, 24, 82, 64, 42, 75, 21, 74, 53, 71, 63],
        [21, 2, 15, 32, 34, 39, 31, 4, 1, 26, 10, 30, 38, 11, 9, 8, 35, 5, 27, 24, 29, 16, 13, 23, 12, 28, 0, 22, 7, 25, 6, 3, 19, 18, 14, 33, 17, 20, 36, 37],
        [30, 48, 11, 34, 28, 68, 1, 45, 78, 71, 5, 56, 38, 27, 7, 54, 19, 63, 16, 42, 49, 69, 50, 51, 76, 0, 35, 72, 31, 25, 66, 15, 39, 70, 18, 21, 3, 77, 58, 26, 61, 24, 65, 67, 36, 55, 53, 47, 9, 74, 44, 10, 60, 22, 33, 79, 37, 20, 52, 2, 40, 29, 59, 14, 62, 12, 73, 6, 41, 43, 23, 75, 4, 13, 64, 8, 32, 17, 46, 57],
        [9, 44, 48, 82, 10, 23, 46, 74, 58, 51, 66, 2, 73, 32, 42, 60, 43, 7, 16, 3, 71, 65, 33, 8, 21, 52, 29, 12, 83, 69, 11, 67, 41, 72, 63, 37, 31, 35, 13, 40, 64, 53, 57, 18, 28, 79, 77, 45, 22, 14, 27, 36, 55, 49, 78, 76, 5, 20, 4, 50, 17, 34, 62, 30, 80, 75, 0, 81, 68, 54, 47, 39, 38, 61, 85, 25, 15, 56, 70, 24, 84, 26, 6, 59, 1, 19],
        [33, 31, 42, 11, 0, 44, 47, 14, 36, 2, 27, 17, 41, 25, 46, 4, 9, 13, 38, 40, 15, 35, 23, 26, 43, 12, 18, 1, 6, 7, 22, 16, 8, 37, 30, 34, 28, 21, 24, 45, 29, 19, 32, 5, 39, 3, 20, 10],
        [4, 73, 74, 63, 19, 42, 46, 61, 38, 16, 5, 3, 26, 31, 41, 49, 37, 39, 66, 65, 29, 10, 57, 12, 18, 30, 51, 52, 45, 58, 32, 9, 11, 76, 33, 0, 60, 2, 7, 78, 14, 8, 55, 43, 23, 48, 69, 24, 22, 28, 27, 25, 6, 53, 47, 17, 72, 1, 56, 77, 71, 15, 13, 64, 67, 75, 62, 21, 54, 40, 59, 70, 20, 79, 36, 34, 35, 50, 68, 44],
        [31, 55, 44, 30, 79, 11, 68, 83, 60, 82, 34, 22, 58, 57, 9, 73, 43, 18, 33, 80, 65, 70, 42, 39, 61, 23, 8, 12, 46, 7, 3, 2, 1, 41, 50, 16, 59, 0, 69, 74, 63, 81, 85, 36, 78, 72, 20, 84, 24, 64, 56, 40, 62, 21, 28, 48, 29, 19, 5, 17, 52, 14, 27, 77, 37, 15, 51, 76, 13, 4, 47, 35, 26, 66, 10, 75, 38, 25, 53, 54, 71, 67, 32, 45, 49, 6],
        [18, 6, 45, 8, 50, 40, 5, 41, 23, 11, 10, 29, 4, 1, 36, 35, 22, 58, 31, 54, 26, 37, 15, 32, 13, 19, 21, 30, 0, 49, 48, 38, 16, 12, 14, 47, 44, 24, 2, 52, 3, 51, 9, 27, 17, 34, 55, 33, 57, 46, 56, 43, 28, 20, 53, 25, 42, 39, 7],
        [42, 18, 72, 45, 39, 56, 11, 8, 63, 71, 76, 35, 20, 46, 57, 75, 40, 58, 31, 44, 24, 0, 6, 48, 5, 41, 55, 43, 50, 74, 78, 61, 2, 23, 14, 73, 69, 29, 66, 65, 77, 52, 3, 10, 60, 36, 25, 37, 59, 17, 27, 21, 22, 53, 9, 33, 16, 38, 67, 13, 15, 30, 54, 34, 70, 7, 1, 12, 49, 32, 26, 68, 62, 51, 28, 19, 4, 79, 64, 47],
        [9, 58, 0, 22, 61, 14, 17, 52, 73, 77, 75, 49, 74, 44, 85, 35, 11, 82, 2, 56, 24, 26, 41, 32, 43, 57, 19, 78, 36, 51, 7, 84, 62, 50, 38, 33, 55, 29, 79, 64, 69, 80, 63, 68, 53, 13, 3, 21, 76, 28, 10, 16, 18, 37, 48, 46, 54, 23, 8, 67, 65, 25, 5, 4, 59, 45, 81, 15, 27, 47, 31, 42, 30, 83, 71, 66, 12, 72, 34, 1, 70, 60, 6, 20, 39, 40],
        [30, 8, 27, 7, 47, 25, 2, 10, 9, 35, 37, 11, 16, 22, 38, 43, 19, 44, 1, 17, 36, 23, 34, 26, 13, 4, 42, 6, 18, 40, 33, 3, 14, 46, 21, 24, 12, 28, 39, 20, 31, 15, 45, 29, 32, 41, 5, 0],
        [78, 29, 8, 56, 25, 9, 19, 11, 17, 12, 41, 70, 51, 15, 35, 30, 7, 1, 61, 23, 24, 46, 21, 59, 13, 33, 18, 22, 66, 47, 26, 38, 53, 52, 68, 31, 37, 39, 50, 77, 2, 55, 69, 20, 74, 3, 48, 79, 45, 76, 72, 28, 43, 75, 54, 62, 0, 4, 65, 42, 57, 34, 73, 27, 63, 6, 64, 60, 10, 40, 14, 16, 36, 5, 32, 44, 58, 67, 71, 49],
        [59, 6, 60, 37, 1, 23, 45, 19, 26, 76, 55, 74, 53, 70, 7, 67, 81, 54, 34, 52, 82, 36, 75, 66, 43, 50, 3, 24, 46, 48, 27, 35, 62, 2, 69, 39, 44, 80, 47, 65, 12, 63, 16, 85, 51, 8, 25, 79, 22, 72, 28, 71, 41, 31, 30, 56, 15, 18, 83, 29, 42, 64, 78, 32, 20, 49, 40, 11, 33, 17, 13, 4, 14, 9, 0, 73, 38, 21, 58, 5, 61, 10, 84, 77, 57, 68],
        [4, 49, 30, 20, 43, 12, 13, 31, 50, 10, 36, 29, 37, 48, 47, 3, 25, 45, 16, 2, 19, 35, 17, 41, 26, 21, 9, 8, 22, 24, 46, 28, 23, 42, 11, 0, 14, 15, 33, 51, 1, 32, 39, 7, 44, 34, 18, 40, 38, 52, 6, 5, 27],
        [32, 48, 79, 36, 6, 77, 19, 10, 33, 52, 37, 29, 1, 8, 30, 73, 12, 70, 3, 66, 72, 64, 39, 25, 14, 78, 61, 21, 54, 68, 62, 63, 53, 28, 69, 27, 55, 40, 31, 75, 18, 58, 46, 67, 11, 44, 57, 43, 2, 76, 34, 9, 74, 41, 51, 35, 42, 22, 0, 45, 71, 49, 17, 59, 20, 16, 38, 47, 24, 56, 15, 60, 4, 50, 5, 7, 13, 23, 65, 26],
        [38, 52, 28, 83, 69, 23, 2, 79, 78, 62, 85, 55, 60, 5, 64, 46, 17, 63, 7, 47, 66, 14, 70, 75, 1, 77, 34, 10, 29, 43, 82, 40, 26, 24, 21, 41, 0, 74, 61, 56, 32, 76, 67, 73, 31, 3, 57, 27, 49, 6, 36, 72, 33, 30, 20, 44, 8, 25, 19, 51, 53, 18, 71, 12, 4, 80, 9, 81, 35, 15, 54, 65, 58, 68, 48, 84, 22, 11, 42, 16, 13, 50, 37, 45, 39, 59],
        [9, 11, 7, 42, 39, 24, 40, 21, 8, 37, 0, 25, 19, 29, 4, 35, 36, 14, 33, 34, 17, 5, 23, 6, 28, 12, 26, 10, 30, 3, 38, 22, 32, 13, 16, 15, 41, 27, 18, 20, 2, 1, 31],
        [44, 65, 18, 62, 4, 41, 76, 40, 32, 56, 36, 23, 19, 58, 43, 12, 5, 74, 7, 29, 52, 24, 47, 48, 0, 15, 21, 34, 37, 14, 9, 51, 31, 71, 67, 66, 11, 53, 45, 46, 78, 75, 39, 70, 59, 49, 69, 54, 16, 17, 72, 55, 10, 28, 8, 35, 27, 25, 77, 60, 38, 63, 26, 6, 64, 79, 33, 20, 2, 22, 50, 61, 13, 57, 3, 42, 30, 73, 68, 1],
        [6, 24, 45, 56, 28, 18, 74, 48, 33, 38, 23, 60, 15, 32, 11, 65, 71, 66, 55, 59, 49, 10, 16, 12, 50, 21, 0, 26, 78, 70, 25, 13, 64, 67, 62, 53, 79, 58, 84, 2, 19, 68, 52, 29, 1, 77, 63, 42, 8, 51, 73, 44, 85, 82, 7, 4, 37, 76, 41, 72, 31, 83, 17, 14, 40, 69, 9, 43, 34, 81, 47, 5, 27, 39, 80, 30, 46, 20, 36, 61, 57, 35, 22, 54, 3, 75],
        [0, 2, 8, 9, 1, 13, 10, 3, 4, 11, 5, 7, 12, 6],
        [78, 11, 63, 13, 39, 71, 48, 65, 18, 5, 73, 16, 17, 0, 51, 54, 2, 35, 24, 19, 7, 50, 3, 34, 72, 67, 70, 26, 53, 68, 40, 46, 61, 45, 57, 31, 55, 75, 60, 58, 15, 69, 43, 77, 25, 32, 38, 56, 42, 49, 41, 44, 14, 59, 9, 37, 66, 30, 21, 20, 8, 10, 79, 27, 1, 52, 74, 28, 47, 4, 23, 12, 6, 33, 64, 22, 62, 36, 29, 76],
        [34, 18, 76, 77, 48, 7, 60, 81, 66, 40, 22, 59, 4, 80, 65, 54, 45, 1, 68, 73, 39, 3, 43, 30, 58, 36, 67, 9, 14, 10, 26, 31, 62, 13, 78, 70, 52, 51, 72, 57, 46, 28, 27, 15, 44, 37, 21, 71, 29, 82, 55, 38, 47, 85, 53, 35, 75, 5, 19, 23, 84, 49, 11, 6, 24, 42, 63, 69, 12, 79, 74, 64, 33, 32, 16, 20, 8, 41, 61, 2, 17, 0, 50, 25, 83, 56])
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
        self.vNumber="v1.3.1"
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


 
