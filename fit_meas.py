import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

show = True #show the plot or nah
sqrt = True #fit to a sqrt or nah (in which case it would be a line).
ln = False #fit to log or nah
inc_big = True
#nvals = 50/5 #50 by 5s, but not 20, but yes 0.
nvals = 18 #1-14, 30, 35, 45, 50.

#get np arrays of flow rates and pressure readings
def get_rp(testn): #, r_arr, p_arr, r_err, p_err):
    rfile = "test{}/rate_bestfit{}.txt".format(testn, testn)
    pfile = "test{}/press_bestfit{}.txt".format(testn, testn)
    #number of different flow rate values tested
    #flow rates
    rates = [0. for i in range(nvals)]
    press = [0. for i in range(nvals)]
    rErr  = [0. for i in range(nvals)]
    pErr  = [0. for i in range(nvals)]

    rf = open(rfile, "r")
    pf = open(pfile, "r")

    for i in range(nvals):
        line = rf.readline()
        words = line.split()
        rlabel = words[0] 
        r = float(words[1])
        rE = float(words[2])
        line = pf.readline()
        words = line.split()
        plabel = words[0]
        if not rlabel == plabel:
            sys.exit("Error: different labels {}, {} in rfile, pfile.".format(rlabel, pfile))
        p = float(words[1])
        pE = float(words[2])
        rates[i] = r
        press[i] = p
        rErr[i] = rE
        pErr[i] = pE

    r_arr = np.array(rates, "f")
    p_arr = np.array(press, "f")
    r_err = np.array(rErr, "f")
    p_err = np.array(pErr, "f")
   # r_arr = np.concatenate((r_arr, rarr))
   # p_arr = np.concatenate((p_arr, parr))
   # r_err = np.concatenate((r_err, rerr))
   # p_err = np.concatenate((p_err, perr))

    return r_arr, p_arr, r_err, p_err

#plot flow rates vs. pressure differences
def plot_rp(p_arr, r_arr, p_err=[], r_err=[], show=False):
    if r_err == []:
        plt.plot(p_arr, r_arr, "s")
    else:
        #errorbar args: x, y, yerr, xerr
        plt.errorbar(p_arr, r_arr, r_err, p_err, '.')
    plt.xlabel("Pressure difference (Pa)")
    plt.ylabel("Flow rate (L/min)")
    plt.title("Average pressure difference vs. average flow rate")
    if not show:
        plt.show()

#define the square root function so you can fit to it.
def func(x, a): #, b, c):
    return (x+0.000001)/abs(x+0.000001) * a * (abs(x))**0.5 #((x-c)/abs(x-c))*a*(abs(x-c))**0.5 + b

def func2(x, a, b, c):
    return a*np.log(b*x) + c

#linear fit for a function that should relate r_arr with p_arr
#inc_big: include the larger-than-normal flow rates/pressures or nah?
#p: pressure (ind. var.), r: flow rate (dep. var.)
def fit_rp_line(p_arr, r_arr):
    
    #print("p_arr: " + str(p_arr))
    #print("r_arr: " + str(r_arr))
    if not inc_big:
        p_arr = np.delete(p_arr, [j for j in xrange(len(p_arr)-4, len(p_arr))])
        r_arr = np.delete(r_arr, [j for j in xrange(len(r_arr)-4, len(r_arr))])
    if ln:
        popt, _ = curve_fit(func2, p_arr, r_arr)
        print("sqrt popt: {}".format(str(popt)))
    elif not sqrt:
        #line
        fit = np.polyfit(p_arr, r_arr, 1)
    else:
        #sqrt (func)
        fit = np.polyfit(r_arr, p_arr, 2)

        popt, _ = curve_fit(func, p_arr, r_arr)
        print("sqrt fit: {}".format(str(fit)))
        print("sqrt popt: {}".format(str(popt)))
        #This gives us y in terms of x. Now solve for y.
        # Use quadratic formula.
#    print("linear fit for dp:\n slope={}, y-int={}".format(fit[0], fit[1]))
    #y-intercept (fit[1] should be close to 0).
    if show:
        x = np.array([float(i) for i in xrange(0, 300)])
        if ln:
            y = func2(x, popt[0], popt[1], popt[2])
        elif not sqrt:
            y = x * fit[0] + fit[1]
        else:
            #y = (-1*fit[1] + (fit[1]**2 - 4*fit[0]*(fit[2] - x))**0.5) / (2*fit[0])
            y = func(x, popt[0]) #, popt[1], popt[2])
        plt.plot(x, y)
        plt.show()
    #return coeff on sqrt, y-int.
    return popt[0]#, popt[1] #fit[0]

#testns is list of all test names to include in the fit
def fit_tests(testns):
    #for each test number
    r_arr, p_arr, r_err, p_err = np.array([]), np.array([]), np.array([]), np.array([])
    for n in testns:
        rarr, parr, rerr, perr = get_rp(n) #, r_arr, p_arr, r_err, p_err)
        plot_rp(parr, rarr, perr, rerr, show=show)
        r_arr = np.concatenate((r_arr, rarr))
        p_arr = np.concatenate((p_arr, parr))
        r_err = np.concatenate((r_err, rerr))
        p_err = np.concatenate((p_err, perr))

    #now fit this to whatever shape it looks like.
    #constant offset is the dp at 0 flow.
    # this offset will change throughout the day and needs to constantly be re-estimated.
    #  therefore it was accounted separately and individually for each value since their tests were ran at different times.
#    p0 = p_arr[0]
#    np.delete( p_arr, 0 )
#    np.delete( r_arr, 0 )
#    n = len(r_arr)
#    p_arr = p_arr - p0*np.ones(n)
    #m = fit_rp_line(p_arr, r_arr, inc_big=inc_big, show=show, sqrt=sqrt, ln=ln)
    a = fit_rp_line(p_arr, r_arr) #,b

    testn = ""
    for n in testns:
        testn += n
    #now write to output file.
    outname = "fit_test{}.txt".format(testn)
    of = open(outname, "w")
    of.write("{}\t{}\n".format(a,a)) #b
    of.close()
    print("{} written.".format(outname))

def main():
    if len(sys.argv) < 2:
        sys.exit("please specify test number(s).")
    testns = []
    for i in xrange(1, len(sys.argv)):
        testns.append( sys.argv[i] )

    fit_tests(testns)

if __name__ == "__main__":
    main()
