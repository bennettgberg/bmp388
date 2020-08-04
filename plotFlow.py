
#program to plot current flow rate using pressure difference measurements from bmp388s (and an appropriate fit).
import bmp388
import sys, time, os
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
np.set_printoptions(threshold=sys.maxsize)

def strtime():
    now = datetime.now()
    strt = now.strftime("%H:%M:%S")
    return strt

#read both bmp388s
def readPs(ba, bb, bc):
    #return the pressures read from the two bmp388 objects
    Ps = [-1., -1., -1.]
    for i, obj in enumerate([ba, bb, bc]):
        #account for possible exception
        while True:
            try:
                #put in 'forced' mode, ie sleep between readings.
                obj._write_byte(0x1B, 0b100011)
                #now get reading
                temperature,Ps[i],altitude = obj.get_temperature_and_pressure_and_altitude()
                Ps[i] /= 100.0
            except KeyboardInterrupt:
                print("Exiting.")
                sys.exit()
            except:
                print("Warning: reading from B{} failed at {}".format(i, strtime()))
                continue
            break
    if abs(Ps[0] - Ps[1]) > 200 :
        print("time: {}, Ps[0]: {}, Ps[1]: {}, dp = {}".format(strtime(), Ps[0], Ps[1], (Ps[0] - Ps[1])))
    return Ps[0], Ps[1], Ps[2]

#global parameters
sampling_rate = 50. #Hz, how often to take a measurement from the bmp388s
t_p0 = 60. #s, time over which to average all measurements to find average differences.
N = int(t_p0 * sampling_rate) #number of measurements to store
update_rate = 0.5 #Hz, how often to update the plot.
dt = int(1/update_rate)

def main():
    testn = 3
    print("Hello. Welcome to the flow rate tracker.")
    print("Using test {} for pressure to flow rate conversion.".format(testn))

    fitname = "fit_test{}.txt".format(testn)
    fitfile = open(fitname, "r")
    line = fitfile.readline()
    #for now we are just using a linear fit, so should only be one word (the slope of the line).
    #  must calculate the y-int constantly (it changes as the day goes on).
    words = line.split()

    slope = float(words[0])

    #start p0 (y-int) at a reasonable value, will change as more measurements are taken.
#    p0 = -75.0 
    dpA_avg = -100. #avg for pC - pA
    dpB_avg = -25.  #avg for pC - pB
    dp0_avg = -75.  #avg for pB - pA

    #number of pressure measurements to average over for calculating Q.
    navg = 50
    #array of the last navg (final adjusted) readings
    vRecentP = np.array([])


    recentPA = np.array([]) #last N dpA measurements
    recentPB = np.array([]) #last N dpB measurements
    recentP0 = np.array([]) #last N dp measurements
    pAtot = 0. #sum of all members of recentPA array
    pBtot = 0. #sum of all members of recentPB array
    p0tot = 0. #sum of all members of recentP0 array
    recentT = np.array([]) #last N times of measurement
    recentQ = np.array([]) #last N Q values
    #connect to the BMP388s
    Ba = bmp388.BMP388()  #default address is 0x77
    Bb = bmp388.BMP388(0x76)
    Bc = bmp388.BMP388(0x77, 0x06)
    #set resolution to maximum.
    Ba.set_osrp(32)
    Bb.set_osrp(32)
    Bc.set_osrp(32)
    #put in 'sleep' mode, required before going into forced mode
    Ba._write_byte(0x1B, 0b000011)
    Bb._write_byte(0x1B, 0b000011)
    Bc._write_byte(0x1B, 0b000011)
    #get first measurement out of the way because it's shite
    pa,pb,pc = readPs(Ba, Bb, Bc)
#    pa,pb = readPs(Ba, Bb)
#    time.sleep(1/sampling_rate)
#    pa,pb = readPs(Ba, Bb)

    realtot = 0. #total of last navg real dp readings (with p0 subtracted off)
    last_update = time.time() #last time the plot was updated
#    ani.FuncAnimation(fig, animate, interval=int(1.0/update_rate))
#    plt.show()
#    plt.ion()
    #call the visualization program to run in the background.
    os.system("python viewFlow.py {} {} &".format(sampling_rate, dt))
    #take measurements until the program is killed.
    try:
        print("Starting to take measurements.")
        while True:
            #read the two bmp388s
            pa,pb,pc = readPs(Ba, Bb, Bc)
            #take their difference
            dp = pa - pb
            dpA = pa - pc
            dpB = pb - pc 
            #print("dp = {}".format(dp))
            # subtract the constant offsets to find the fluctuation.
            dp_real =  (dp-dp0_avg) - (dpA_avg - dpA) + (dpB_avg - dpB)
#            print("pa={}, pb={}, pc={}, dp={}, dpA={}, dpB={}, dpA_avg={}, dpB_avg={}, dp_real={}".format(pa,pb,pc,dp,dpA,dpB,dpA_avg,dpB_avg,dp_real))
            
            if len(vRecentP) == navg:
                realtot -= vRecentP[0]
                vRecentP = np.delete(vRecentP, 0)
            vRecentP = np.append(vRecentP, dp_real)
            realtot += dp_real
            #divide by the length of vRecentP so that the first navg values are also reasonable.
            dp_avg = realtot / len(vRecentP)
            #calculate the flow rate. (subtract 0.5 because that was what the slope was calculated relative to.)
            Q = slope * dp_avg - 0.5
            
            #update the plot file if it's time to do so.
            # (the actual plotting will be done by viewFlow.py)
            t = time.time() 
            #print("t = {}".format(t))
            if t - last_update > 1.0/update_rate:
               # plt.plot(recentT, recentQ)
#                print("recentQ= {}\nrecentP={}".format(str(recentQ), str(recentP)))
               # plt.xlabel("Time (s)")
               # plt.ylabel("Flow rate (L/min)")
               # plt.title("Flow Rate")
#                plt.draw()
               # plt.show()
                pltfile = open("pltfile.txt", "w")
              #  pltfile.write(str(recentT) + "\n")
                pltfile.write(str(recentQ) + "\n")
                pltfile.close()
                last_update = t

            #calculate the latest value of p0 and update the recentP array.
            if len(recentPA) == N:
                oldpA = recentPA[0]
                oldpB = recentPB[0]
                oldp0 = recentP0[0]
                pAtot -= oldpA
                pBtot -= oldpB
                p0tot -= oldp0
                recentPA = np.delete(recentPA, 0)
                recentPB = np.delete(recentPB, 0)
                recentP0 = np.delete(recentP0, 0)

            recentPA = np.append(recentPA, dpA)
            recentPB = np.append(recentPB, dpB)
            recentP0 = np.append(recentP0, dp)
            #print("recentP: " + str(recentP))
            pAtot += dpA
            pBtot += dpB
            p0tot += dp
            dpA_avg = pAtot / len(recentPA)
            dpB_avg = pBtot / len(recentPB)
            dp0_avg = p0tot / len(recentP0)

            #also update the recentT and recentQ arrays.
            if len(recentT) == N:
                recentT = np.delete(recentT, 0)
                recentQ = np.delete(recentQ, 0)
            recentT = np.append(recentT, strtime())
            recentQ = np.append(recentQ, Q)

            time.sleep(1.0/sampling_rate)

    except KeyboardInterrupt:
        print("Ending program.")
        #must kill the background process


if __name__ == "__main__":
    main()
