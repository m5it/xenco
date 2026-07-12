"""
xLife
"""
import os
import time
import re
import sys,getopt
import threading

#--
keepalive    = "xIrcCat.py"
keepalivePid = 0
processName  = os.path.basename(__file__)
processPid   = os.getpid()
cmd          = "ps -A x"
info         = "xLife {} keeping alive: {}. processName: {}".format( processPid, keepalive, processName  )
sleep        = 0.5
stopName     = "xLife.kill"
updating     = False
updateFile   = ""
restarting   = False

#--
def restart():
    os.popen("python {} -r&".format("xLife.py"))
    
#--
def update(filename):
    os.popen("python {} -u {}&".format("xLife.py",filename))

#--
def protect():
    global protectxLife
    #print("protect() start.")
    x = threading.Thread(target=protectxLife)
    x.start()


#--
def protectxLife():
    #print("protectxLife() start.")
    while True:
        if not exists("xLife.py"):
            #print("protectxLife() restarting...")
            os.popen("python {}&".format("xLife.py"))
        time.sleep(5)

#--
def exists(name):
    global cmd, info
    data = os.popen( cmd )
    data = data.read().splitlines()
    keepalivePid = 0
    for line in data:
        if re.match(".*{}.*".format(name),line):
            keepalivePid = int(line[1:].split(" ",2)[0])
            open("xLife.info","w").write("{} - keepalivePid: {}\n".format(info, keepalivePid))
            return keepalivePid
    return keepalivePid

#--
def main(argv):
    global keepalive,updating,updateFile,restarting
    
    try:
        opts, args = getopt.getopt(argv,"u:hr",[])
    except getopt.GetoptError:
        print('need help... :) d1"')
        sys.exit(2)
    #--
    for opt, arg in opts:
        if opt=="-h":
            print("need help...")
            sys.exit(2)
        elif opt=="-u":
            updating=True
            updateFile = arg
        elif opt=="-r":
            restarting=True
    
    if updating or restarting:
        time.sleep(3)
    
    #--
    keepalivePid = exists(keepalive)

    #--
    if keepalivePid==0:
        tmpFile = keepalive
        if updating:
            tmpFile = updateFile
            os.popen("rm {}".format(keepalive))
            os.popen("mv {} {}".format(tmpFile,keepalive))
            open("xLife.info","w").write("{} - updating {}\n".format(info,tmpFile))
        else:
            open("xLife.info","w").write("{} - rerunning {}\n".format(info,keepalive))
        
        os.popen("python {}&".format(keepalive))
    
    #--
    if not restarting and not updating and not os.path.exists(stopName):
        #--
        time.sleep(sleep)
        os.popen("python {}&".format(processName))


#--
if __name__ == '__main__':
    #--
    main(sys.argv[1:])

    try:
        sys.stdout.close()
    except:
        pass
    try:
        sys.stderr.close()
    except:
        pass

