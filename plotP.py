#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import math
import bmp388
from matplotlib import pyplot as plt
import sys
import plotFlow

#if diff is True, plot pressure difference instead of absolute pressures.
#if temp is True, plot temperature instead of pressure.
#difdif: True to plot the differences' difference from their average value (over all time)
def plot_from_file(filename="pressures.txt", n=60*5, diff=False, temp=False, navg=1, difdif=False):
    f = open(filename, "r")
    t = [0. for i in range(n)]
    p0 = [0. for i in range(n)]
    p1 = [0. for i in range(n)]
    dp = [0. for i in range(n)]
    t0 = [0. for i in range(n)] #temperature measured by b1
    t1 = [0. for i in range(n)]
    dt = [0. for i in range(n)] #temp difference, not time
    p2 = [0. for i in range(n)] #pressure measured by b2
    t2 = [0. for i in range(n)] #temperature measured by b2
    dp0 = [0. for i in range(n)] #pressure dif between b2 and b0
    dp1 = [0. for i in range(n)] #pressure dif between b2 and b1
    dt0 = [0. for i in range(n)] #temp dif between b2 and b0
    dt1 = [0. for i in range(n)] #temp dif between b2 and b1
    count = 0
    for j, line in enumerate(f):
        if j >= n:
            t.append(0.)
            p0.append(0.)
            p1.append(0.)
            dp.append(0.)
            t0.append(0.)
            t1.append(0.)
            dt.append(0.)
            p2.append(0.)
            t2.append(0.)
            dp0.append(0.)
            dp1.append(0.)
            dt0.append(0.)
            dt1.append(0.)
        words = line.split()
        t[j] = float(words[0])
        p0[j] = float(words[1])
        p1[j] = float(words[2])
        dp[j] = (p0[j] - p1[j])
     #   if dp[j] < 20:
     #       print("p0= {}, p1={}, dp={}".format(p0[j], p1[j], dp[j]))
        t0[j] = float(words[3])
        t1[j] = float(words[4])
        dt[j] = abs(t1[j] - t0[j])
        if len(words) > 4:
            p2[j] = float(words[5])
            t2[j] = float(words[6])
            dp0[j] = p0[j] - p2[j]
            dp1[j] = p1[j] - p2[j]
            dt0[j] = t0[j] - t2[j]
            dt1[j] = t1[j] - t2[j]
        count = j+1

    #averages
    t_a = [0. for i in xrange(count/navg)]
    p0_a = [0. for i in xrange(count/navg)] #+1-navg)/navg)]
    p1_a = [0. for i in xrange(count/navg)] #+1-navg)/navg)]
    dp_a = [0. for i in xrange(count/navg)] #+1-navg)/navg)]
    t0_a = [0. for i in xrange(count/navg)] #+1-navg)/navg)] #temperature measured by b1
    t1_a = [0. for i in xrange(count/navg)] #+1-navg)/navg)]
    dt_a = [0. for i in xrange(count/navg)] #+1-navg)/navg)] #temp difference, not time
    p2_a = [0. for i in xrange(count/navg)] 
    t2_a = [0. for i in xrange(count/navg)] 
    dp0_a = [0. for i in xrange(count/navg)] 
    dp1_a = [0. for i in xrange(count/navg)] 
    dt0_a = [0. for i in xrange(count/navg)] 
    dt1_a = [0. for i in xrange(count/navg)] 
    #averages over all time
    dp_avg = 0.0
    dp0_avg = 0.0
    dp1_avg = 0.0
    
    #now get the navg-measurement averages.
    ct_a = 0 #count for avg lists
    for j in xrange(navg/2, count-(count%navg), navg):
        avg = 0
        for k in xrange(j-navg/2, j+navg/2 +(navg % 2)):
#            print("j={} k={} ct_a={} navg={} count={} length={}".format(j, k, ct_a, navg, count, len(p0_a)))
#            print("j:{}, k:{}, ct_a:{}, navg:{}, count:{}".format(j, k, ct_a, navg, count))
            a = p0[k]
            p0_a[ct_a] += a
            p1_a[ct_a] += p1[k]
            dp_a[ct_a] += dp[k]
            t0_a[ct_a] += t0[k]
            t1_a[ct_a] += t1[k]
            dt_a[ct_a] += dt[k]
            p2_a[ct_a] += p2[k]
            t2_a[ct_a] += t2[k]
            dp0_a[ct_a] += dp0[k]
            dp1_a[ct_a] += dp1[k]
            dt0_a[ct_a] += dt0[k]
            dt1_a[ct_a] += dt1[k]

            dp_avg += dp[k]
            dp0_avg += dp0[k]
            dp1_avg += dp1[k]
        if j != 0 and t[j] == 0:
            print("Error: time is 0. j = {0:d}, ct_a = {1:d}".format(j, ct_a))
        t_a[ct_a] = t[j]
        p0_a[ct_a] /= navg
        p1_a[ct_a] /= navg
        dp_a[ct_a] /= navg
        t0_a[ct_a] /= navg
        t1_a[ct_a] /= navg
        dt_a[ct_a] /= navg
        p2_a[ct_a] /= navg
        t2_a[ct_a] /= navg
        dp0_a[ct_a] /= navg
        dp1_a[ct_a] /= navg
        dt0_a[ct_a] /= navg
        dt1_a[ct_a] /= navg
        ct_a += 1
        
    dp_avg /= (ct_a*navg)
    dp0_avg /= (ct_a*navg)
    dp1_avg /= (ct_a*navg)
    #subtract off the average value of each (to get fluctuation around 0)
    #  only if difdif is True.
    if difdif:
        for i in range(ct_a):
            dp_a[i] -= dp_avg
            dp0_a[i] -= dp0_avg
            dp1_a[i] -= dp1_avg

    #plot the relevant item(s)
    if not diff and not temp:
        #pressures
        plt.plot(t_a, p0_a)
        plt.plot(t_a, p1_a)
        plt.plot(t_a, p2_a)
    elif not temp:
        #pressure difference
