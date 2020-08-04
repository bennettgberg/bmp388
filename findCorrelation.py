import sys
import matplotlib.pyplot as plt


#find correlation between average pressure and pressure difference
def findCor(filename, temp=False, alti=False, navg=1):
    f = open(filename, 'r')

    avgs = []
    difs = []
    count = 0
    tot = 0.0
    dtot = 0.0
    for line in f:
        words = line.split()
        p1 = float(words[1])
        p2 = float(words[2])
        t1 = float(words[3])
        t2 = float(words[4])
#        a1 = float(words[5])
#        a2 = float(words[6])
        a1, a2 = 0.0, 0.0

        tmp = (t1 + t2) / 2.0
        #alt = (a1 + a2) / 2.0
        alt = (a2 - a1) / 2.0

        avg = (p1 + p2) / 2.0
        dif = p2 - p1
        if dif < 10:
            continue
        da = a2 - a1

        dtot += dif
        if temp:
            tot += tmp
        else:
            tot += avg
        if count == navg-1:
            count = 0
            tot /= navg
            dtot /= navg
        else:
            count += 1
            continue
#        if temp:
        avgs.append(tot)
#        elif alti:
#            avgs.append(alt)
#        else:
#            avgs.append(avg)
        difs.append(dtot)

    plt.plot(avgs, difs, '.')
    if temp:
        plt.xlabel("Average temperature (C)")
    elif alti:
        plt.xlabel("altitude difference (m)")
    else:
        plt.xlabel("Average pressure (Pa)")
    plt.ylabel("Pressure difference (Pa)")
    if temp:
        plt.title("Average temperature vs. Pressure difference over 2 weeks, 10-meas avg")
    elif alti:
        plt.title("Altitude measurement difference vs. Pressure difference over 2 days")
    else:
        plt.title("Absolute Pressure vs. Pressure difference over 1 week (0 flow)")
    plt.show()

def main():
    #filename = "press_highest_1week.txt"
    filename = "press_2days.txt"
    temp = True
    findCor(filename, temp, False, navg=10)

if __name__ == "__main__":
    main()

