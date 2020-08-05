print('Welcome to a simple python script to read and write to a LabJack')

print('Connecting to lab jack...')
import u3 #import the driver for the lab jack

d = u3.U3() #find the labjack and attach
print('Found a labjack!')


#Set up the addresses of the various pins
# Following example: https://labjack.com/support/software/examples/ud/labjackpython/modbus
AIN0_REGISTER = 0
AIN1_REGISTER = 2
DAC0_REGISTER = 5000

import time # import timing library


sampling_freq = 50. #Hz (approximate)
Vmax = 5.0 # volts
Qmax = 100.0 #L/min

#beginning of filename
prefix = "test3/rate_"

#t_wait = 30. #seconds to wait after each voltage change before recording the flow readings
#wait until given the signal to continue
t_meas = 24. #seconds of measurement to take for each flow rate.
realQ = 0.
Vin0 = 0.

print("Hit Control-c at any point to quit")
try:
    while True:
        intext = raw_input("Enter flow rate in L/min or 0_[flow rate] (or press enter to end): ")
        if intext == "": break
        #####if it's nothing it will be an exception, which will then goto the except block anyways mwahaha
        if "0_" in intext:
            Qset = 0.0
        else:
            Qset = int(intext)
        filename = prefix + intext + ".txt"
        f = open(filename, "w")
        #20 L/min is weird for some reason so skip it.
#        if Qset == 20.: continue
        Vout = 5.*Qset/Qmax
        d.writeRegister(DAC0_REGISTER, Vout)
        timestamp = 0.
#added for test2
        cont = raw_input("Press enter when readings are stabilized, or \'k\' to cancel this value. ")
        if cont == 'k': continue
        start_time = time.time()  #seconds since 1970
        #while timestamp < (t_wait + t_meas):
        while timestamp <  t_meas:

            Vin0 = d.readRegister(AIN0_REGISTER)

            timestamp = time.time() - start_time

            #flow rate is proportional to voltage reading.
            realQ = Vin0 / Vmax * Qmax

            #write to output file if it's writing time.
            #if timestamp > t_wait:
            f.write("{}\t{}\n".format(timestamp, realQ))

        # Wait one interval of the sampling rate
            time.sleep(1 / sampling_freq)

        #close output file after each value change now that we're done with it.
        f.close()
        
except:
    pass
#except: #KeyboardInterrupt:
d.writeRegister(DAC0_REGISTER, 0.0)
#    print("Interrupt!")

print("Acabo de set Vout=0. Goodbye.")

