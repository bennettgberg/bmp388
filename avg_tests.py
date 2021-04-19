
import os
#get the average of multiple different tests so that average can be fitted.

tests = ["4", "5"]
rtots = [0. for i in xrange(1, 15)]
ptots = [0. for i in xrange(1, 15)]
rEtot = [0. for i in xrange(1, 15)]
pEtot = [0. for i in xrange(1, 15)]
for i in [30, 35, 45, 50]: 
    rtots.append(0.)
    ptots.append(0.)
    rEtot.append(0.)
    pEtot.append(0.)

for testn in tests:
    inr = "test{}/rate_bestfit{}.txt".format(testn, testn)
    inp = "test{}/press_bestfit{}.txt".format(testn, testn)
    infr = open(inr, "r")
    infp = open(inp, "r")
    for i, line in enumerate(infr):
        ws = line.split()
        rate = float(ws[1])
        err = float(ws[2])
        rtots[i] += rate
        rEtot[i] += err**2
    for i, line in enumerate(infp):
        ws = line.split()
        press = float(ws[1])
        err = float(ws[2])
        ptots[i] += press
        pEtot[i] += err**2
    infr.close()
    infp.close()
#now divide by the number of tests averaged.
for i in range(len(rtots)):
    rtots[i] /= len(tests)
    ptots[i] /= len(tests)
    rEtot[i] = (rEtot[i])**0.5 / len(tests)
    pEtot[i] = (pEtot[i])**0.5 / len(tests)

#now write to output file.
outdirname = "test"
newtestn = ""
for testn in tests:
    newtestn += testn
outdirname += newtestn
if not os.path.exists(outdirname):
    os.system("mkdir {}".format(outdirname))

outr = "{}/rate_bestfit{}.txt".format(outdirname, newtestn)
outp = "{}/press_bestfit{}.txt".format(outdirname, newtestn)
outfr = open(outr, "w")
outfp = open(outp, "w")
labels = [i for i in xrange(1, 15)]
for lab in [30, 35, 45, 50]:
    labels.append(lab)

for i,lab in enumerate(labels):
    outfr.write("{}\t{}\t{}\n".format(lab, rtots[i], rEtot[i]))
    outfp.write("{}\t{}\t{}\n".format(lab, ptots[i], pEtot[i]))

outfr.close()
outfp.close()
print("{} and {} have been written.".format(outr, outp))
print("Use testname \"{}\".".format(newtestn))