#        plt.plot(t_a, dp_a)
        plt.plot(t_a, dp0_a)
        plt.plot(t_a, dp1_a)
    elif not diff:
        #temperatures
        plt.plot(t_a, t0_a)
        plt.plot(t_a, t1_a)
        plt.plot(t_a, t2_a)
    else:
        #temperature difference
        plt.plot(t_a, dt_a)
        plt.plot(t_a, dt0_a)
        plt.plot(t_a, dt1_a)

    #label the axes
    plt.xlabel("time (s)")
    ylab = ""
    if not temp:
        ylab += "pressure "
    else:
        ylab += "temperature "
    if diff:
        ylab += "differences "
    if temp:
        ylab += "(deg. C)"
    else:
        ylab += "(Pa)"
    plt.ylabel(ylab)
#    plt.xticks([int(t[j]) for j in range(0, n, 60)])
    #get max, min y values to set reasonable tick marks.
#    ymin = float('inf')
#    ymax = 0.0
#    for j in range(n): 
#        ymin = min(ymin, p0[j], p1[j])
#        ymax = max(ymax, p0[j], p1[j])
#    plt.yticks([k for k in range(int(ymin/1000)*1000, int(ymax), 50)])
    #title = "Highest resolution: "
    title = ""
    if not temp:
        title += "Pressure"
    else: 
        title += "Temperature"
    if diff:
        title += " Difference"
    else:
        title += "s"
    if difdif:
        title += ", fluctuation around average value"
    if navg != 1:
        title += " avg. over %d measurements"%(navg)
    plt.title(title)
#    plt.show()

#filename is file to write data to (to save time)
#t_meas is total time to take measurements (in seconds)
#sampling_rate is how many times per second to take a measurement.
def run_test(filename="", t_meas=120., sampling_rate=5.):
    t = t_meas #time in seconds to run the test
    n = int(round(t*sampling_rate))  #number of measurements to take
    b0 = bmp388.BMP388()  #default address is 0x77
    b1 = bmp388.BMP388(0x76)
    b2 = bmp388.BMP388(0x77, 0x06)
    #read enablement
  #  en = b1._read_byte(0x1B)
  #  print("before: enabled: {0:b}".format(en))

    #set resolution
    b0.set_osrp(32)
    b1.set_osrp(32)
    b2.set_osrp(32)
    #read resolution
  #  res = b1._read_byte(0x1C)
  #  print("pressure resolution: {0:b}".format(res))
    #read enablement
 #   en = b1._read_byte(0x1B)
 #   print("after: enabled: {0:b}".format(en))
    #put in 'sleep' mode, required before going into forced mode
    b0._write_byte(0x1B, 0b000011)
    b1._write_byte(0x1B, 0b000011)
    b2._write_byte(0x1B, 0b000011)
  #  #read enablement
   # en = b1._read_byte(0x1B)
   # print("sleep mode? enabled: {0:b}".format(en))
    
  #  #turn pressure sensor off then on again
  #  b1._write_byte(0x1B, 0b110010 )
  #  b1._write_byte(0x1B, 0b110011)
  #  #read enablement
  #  en = b1._read_byte(0x1B)
  #  print("on?: enabled: {0:b}".format(en))
    
