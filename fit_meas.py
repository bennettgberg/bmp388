import sys
import numpy as np
import matplotlib.pyplot as plt

#get np arrays of flow rates and pressure readings
def get_rp(testn):
    rfile = "test{}/rate_bestfit{}.txt".format(testn, testn)
    pfile = "test{}/press_bestfit{}.txt".format(testn, testn)
    sampling_rate = 5
    #number of different flow rate values tested
    #nvals = 50/5 #50 by 5s, but not 20, but yes 0.
    nvals = 18 #1-14, 30, 35, 45, 50.
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

#linear fit for a function that should relate r_arr with p_arr
#inc_big: include the larger-than-normal flow rates/pressures or nah?
def fit_rp_line(p_arr, r_arr, inc_big=True, show=False):
    
    #print("p_arr: " + str(p_arr))
    #print("r_arr: " + str(r_arr))
    if not inc_big:
        p_arr = np.delete(p_arr, [j for j in xrange(len(p_arr)-4, len(p_arr))])
        r_arr = np.delete(r_arr, [j for j in xrange(len(r_arr)-4, len(r_arr))])
    fit = np.polyfit(p_arr, r_arr, 1)
    print("linear fit for dp:\n slope={}, y-int={}".format(fit[0], fit[1]))
    #y-intercept (fit[1] should be close to 0).
    if show:
        x = np.array([float(i) for i in xrange(-5, 25)])
        y = x * fit[0] + fit[1]
        plt.plot(x, y)
        plt.show()
    return fit[0]

def main():
    #test number
    testn = ""
    if len(sys.argv) > 1:
        testn = sys.argv[1]
    else:
        sys.exit("please specify test number.")
    show = False
    r_arr, p_arr, r_err, p_err = get_rp(testn)
    plot_rp(p_arr, r_arr, p_err, r_err, show=show)

    #now fit this to whatever shape it looks like.
    #constant offset is the dp at 0 flow.
    # this offset will change throughout the day and needs to constantly be re-estimated.
    #  therefore it was accounted separately and individually for each value since their tests were ran at different times.
#    p0 = p_arr[0]
#    np.delete( p_arr, 0 )
#    np.delete( r_arr, 0 )
#    n = len(r_arr)
#    p_arr = p_arr - p0*np.ones(n)
    inc_big = True
    m = fit_rp_line(p_arr, r_arr, inc_big=inc_big, show=show)

    #now write to output file.
    outname = "fit_test{}.txt".format(testn)
    of = open(outname, "w")
    of.write("{}\n".format(m))
    of.close()
    print("{} written.".format(outname))

if __name__ == "__main__":
    main()
