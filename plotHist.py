#!/usr/bin/python
# -*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import numpy as np
import sys, os, math
np.set_printoptions(threshold=sys.maxsize)
#import scipy
from scipy.stats import norm

#tstep is how much time to skip between array fillings (default 10 minutes) (not used anymore)
def fill_arr(filename, arr, flow=False, start=0): #, step=1):
    f = open(filename, "r")
    #end is the array index that we finish with this file at.
    end = start
    j = 0
#    told = -1.0*step #old time
    for line in f:
        words = line.split()
        if not flow:
        #ie pressure measurements
            if len(words) < 3:
                sys.exit("Error: wrong file format.")
            #time, p0, p1 [, t0, t1]
            tnew = float(words[0])
         #   dt = tnew - told
         #   if not abs(dt - step) < 0.01:
         #       print("tnew: {0:f}, told: {1:f}, dt: {2:f}".format(tnew, told, dt))
         #       continue
           # print("GOOD! tnew: {0:f}, told: {1:f}, dt: {2:f}".format(tnew, told, dt)) 
    #        told = tnew
            p0 = float(words[1])
            p1 = float(words[2])
            dp = abs(p0 - p1)
            #0 measurements are failed readings, as are very small dp's.
            print("p0= {}, p1={}, dp={}".format(p0, p1, dp))
#            if p0 == 0.000000 or p1 == 0.000000 or dp < 5.0: continue
#            if dp < 20:
#                print("p0={}, p1={}, dp={}".format(p0, p1, dp))
        else:
            #flow; dp is actually a flow rate now.
            dp = float(words[1])
        if len(arr) < end+1:
            print("Error: array not big enough.\narray length: {0:d}\nTrying to access index {1:d}".format(len(arr), end))
            sys.exit()
        print("appending for the {}th time".format(j))
        arr[end] = p0#dp
        end += 1
        j += 1
    #print("j = {}".format(j))
    
    return end

#flow is true if we're fitting the flow rates instead of the pressure measurements.
#sampling rate in Hz
#t_meas is measurement time in seconds
def fit_hist(filename, sampling_rate=50, t_meas=24, flow=False, show=False):
#    filenames = ["press_highest_7day.txt", "press_highest_1week.txt", "press_highest_2day.txt"]  #could use press_highest_2day.txt but it has different time increments
    n = int(t_meas * sampling_rate)
    #print("n= {}".format(n))
    #pressure differences, to be histogrammed
    #dps = np.zeros(6*24*7*2+6*24*2)
    dps = np.zeros(n)
    #print("dps size = {}".format(len(dps)))
    #fill dps
    end = 0
#    for fn in filenames:
#        start = fill_arr(fn, dps, start)
    end = fill_arr(filename, dps, flow)
    #if filename == "test3/rate_30.txt":
    #    print(str(dps))
    if end != n:
        dps = np.delete(dps, [i for i in range(end, n)])
        print("deleting from {} to {}".format(end, n))

##############for plotting###################################################
    if show:
        #plt.hist(dps, 40, (70, 110))
        minval = int(min(dps))
        maxval = int(math.ceil(max(dps)))
        #hist arguments: x, nbins, (xlow, xhigh)
        plt.hist(dps, maxval - minval, (minval, maxval))

##############################################################################
    mu, sigma = norm.fit(dps)

 ###don't do this   #have to divide sigma by sqrt(N)
#    print("sigma before: {}".format(sigma))
#    sigma = sigma / end**0.5
#    print("sigma after: {}".format(sigma))
    if show:
    ##############################################################################
        plt.xlabel("pressure differences (Pa)")
        plt.ylabel("Number of measurements / 1 Pa")
        plt.title("Histogram of pressure difference measurements for {}".format(filename))
        plt.show()
##############################################################################
    print("mu = {0:f}, sigma = {1:f}".format(mu, sigma))

    return mu, sigma

def full_test():
    #test number
    testn = 5
    show = False #True #show plots or nah
    sampling_rate = 50 #Hz
    t_meas = 24 #s
    flow = False #true for flow rate files, false for pressure reading files
    body = "press_" #body of the file name
    if flow:
        body = "rate_"
    outname = "test{}/{}bestfit{}.txt".format(testn, body, testn)
    of = open(outname, "w")
    values = [i for i in range(1, 15)]
    values.append(30)
    values.append(35)
    values.append(45)
    values.append(50)
    #get best fit for each input file
    for i in values:
        inname = "test{}/{}{}.txt".format(testn, body, i)
        inname0 = "test{}/{}0_{}.txt".format(testn, body, i)
        if not os.path.exists(inname):
            print("Warning: {} does not exist.".format(inname))
            continue
        mu0, sigma0 = fit_hist(inname0, sampling_rate, t_meas, flow, show)
        mu, sigma = fit_hist(inname, sampling_rate, t_meas, flow, show)
        #dp is pressure difference from flow of ~0.4 L/min
        dp = mu
        if not flow:
            dp = mu - mu0
        #what we want is the difference between dp at 0 flow and dp at this flow.
        # but 0 flow is actually ~0.4 L/min flow. So for flow do not subtract mu0.
        of.write("{}\t{}\t{}\n".format(i, dp, sigma))
    of.close()
    print("{} written.".format(outname))
    
def rate_v_rms():
    nmeas = 100

    #rates to test (in Hz)
    rates = [1000., 500., 250., 100., 50., 25., 10., 5., 2., 1.] #, 0.01]
    RMSs = [0.0 for i in range(len(rates))]
    #repeat the same test ntrial times (take their average) to make sure the results are significant.
    ntrial = 10
    for i in range(ntrial):
        #for each rate, run plotP, get 100 samples
        for j,rate in enumerate(rates): 
            suffix = "{}_{}_2021".format(rate, i)
            os.system("python plotP.py {}".format(suffix))
            
            inname = "press_{}.txt".format(suffix)
            t_meas = nmeas/rate
            mu, sigma = fit_hist(inname, rate, t_meas, show=False)
            RMSs[j] += sigma
            if i == ntrial-1:
                RMSs[j] /= ntrial

    plt.plot(rates, RMSs)
    plt.xscale("log")
    plt.title("RMS noise as a function of sampling rate for BMP388")
    plt.xlabel("sampling rate (Hz)", fontsize=16)
    plt.ylabel("RMS noise (Pa)", fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.show()

    
def main():
    #full_test()
  #  sampling_rate = 1
  #  t_meas = 34*1
  #  inname = "press_34sec.txt"
  #  print("Warning: filling with p0, not dp.")
  #  mu, sigma = fit_hist(inname, sampling_rate, t_meas, show=True)
  rate_v_rms()

if __name__ == '__main__':
    main()