#    while True:
#        try:
#            #put in 'forced' mode, ie sleep between readings.
#            b0._write_byte(0x1B, 0b100011)
#            temperature,pressure,altitude = b0.get_temperature_and_pressure_and_altitude()
#            b1._write_byte(0x1B, 0b100011)
#            temperature,pressure,altitude = b1.get_temperature_and_pressure_and_altitude()
#            b2._write_byte(0x1B, 0b100011)
#            temperature,pressure,altitude = b2.get_temperature_and_pressure_and_altitude()
#        except:
#            continue
#        break
    #Get first measurement out of the way since it's always shite
    plotFlow.readPs(b0, b1, b2)

    times = [i*t/(n) for i in range(n)]  #divide by 3600 for hours, don't for seconds
    p0 = [0.0 for i in range(n)]
    p1 = [0.0 for i in range(n)]
    p2 = [0.0 for i in range(n)]
    #also keep track of the temperatures
    temp0 = [0.0 for i in range(n)]
    temp1 = [0.0 for i in range(n)]
    temp2 = [0.0 for i in range(n)]
    #write data to file so don't have to rerun just to fix graph (only if filename is provided).
    start_time = time.time()
    for i in range(n):
        if filename != "" and i == 0:
            f = open(filename, "w")
        elif filename != "":
            f = open(filename, "a")
        time.sleep(t/n)
        #read resolution to make sure it hasn't changed
#        res = b1._read_byte(0x1C)
#        print("time= {} pressure resolution= {}".format(times[i], res))
        #put in 'forced' mode, ie sleep between readings.
        #sometimes fails randomly.
 #       while True:
 #           try:
 #               b0._write_byte(0x1B, 0b100011)
 #               temperature,pressure,altitude = b0.get_temperature_and_pressure_and_altitude()
 #               #if the pressure reading is preposterous, get a better one.
 #               if abs(pressure - last_p0) > 20000:
 #                   print("Warning: b0 read preposterous pressure {} at {}".format(pressure/100.0, (time.time()-start_time)))
 #                   continue
 #               last_p0 = pressure
 #               break
 #           except:
 #               print("Warning: write_byte failed for b0 at {}.".format((time.time()-start_time)))
 #               continue
 #     #  #read enablement
##        en = b1._read_byte(0x1B)
##        print("forced mode? enabled: {0:b}".format(en))
 #     #  #read enablement
 #  #     en = b1._read_byte(0x1B)
 #  #     print("sleep mode? enabled: {0:b}".format(en))
 #       p0[i] = pressure/100.0
 #       temp0[i] = temperature/100.0
 #      # print('time=%f Temperature = %.1f Pressure = %.2f  Altitude =%.2f '%(times[i], temperature/100.0,pressure/100.0,altitude/100.0))
 #       #put in 'forced' mode, ie sleep between readings.
 #       try:
 #           b1._write_byte(0x1B, 0b100011)
 #           temperature,pressure,altitude = b1.get_temperature_and_pressure_and_altitude()
 #       except:
 #           print("Warning: write_byte failed for b1 at {}.".format((time.time()-start_time)))
 #           continue
 #      #print('b1: Temperature = %.1f Pressure = %.2f  Altitude =%.2f '%(temperature/100.0,pressure/100.0,altitude/100.0))
 #       p1[i] = pressure/100.0
 #       temp1[i] = temperature/100.0
 #       try:
 #           b2._write_byte(0x1B, 0b100011)
 #           temperature,pressure,altitude = b2.get_temperature_and_pressure_and_altitude()
 #       except:
 #           print("Warning: write_byte failed for b2 at {}.".format((time.time()-start_time)))
 #           continue
 #      #print('b1: Temperature = %.1f Pressure = %.2f  Altitude =%.2f '%(temperature/100.0,pressure/100.0,altitude/100.0))
 #       p2[i] = pressure/100.0
 #       temp2[i] = temperature/100.0
        prevPs = (-1, -1, -1)
        if i != 0:
            prevPs = (p0[i-1], p1[i-1], p2[i-1])
        p0[i], p1[i], p2[i], temp0[i], temp1[i], temp2[i] = plotFlow.readPs(b0, b1, b2, inc_temp=True, prevPs=prevPs)
        if filename != "":
            f.write("%f\t%f\t%f\t%f\t%f\t%f\t%f\n"%(times[i], p0[i], p1[i], temp0[i], temp1[i], p2[i], temp2[i]))
            f.close()
       # p2[i] = p1[i] - p0[i]
#       print(press[i])

#    plt.plot(times, p0)
#    plt.plot(times, p1)
#    plt.xlabel("time (s)")
#    plt.ylabel("Measured Pressure (Pa)")
#    plt.title("Highest Resolution Pressure measurements")
#    plt.show()

def main():
    filename = "press_15mins.txt"
    testn = 5
    t_meas = 60*15. #24. #measurement time (s)
    sampling_rate = 50.0 #1.0 / 10 #Hz
#    print("file will be saved to directory test{}.".format(testn))
    #if there's an argument, it is a label for the output filename.
    if len(sys.argv) > 1:
        label = sys.argv[1]
        filename = "test{}/press_{}.txt".format(testn, label)
#    else:
#        sys.exit("Please specify pressure.")
    #filename = "press_highest_1week.txt"
    #run_test(filename, t_meas, sampling_rate)
    plot_from_file(filename, diff=True, temp=False, navg=1, difdif=True)
    plt.show()

if __name__ == '__main__':
    main()
