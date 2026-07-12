"""
---------------------------
--== xEnco ==-- by madK0s
---------------------------

# options
-E = encode          (text)
-D = decode          (text)
-f = from ascii char (int)
-t = to ascii char   (int)
-d = debug           (set/not)
-s = silent          (set/not)

# example encode
python xEnco.py -E '!kill 201.160.70.51' -f 40 -t 127 -M https://www.lalaland.com -s

# example decode
python xEnco.py -D '7:1I]iKL>\[N6\/b>+`;>+`?>xQQ' -f 40 -t 127 -M https://www.lalaland.com -s
"""

#import struct
#import urllib
import requests
import base64
import sys, getopt
import re

headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"}
text    = "!reverse 127.0.0.1"
debug   = False
silent  = False

cntFrom    = 32
cntTo      = 128
masterFrom = "https://www.google.com"

optEnc = False
optDec = False

#--
"""magic = {
    "h":0,
    "e":0,
    "l":0,
    "o":0,
    "w":0,
    "r":0,
    "l":0,
    "d":0,
    ",":0,
    " ":0,
    ".":0,
}"""
magic = {}

def xEnco_test():
    print("xEnco test.")

#--
def updateMagic(masterFrom, cntFrom, cntTo):
    global magic, headers
    
    cnt     = 0
    content = ""
    
    #--
    if re.match("^http.*",masterFrom):
        page = requests.get( masterFrom, headers );
        content = page.content
    else:
        content = open(masterFrom).read()
    
    if debug:
        print("content: {}".format(len(content)))
    
    #--
    for i in range(len(content)):
        c = content[i]
        if ord(c)>=cntFrom and ord(c)<=cntTo and c not in magic:
            magic.update({c:cntFrom+cnt})
            cnt+=1
    
    #--
    #for k,v in magic.iteritems():
    for k,v in magic.items():
        if debug:
            print("magic k: {}, v: {}".format(k,v))

#--
def encoX(masterFrom, text, cntFrom, cntTo):
    global magic,optEnc
    enco=""
    
    #--
    updateMagic(masterFrom, cntFrom, cntTo)
    
    #--
    text = base64.b64encode(str.encode(text))
    text = text.decode("utf-8")
    for i in range(len(text)):
        xord = ord(text[i])
        xmag = magic[text[i]]
        xenc = chr(xmag)
        if debug:
            print("enco i: {} c: {}, xord: {}, xmag: {}, xenc: {}".format( i, text[i], xord, xmag, xenc ))
        enco += xenc
    if optEnc:
        print("{}".format(enco))
    return enco

#--
def decoX(masterFrom,text,cntFrom,cntTo):
    global magic,optDec
    deco=""
    
    #--
    updateMagic(masterFrom, cntFrom, cntTo)
    
    for i in range(len(text)):
        #-- python2 - x = magic.keys()[magic.values().index( ord(text[i]) )]
        x = find_key_by_value( ord(text[i]) )
        if debug:
            print("deco i: {} enco: {}, x: {}".format( i, text[i], x ))
        deco += x
    try:
        deco = base64.b64decode(deco).decode("utf-8")
    except:
        return False
        
    if optDec:
        print("{}".format(deco))
    return deco

#--
def find_key_by_value(value):
    global magic
    for k,v in magic.items():
        if v==value:
            return k
    return ""

#--
def main(argv):
    global text, debug, cntFrom, cntTo, optEnc, optDec, masterFrom, silent
    
    try:
        opts, args = getopt.getopt(argv,"sdhE:D:f:t:M:",[])
    except getopt.GetoptError:
        print('need help... :) d1"')
        sys.exit(2)
    #--
    for opt, arg in opts:
        if opt=="-h":
            print("need help... :) d2")
            sys.exit(2)
        elif opt=="-E":
            text = arg
            optEnc=True
        elif opt=="-D":
            text = arg
            optDec=True
        elif opt=="-f":
            cntFrom=int(arg)
        elif opt=="-t":
            cntTo=int(arg)
        elif opt=="-M":
            masterFrom=arg
        elif opt=="-s":
            silent=True
        elif opt=="-d":
            debug=True
    #--
    if optEnc and optDec:
        print("Use only one option.")
        sys.exit(2)
    
    #--
    if not silent:
        print("using -f: {}, -t: {}, -M: {}, text: {}".format(cntFrom,cntTo,masterFrom,text))
    
    
    #-- encode
    if optEnc:
        encoX(masterFrom, text, cntFrom, cntTo)
    
    #-- decode
    if optDec:
        decoX(masterFrom,text,cntFrom,cntTo)

#--
if __name__ == '__main__':
    #--
    main(sys.argv[1:])
