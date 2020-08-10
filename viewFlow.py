import matplotlib.pyplot as plt
import matplotlib.animation as ani
from datetime import datetime
import sys, time

#get string representation of the current time
def strtime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

meas_rate = 50.
dt = 2.
if len(sys.argv) > 2:
    meas_rate = float(sys.argv[1])
    dt = float(sys.argv[2])

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
def animate(i):
    pltfile = open("pltfile.txt", "r")
    
    x = []
    y = []
   # reading_Q = False
    count = 0
    for line in pltfile:
#        print("line = {}".format(line))
        line = line.replace("[", "")
        line = line.replace("]", "")
#        print("line = {}".format(line))
        ws = line.split()
        for w in ws:
            try:
                wf = float(w)
            except:
                print("Error: {} not a valid float!".format(w))
                continue
            y.append(wf)
            count += 1

    pltfile.close()
    end_time = time.time()
    start_time = end_time - 1.0/meas_rate * count
    step = 1.0*dt
    if count != 0:
        step = (end_time - start_time) / count
    t = start_time
#    print("step = {}, dt={}, count={}, start={}, end={}".format(step, dt, count, start_time, end_time))
    for j in range(count):
        x.append(t)
        t += step

    # Draw x and y lists
    ax.clear()
#    print("x:")
#    print(x)
#    print("y:")
#    print(y)
    ax.plot(x, y)
    plt.xlabel("Time")
    ax.set_xticklabels([strtime(k) for k in x])
    plt.ylabel ("Flow rate (L/min)")

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title("Flow Rate")

def main():
    print("Hello.")
    # Set up plot to call animate() function periodically
    anisan = ani.FuncAnimation(fig, animate, interval=int(1000*dt))
    plt.show()

if __name__ == "__main__":
    main()
