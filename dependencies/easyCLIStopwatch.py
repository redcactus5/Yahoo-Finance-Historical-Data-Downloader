'''
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 
'''

from dependencies.easyCliPrivateConfigBackend import _privateInternalGetTimeRef

#literally just an error for the timer so it has its own
class EasyCLIStopwatchError(Exception):
    def __init__(self, message="generic timer error"):
        self.message = message
        super().__init__(self.message)

class Stopwatch:
    def __init__(self):
        #init our vars, and grab a personal reference to the time standard lib
        
        self.timeLib=_privateInternalGetTimeRef()
        self.startTime=0
        self.endTime=0
        self.totalElapsedTime=0
        self.partialElapsedTime=0
        self.newStartTime=0
        self.started=False
        self.finished=False
        self.paused=False
        self.hasBeenPaused=False
        
    
    def reset(self):
        #reinitialize our variables and flags
        self.startTime=0
        self.endTime=0
        self.totalElapsedTime=0
        self.partialElapsedTime=0
        self.newStartTime=0
        self.started=False
        self.finished=False
        self.paused=False
        self.hasBeenPaused=False
        #i know there are a lot of them, and it proably could have been implemented cleaner, but this is simple and fast enough, and pretty understandable

    def start(self):
        #safety checks
        if(self.started):
            if(self.paused):
                raise EasyCLIStopwatchError("error: cannot start the stopwatch, the stopwatch has already been started!\ndid you mean resume()?")
            elif(self.finished):
                raise EasyCLIStopwatchError("error: cannot start the stopwatch, the stopwatch has ended! \nto start over, call reset() first.")
            raise EasyCLIStopwatchError("error: cannot start the stopwatch, the stopwatch is already running!")
        #just in case we somehow didnt reset, even though we check that, reset again
        self.reset()
        self.startTime=self.timeLib.perf_counter()
        self.started=True

    def pause(self):
        #safety checks
        if((not self.started)or self.paused or self.finished):
            if(not self.started):
                raise EasyCLIStopwatchError("error: cannot pause the stopwatch, the stopwatch hasnt been started yet!")
            elif(self.paused):
                raise EasyCLIStopwatchError("error: cannot pause the stopwatch, the stopwatch is already paused!")
            raise EasyCLIStopwatchError("error: cannot pause the stopwatch, the stopwatch has been ended!")
        
        #grab our pause time
        temp=self.timeLib.perf_counter()

        
        if(not self.hasBeenPaused):
            #if we have never paused before, use our origonal start time as the starting time in the durration math, then write down the result
            self.partialElapsedTime=temp - self.startTime
        else:
            #otherwise if we have paused before, subtract our must recent resume time from our pause time then write down the result
            self.partialElapsedTime+=(temp - self.newStartTime)

        #record that we are paused
        self.paused=True
        #record that we have been paused before. yeah, overwrite it even if we have paused before, the overhead of checking isnt worth it
        self.hasBeenPaused=True
        

    def resume(self):
        #safety checks
        if((not self.started)or(not self.paused)or self.finished):
            if(not self.started):
                raise EasyCLIStopwatchError("error: cannot resume the stopwatch, the stopwatch hasnt been started yet!")
            elif(not self.paused):
                raise EasyCLIStopwatchError("error: cannot resume the stopwatch, the stopwatch hasnt been paused yet!")
            elif(self.finished):
                raise EasyCLIStopwatchError("error: cannot resume the stopwatch, the stopwatch has been ended!")
        #get and write down our resume time
        self.newStartTime=self.timeLib.perf_counter()
        #record that we arent paused anymore
        self.paused=False
        

        
    def stop(self):
        #safety checks, set up this way for fast id and nuanced error messages
        if((not self.started) or self.finished):
            if(not self.started):
                raise EasyCLIStopwatchError("error: cannot stop the stopwatch, the stopwatch hasnt been started yet!")
            elif(self.finished):
                raise EasyCLIStopwatchError("error: cannot stop the stopwatch, the stopwatch has already been stopped!")
        
        
        #grab the current time
        self.endTime=self.timeLib.perf_counter()


        #if we have paused, we need to do soem very different logic
        if(self.hasBeenPaused):
            #are we currently paused, becuase if so, we have to do more different logic
            if(self.paused):
                #reset our paused flag
                self.paused=False
                #since we havent resumed since pausing, our total time is our time we calculated when pausing and write it down
                self.totalElapsedTime=self.partialElapsedTime


            else:   
                #if not, first subtract the last time we resumed, from our end time, and then add the time we clocked before our last resume to that and write the result of the whole thing down
                self.totalElapsedTime=((self.endTime - self.newStartTime)+self.partialElapsedTime)



        #if we havent been paused, just do a normal durration calculation
        else:
            #find durration by subtracting start from end, and write it down
            self.totalElapsedTime=self.endTime - self.startTime


        #note down that we have stopped the stopwatch
        self.finished=True


        #return that value we just calulated
        return self.totalElapsedTime
    
    #literally the same as stop, just here in case of mistakes
    def end(self):
        #safety checks, set up this way for fast id and nuanced error messages
        if((not self.started) or self.finished):
            if(not self.started):
                raise EasyCLIStopwatchError("error: cannot end the stopwatch, the stopwatch hasnt been run yet!")
            elif(self.finished):
                raise EasyCLIStopwatchError("error: cannot end the stopwatch, the stopwatch has already been ended!")
        
        
        #grab the current time
        self.endTime=self.timeLib.perf_counter()


        #if we have paused, rwe need to do soem very different logic
        if(self.hasBeenPaused):
            #are we currently paused, becuase if so, we have to do more different logic
            if(self.paused):
                #reset our paused flag
                self.paused=False
                #since we havent resumed since pausing, our total time is our time we calculated when pausing
                self.totalElapsedTime=self.partialElapsedTime


            else:   
                #if not, first subtract the last time we resumed, from our end time, and then add the time we clocked before our last resume to that and write the whole result down
                self.totalElapsedTime=(self.endTime - self.newStartTime)+self.partialElapsedTime
        
        
        #if we havent been paused, just do a normal durration calculation
        else:
            #find durration by subtracting start from end, and write it down
            self.totalElapsedTime=self.endTime - self.startTime


    
        #note down that we have stopped the stopwatch
        self.finished=True



        #return that value we just calulated
        return self.totalElapsedTime
    
    def getElapsedSeconds(self):
        #safety checks
        if(not self.started):
            raise EasyCLIStopwatchError("error: cannot get elasped seconds, the stopwatch hasnt been run yet!")
        elif(not self.finished):
            raise EasyCLIStopwatchError("error: cannot get elasped seconds, the stopwatch is currently running!")
        #return what was asked for
        return self.totalElapsedTime
    

    #need to make a new function for doing this taking into account hours and days
    def getElsapsedSecondsString(self,supportScientificNotation:bool=False,decimalPlaceCutoff:int=12,cutTrailingZeros=True):
        #safety checks
        if(not self.started):
            raise EasyCLIStopwatchError("error: cannot get elasped seconds string, the stopwatch hasn't been run yet!")
        elif(not self.finished):
            raise EasyCLIStopwatchError("error: cannot get elasped seconds string, the stopwatch is currently running!")
        else:
            #if we want scientific notation support, return the raw value
            if(supportScientificNotation):
                return str(self.totalElapsedTime)
            #otherwise grab the decimal place falues up to the decimal place cutoff
            stringManipulationCache="{:."+str(decimalPlaceCutoff)+"f}".format(round(self.getElapsedSeconds(),decimalPlaceCutoff))
            #and if we want to cut trailing zeros 
            if(cutTrailingZeros):
                #do that
                stringManipulationCache=stringManipulationCache.rstrip('0')
            #then cut off any hanging decimal point if it exists
            return stringManipulationCache.rstrip('.')+" second(s)"





      
            
    def getUnitDeviatedTime(self)->tuple:
        #safety checks
        if(not self.started):
            raise EasyCLIStopwatchError("error: cannot get unit separated elapsed time, the stopwatch hasn't been run yet!")
        elif(not self.finished):
            raise EasyCLIStopwatchError("error: cannot get unit separated elapsed time, the stopwatch is currently running!")
        else:
            #there, are you happy now dateTime nuts?!
          
            #init our algoritm variables, they are self explanitory
            #grab a copy of our elapsed time
            totalTime:float=self.totalElapsedTime
            #some flags that explain themselves
            counting=True
            isLeapYear=False
            #self explaitory, how many years worth of seconds we have
            yearCount=0


            #leap year determination algorithm, not the fastest, but im lazy
            while counting:
                
                #if we have a year count divisible by 4 with no remainder(a leap year candidate)
                #and if the year count isnt divisible by 100 or is divisible by 400 
                #(for some reason, idk man, i looked this shit up)
                if(((yearCount % 4) == 0)and(((yearCount % 100) != 0) or ((yearCount % 400) == 0))):
                        #it is a leap year!
                        #record that it is a leap year
                        isLeapYear=True

                        #if we have enough seconds to end the year
                        if((totalTime - 31622400.0) > 0):
                            #increase the year count
                            yearCount+=1
                            #subtract the durration of this year from the time we have left
                            totalTime-=31622400.0
                        else:
                            #otherwise stop looking for more years, we ran out of seconds for there to be another year
                            counting=False
                    
                else:
                    #if it isnt a leap year
                    #record that
                    isLeapYear=False

                    #if we have enough time to complete the year
                    if((totalTime - 31536000.0) > 0):
                        #increase the year count
                        yearCount+=1
                        #subtract the durration of this year from the time we have left
                        totalTime-=31536000.0

                    else:
                        #otherwise stop looking for more years, we ran out of seconds for there to be another year
                        counting=False

            #use this to know when to rollover our days   
            dayDivider=365
            
            #if we ended on a leap year
            if(isLeapYear):
                #change our rollover value to reflect that
                dayDivider=366
            
            #just a stack of math that is much easier tahn that monster up there
            #calculate the number days we are into the year
            days = int((totalTime // 86400) % dayDivider)
            #calulate the number of hours we are into the day
            hours = int((totalTime // 3600) % 24)
            #calculate the number of minutes we are into the hour
            minutes = int((totalTime % 3600) // 60)
            #calulate the number of integer seconds we are into the minute
            intSeconds = int((totalTime % 60))
            #put the int portion of how many seconds in we are in seconds
            seconds=intSeconds

            #if we have decimal parts of our seconds
            if((totalTime % 1) != 0):
                #extract the decimal part and add it to our seconds
                seconds=float(seconds)+float(totalTime % 1)

            #these should never trigger without act of god or value tampering:
            if(yearCount<0):
                raise ArithmeticError("error: somehow calulated years was negitive. bad years value: "+str(yearCount))
            elif(days<0):
                raise ArithmeticError("error: somehow calulated days was negitive. bad days value: "+str(days))
            elif(hours<0):
                raise ArithmeticError("error: somehow calulated hours was negitive. bad hours value: "+str(hours))
            elif(minutes<0):
                raise ArithmeticError("error: somehow calulated minutes was negitive. bad minutes value: "+str(minutes))
            elif(seconds<0):
                raise ArithmeticError("error: somehow calulated seconds was negitive. bad seconds value: "+str(seconds))

            
            
            #now we have the value populated return tree
            #basically, we go through and find the highest deviation of time we calculated that
            #actually has a non zero ovalue in it, then return that 
            #and every deviation below it
            if(yearCount!=0):
                return(yearCount,days,hours,minutes,seconds)
            elif(days!=0):
                return(days,hours,minutes,seconds)
            elif(hours!=0):
                return(hours,minutes,seconds)
            elif(minutes!=0):
                return(minutes,seconds)
            return(seconds,)
            
    def __formatSecondsValueStringInternal__(self,seconds,justSeconds,supportScientificNotation,decimalPlaceCutoff,cutTrailingZeros):
        #if we don't want to format the seconds, and we only have seconds
        if(justSeconds and supportScientificNotation):
            #do absolutely nothing
            return seconds
        
        #otherwise

        #get the int portion of seconds
        intSeconds=int(seconds)
        #init our decimal seconds variable
        decimalSeconds=""
        #if we have a decimal portion
        if((seconds % 1) != 0):
            #round seconds to decimalplacecutoff, string and format seconds to a decimal cutoff of decimalplacecutoff, then extract the fraction portion
            decimalSeconds=("."+(("{:."+str(decimalPlaceCutoff)+"f"+"}").format(round(float(seconds),decimalPlaceCutoff)).split(".")[1]))
            #if we want to cut trailing zeros
            if(cutTrailingZeros):
                decimalSeconds=decimalSeconds.rstrip('0').rstrip(".")
        
        return (str(intSeconds)+decimalSeconds)
        
            
    def getUnitDeviatedTimeString(self,supportScientificNotation:bool=False,decimalPlaceCutoff:int=12,cutTrailingZeros=True):
        #grab our unit deviated time values
        values=self.getUnitDeviatedTime()
        #look, its efficent enough, and i'd like to see you do any better. that isn't a personal challenge by the way, i dont want suggestions here.
        if(len(values)==5):
            return "".join((str(values[0])," year(s), ",str(values[1])," day(s), ",str(values[2])," hour(s), ",str(values[3])," minute(s), and ",self.__formatSecondsValueStringInternal__(values[4],False,supportScientificNotation,decimalPlaceCutoff,cutTrailingZeros)," second(s)"))
        elif(len(values)==4):
            return "".join((str(values[0])," day(s), ",str(values[1])," hour(s), ",str(values[2])," minute(s), and ",self.__formatSecondsValueStringInternal__(values[3],False,supportScientificNotation,decimalPlaceCutoff,cutTrailingZeros)," second(s)"))
        elif(len(values)==3):
            return "".join((str(values[0])," hour(s), ",str(values[1])," minute(s), and ",self.__formatSecondsValueStringInternal__(values[2],False,supportScientificNotation,decimalPlaceCutoff,cutTrailingZeros)," second(s)"))
        elif(len(values)==2):
            return "".join((str(values[0])," minute(s) and ",self.__formatSecondsValueStringInternal__(values[1],False,supportScientificNotation,decimalPlaceCutoff,cutTrailingZeros)," second(s)"))
        elif(len(values)==1):
            return "".join((self.__formatSecondsValueStringInternal__(values[0],True,supportScientificNotation,decimalPlaceCutoff,cutTrailingZeros)," second(s)"))
        raise EasyCLIStopwatchError("error: getUnitDeviatedTimeString emergency safety case somehow trigger, len(values) invalid expected 1-5, received: "+str(len(values)))
    
    def getState(self):
        if(self.finished):
            return 3
        elif(self.paused):
            return 2
        elif(self.started):
            return 1
        else:
            return 0