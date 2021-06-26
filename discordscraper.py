# -*- coding: utf-8 -*-
################################################################################
## Message Scraper for discord archival                                       ##
################################################################################
#                                                                             ##
# Permission is hereby granted, free of charge, to any person obtaining a copy##
# of this software and associated documentation files (the "Software"),to deal##
# in the Software without restriction, including without limitation the rights##
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell   ##
# copies of the Software, and to permit persons to whom the Software is       ##
# furnished to do so, subject to the following conditions:                    ##
#                                                                             ##
# Licenced under GPLv3                                                        ##
# https://www.gnu.org/licenses/gpl-3.0.en.html                                ##
#                                                                             ##
# The above copyright notice and this permission notice shall be included in  ##
# all copies or substantial portions of the Software.                         ##
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
################################################################################
"""
Discord bot message archival
    --saveformat sets the defaults save format

"""
################################################################################
# Imports
################################################################################
print("[+] Starting Discord Scraping Utility")
TESTING = True

import base64
import sys,os
import pandas
import logging
import pkgutil
import inspect
import requests
import traceback
import threading
import subprocess
from time import sleep
from sys import stderr
from io import BytesIO
from pathlib import Path
from datetime import date
from os import _exit as exit
from mimetypes import MimeTypes
from signal import SIGINT, signal
from sys import stderr, version_info
from os import makedirs, getcwd, path
from datetime import datetime, timedelta
from urllib.parse import urlparse
import discord
import PIL
from discord.ext import commands, tasks

###############################################################################
#                Flask Server / Flask Routes / User Interface
###############################################################################
#from sqlalchemy import inspect

import flask
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists
from flask import Flask, render_template, Response, Request ,Config

###############################################################################
#                        Command Line Arguments
###############################################################################
import argparse
parser = argparse.ArgumentParser(description='Discord Message Archival')
parser.add_argument('--imagestoretype',
                                 dest    = 'saveformat',
                                 action  = "store" ,
                                 default = "file", 
                                 help    = "set if images are saved in the DB as text or externally as files, OPTIONS: 'file' OR 'base64. " )
parser.add_argument('--messagelimit',
                                 dest    = 'limit',
                                 action  = "store" ,
                                 default = "10000", 
                                 help    = "Number of messages to download" )
parser.add_argument('--databasename',
                                 dest    = 'dbname',
                                 action  = "store" ,
                                 default = "discordmessagehistory", 
                                 help    = "Name of the file to save the database as" )
parser.add_argument('--databasetype',
                                 dest    = 'dbtype',
                                 action  = "store" ,
                                 default = "sqlite3", 
                                 help    = "text storage format, can be 'sqlite3' OR 'csv', This applies to base64 image data as well" )
parser.add_argument('--imagesaveformat',
                                 dest    = 'imagesaveformat',
                                 action  = "store" ,
                                 default = ".png", 
                                 help    = "File extension for images" )
arguments = parser.parse_args()
################################################################################
# Terminal Colorication Imports
################################################################################

try:
    import colorama
    from colorama import init
    init()
    from colorama import Fore, Back, Style
    if TESTING == True:
        COLORMEQUALIFIED = True
except ImportError as derp:
    print("[-] NO COLOR PRINTING FUNCTIONS AVAILABLE, Install the Colorama Package from pip")
    COLORMEQUALIFIED = False

print("[+] Basic imports completed")

################################################################################
# Variables
################################################################################
discord_bot_token   = "NzE0NjA3NTAyOTg1MDAzMDgw.XxV-HQ.mn5f97TDYXtuFVgTwUccfsW4Guk"
COMMAND_PREFIX      = "."
bot_help_message = "I AM"
BOT_PERMISSIONS     = 3072
devs                = [712737412018733076]
#cog_directory_files = os.listdir("./things_it_does/cogs")
load_cogs           = False
bot = commands.Bot(command_prefix=(COMMAND_PREFIX))
###############################################################################
#   LOGGING
###############################################################################
domainlist = ['discordapp.com', 'discord.com', "discordapp.net"]
attachmentsurl = "/attachments/"
client = discord.Client()
guild = discord.Guild
SAVETOCSV = arguments.saveformat
today = date.today()
log_file            = 'LOGGING LOGGER LOG'
logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s', filemode='w')
logger              = logging.getLogger()
script_cwd          = Path().absolute()
script_osdir        = Path(__file__).parent.absolute()
###############################################################################
#   Lambdas
###############################################################################
redprint          = lambda text: print(Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
blueprint         = lambda text: print(Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
greenprint        = lambda text: print(Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
yellowboldprint = lambda text: print(Fore.YELLOW + Style.BRIGHT + ' {} '.format(text) + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
makeyellow        = lambda text: Fore.YELLOW + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else text
makered           = lambda text: Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makegreen         = lambda text: Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makeblue          = lambda text: Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
debugmessage     = lambda message: logger.debug(blueprint(message)) 
info_message      = lambda message: logger.info(greenprint(message))   
warning_message   = lambda message: logger.warning(yellowboldprint(message)) 
error_message     = lambda message: logger.error(redprint(message)) 
critical_message  = lambda message: logger.critical(yellowboldprint(message))
scanfilesbyextension = lambda directory,extension: [f for f in os.listdir(directory) if f.endswith(extension)]

greenprint("[+] Variables Set!")

################################################################################
##############                      SYSTEM                     #################
################################################################################
def errormessage(message):
    exc_type, exc_value, exc_tb = sys.exc_info()
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    try:
        error( message + ''.join(trace.format_exception_only()))
        #traceback.format_list(trace.extract_tb(trace)[-1:])[-1]
        blueprint('LINE NUMBER >>>' + str(exc_tb.tb_lineno))
    except Exception:
        error("EXCEPTION IN ERROR HANDLER!!!")
        redprint(message + ''.join(trace.format_exception_only()))

def sigintEvent(sig, frame):
    print('You pressed CTRL + C')
    exit(0)
signal(SIGINT, sigintEvent)

def error(message):
    # Append our message with a newline character.
    redprint('[ERROR]: {0}\n'.format(message))
    # Halt the script right here, do not continue running the script after this point.
    exit(1)

def warn(message):
    """Throw a warning message without halting the script.
    :param message: A string that will be printed out to STDERR.
    """
    # Append our message with a newline character.
    yellowboldprint('[WARN] {0}\n'.format(message))
################################################################################
##############                      CONFIG                     #################
################################################################################
#TEST_DB            = 'sqlite://'
DATABASE           = arguments.dbname
LOCAL_CACHE_FILE   = 'sqlite:///' + DATABASE + ".db"
DATABASE_FILENAME  = DATABASE + '.db'

if database_exists(LOCAL_CACHE_FILE) or os.path.exists(DATABASE_FILENAME):
    DATABASE_EXISTS = True
else:
    DATABASE_EXISTS = False        
  
class Config(object):
# TESTING = True
# set in the std_imports for a global TESTING at top level scope
    SQLALCHEMY_DATABASE_URI = LOCAL_CACHE_FILE
    SQLALCHEMY_TRACK_MODIFICATIONS = False

try:
    engine = create_engine(LOCAL_CACHE_FILE , connect_args={"check_same_thread": False},poolclass=StaticPool)
    PybashyDatabase = Flask(__name__ )
    PybashyDatabase.config.from_object(Config)
    DiscordMsgDB = SQLAlchemy(PybashyDatabase)
    DiscordMsgDB.init_app(PybashyDatabase)
    if TESTING == True:
        DiscordMsgDB.metadata.clear()
except Exception:
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    error_message("[-] Database Initialization FAILED \n" + ''.join(tb.format_exception_only()))

###############################################################################
#                DATABASE MODELS
###############################################################################

class DiscordMessage(DiscordMsgDB.Model):
    __tablename__       = 'Messages'
    #__table_args__      = {'extend_existing': True}
    id       = DiscordMsgDB.Column(DiscordMsgDB.Integer,
                           index         = True,
                           unique        = True,
                           autoincrement = True)
    channel   = DiscordMsgDB.Column(DiscordMsgDB.String(256), primary_key   = True)
    time      = DiscordMsgDB.Column(DiscordMsgDB.String(64))
    sender    = DiscordMsgDB.Column(DiscordMsgDB.string(64))
    content   = DiscordMsgDB.Column(DiscordMsgDB.Text)
    #filelocation or base64
    file      = DiscordMsgDB.Column(DiscordMsgDB.Text)

    def __repr__(self):
        return '''=========================================
channel : {}
sender : {} 
time : {} 
message : {} 
'''.format(self.channel,
            self.sender,
            self.time,
            self.message
        )

###############################################################################
###             DATABASE FUNCTIONS
#########################################################
def add_to_db(thingie):
    """
    Takes SQLAchemy model Objects 
    For updating changes to Class_model.Attribute using the form:
        Class_model.Attribute = some_var 
        add_to_db(some_var)
    """
    try:
        DiscordMsgDB.session.add(thingie)
        DiscordMsgDB.session.commit
        redprint("=========Database Commit=======")
        greenprint(thingie)
        redprint("=========Database Commit=======")
    except Exception as derp:
        print(derp)
        print(makered("[-] add_to_db() FAILED"))

def ReturnMessageVar(message, var):
    return message.query.filter_by(var)

def ReturnMessageById(idnum):
    DiscordMsgDB.session.query(idnum)

def querychannelall(channelname):
    DiscordMsgDB.session.query(DiscordMessage).filter_by(channel = channelname)

def addmsgtodb(msg_to_add):
    """
    "name" is the primary key of DB, is unique
    """
    try:
        if DiscordMsgDB.session.query(msg_to_add).filter_by(name=msg_to_add.name).scalar() is not None:
            info_message('[+] Duplicate Entry Avoided : ' + msg_to_add.sender + " : " + msg_to_add.time)
        # and doesnt get added
        else: # and it does if it doesnt... which works out somehow ;p
            DiscordMsgDB.session.add(msg_to_add)
            info_message('[+] Message Added To Database : ' + msg_to_add.sender + " : " + msg_to_add.time)
    except Exception:
        errormessage("[-] addmsgtodb() FAILED")

def update_db():
    try:
        DiscordMsgDB.session.commit()
    except Exception as derp:
        print(derp.with_traceback)
        print(makered("[-] Update_db FAILED"))


def doesexistbyID(plant_name):
    try:
        exists = DiscordMsgDB.session.query(DiscordMessage.id) is not None
    except Exception:
        errormessage('[-] Database VERIFICATION FAILED!')
    if exists:
        info_message("[-] Message already in database... Skipping!")
        return True
    else:
        return False

def does_exists(self,Table, Row):
    try:
        if DiscordMsgDB.session.query(Table.id).filter_by(name=Row).first() is not None:
            info_message('[+] MESSAGE {} Exists'.format(Row))
            return True
        else:
            return False        
    except Exception:
        errormessage('[-] Database VERIFICATION FAILED!')

def table_exists(name):
    try:
        from sqlalchemy import inspect
        blarf = inspect(engine).dialect.has_table(engine.connect(),name)
        if blarf:
            info_message('[+] Database Table {} EXISTS'.format(name))
            return True
        else:
            return False
    except Exception:
        errormessage("[-] TABLE {} does NOT EXIST!".format(name))
        return False

greenprint("[+] Database functions loaded!")

###############################################################################
#                DISCORD COMMANDS
###############################################################################
# WHEN STARTED, APPLY DIRECTLY TO FOREHEAD
@bot.event
async def on_ready():
    print("Discrod Scraper ALPHA")
    await bot.change_presence(activity=discord.Game(name="Chembot - type .help"))
    #await lookup_bot.connect()

def filtermessage(attachment):
    if (attachment.url != None) and \
       (attachment.filename.endswith(".jpg" or ".png" or ".gif")) and\
       (attachment.url) and\
       (attachment) :
imagesaveformat = ".png"
imagedirectory = os.getcwd() + "/images/"
directory_listing = scanfilesbyextension(imagedirectory,arguments.imagesaveformat)
#function to call the scraper class when ordered
@bot.event
async def scrapemessages(message,channel,limit):
    #get the input
    channelscraper = ChannelScraper()
    #itterate over messages in channel until limit is reached
    for msg in message.channel.history(limit):
        #ain't us
        if msg.author != client.user:
            #wasting memory
            messageContent = message.content
            messageattachments = message.attachments
            ## shove into pandas DF
            data = pandas.DataFrame(columns=['channel', 'sender', 'time', 'content','file'])
            #if attachment exists in message
            if len(messageattachments) > 0:
                #process attachments to grab images
                for attachment in messageattachments:
                    #its a link to something and that link is an image in discords CDN
                    # TODO: add second filter calling a class that checks for discord CDN
                    if (attachment.url != None) and (attachment.filename.endswith(".jpg" or ".png" or ".gif")):
                        # standard headers
                        imagedata = HTTPDownloadRequest("",discord_bot_token,attachment.url)
                        imagesaver = SaveDiscordImage(imagebytes      = imagedata,
                                                      base64orfile    = arguments.saveformat,
                                                      filename        = attachment.name,
                                                      imagesaveformat = arguments.imagesaveformat
                                                    )
                        #base64 specific stuff
                        #if arguments.saveformat == "base64":
                        
                        # if they want to save an image as a file and link to it in the database
                        if arguments.saveformat == "file":
                            # add the time and sender/messageID to name
                            # just in case of data loss
                            file_location = arguments.dbname + "_" + str(datetime.now()) + "_" + msg.author
                        # we now have either base64 image data, or binary image data
                        imageblob = imagesaver.imagedata()
                    else:
                        raise Exception

            data = data.append({'channel'      : msg.channel,
                                'sender'       : msg.author.name,
                                'time'         : msg.created_at,
                                'content'      : msg.content,
                                'file'         : imagedata},
                                ignore_index = True)
            #perform data output

            #if they want a CSV file
            if SAVETOCSV == True:
                #file_location = arguments.dbname + str(today) # Set the string to where you want the file to be saved to
                data.to_csv(file_location)
            #i they want to push it to a local sqlite3 database
            elif SAVETOCSV == False:
                messagesent = DiscordMessage(channel = data['channel'],
                                            time     = data['time'],
                                            sender   = data['sender'],
                                            content  = data['content'],
                                            # either a file path or base64 
                                            file     = data['file'])
                #push to DB
                addmsgtodb(messagesent)
                channelscraper.channelscrapetodb(data)
        #stop at message limit
        if len(data) == limit:
            break



###############################################################################
#                IMAGE SAVING CLASS
###############################################################################
randomimagename = lambda string: str(os.urandom(12)) + ".png"
class SaveDiscordImage():
    def __init__(self,  
                 imagebytes:bytes,
                 base64orfile = "file", 
                 filename = "",
                 imagesaveformat = ".png"):
        try:
            self.imagesaveformat = imagesaveformat
            self.imagein = imagebytes
            self.imageout = bytes

            if len(filename) > 0 :
                self.filename = filename
            else:
                self.filename = randomimagename
            self.image_as_base64 = base64orfile
            #they want to return a file blob
            if self.image_as_base64 == "file":
                try:
                    self.filename    = filename
                    greenprint("[+] Saving image as {}".format(self.filename))
                    self.image_storage = PIL.Image.open(self.imagein)
                    self.image_storage.save(self.filename, format = self.imagesaveformat)
                    self.image_storage.close()
                except Exception:
                    errormessage("[-] Exception when opening or writing Image File")
            #they want to return a text blob
            elif self.image_as_base64 == "base64" :
                buff = BytesIO()
                imagebytes.save(buff, format=self.imagesaveformat)
                self.image_storage = base64.b64encode(buff.getvalue())
                #self.image_storage = self.encode_image_to_base64(self.image_storage)
            else:
                raise ValueError
        except:
            errormessage("[-] Error with Class Variable self.base64_save")

    def imagedata(self):
        '''returns either base64 encoded text or a filebyte blob'''
        return self.image_storage

class APIRequest():
    '''uses Requests to return specific routes from a base API url'''
    def __init__(self, apibaseurl:str, thing:str):
        self.request_url = requote_uri("".format(apibaseurl,self.thing))
        blueprint("[+] Requesting: " + makered(self.request_url) + "\n")
        self.request_return = requests.get(self.request_url)


###############################################################################
#                CHANNEL SCRAPING CLASS
###############################################################################
class ChannelScraper():
    def __init__(self):#,channel,server):
        #self.channel = channel
        #self.server = server
        self.filterfield = ""
        self.filterstring = ""

    def channelscrapetodb(self,dataframe:pandas.DataFrame):#,thing_to_get):
        try:
            #entrypoint for data
            dataframe.columns = ['channel','time','sender','content','file']
            for row in range(0, len(dataframe.index)):
                if dataframe.iloc[row][filterfield] == filterstring:
                    warning_message("[-] PANDAS - input : {} : discarded from rows".format(dataframe.iloc[row][filterstring]))
                else :                          #sender of message
                    messagesent = DiscordMessage(channel = dataframe['channel'],
                                                time = dataframe['time'],
                                                sender = dataframe['sender'],
                                                content = dataframe['content'],
                                                # either a file path or base64 
                                                file = dataframe['file'])
                    #push to DB
                    addmsgtodb(messagesent)
        except Exception:
            errormessage("[-] WikiScraper FAILEDFAILED")


greenprint("[+] Loaded Discord commands")

class HTTPDownloadRequest():
    '''refactoring to be generic, was based on discord, DEFAULTS TO DISCORD AUTHSTRING'''
    def __init__(self,headers:str, httpauthstring:str,url:str):
        self.responsedatacontainer = []
        # just a different way of setting a default
        # good for long strings as defaults
    #Note: Custom headers are given less precedence than more specific sources 
    # of information. For instance:
    # Authorization headers set with headers= will be overridden if credentials 
    #    are specified in .netrc, which in turn will be overridden by the auth= parameter. 
    #    Requests will search for the netrc file at ~/.netrc, ~/_netrc, or at the path 
    #    specified by the NETRC environment variable.
    # Authorization headers will be removed if you get redirected off-host.
    # Proxy-Authorization headers will be overridden by proxy credentials provided in the URL.
    # Content-Length headers will be overridden when we can determine the length of the content.
        try:
            if len(httpauthstring) > 0:
                self.headerauthstring = "'Authorization':" + httpauthstring
            else:
                self.httpauthstring = "'Authorization':" + discord_bot_token
            if len(headers) >0:
                self.setHeaders(headers)
            else:
                self.headers = {
                    'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) \
                              AppleWebKit/537.36 (KHTML, like Gecko) \
                              discord/0.0.309 Chrome/83.0.4103.122 \
                              Electron/9.3.5 Safari/537.36", 
                    'Authorization' : self.httpauthstring}
            # perform the http request
            self.sendRequest(url)
            #check to see if there is data
            if self.response == None:
                raise Exception

        except Exception:
            errormessage("[-] Error in HTTPDownloadRequest()")

    def setHeaders(self, headers):
        self.headers = headers


    def sendRequest(self, url):
        '''first this is called'''
        self.response = requests.get(url, headers=self.headers)
        if TESTING == True:
            for header in self.response.headers:
                if header[0] == 'Retry-After':
                    debugmessage(header)
        #filter out errors with our own stuff first
        if self.was_there_was_an_error(response.status) == False:
            # Return the response if the connection was successful.
            if 199 < response.status_code < 300:
                return response
            #run this function again if we hit a redirect page.
            elif 299 < response.status_code < 400:
                # Grab the URL that we're redirecting to.
                redirecturl = response.header('Location')
                newdomain = redirecturl.split('/')[2].split(':')[0]
                # If the domain is a part of Discord then re-run this function.
                if newdomain in domainlist:
                    self.sendRequest(redirecturl)
                # Throw a warning message to acknowledge an untrusted redirect.
                warn('[+] Ignored unsafe redirect to {0}.'.format(redirecturl))
            # Otherwise throw a warning message to acknowledge a failed connection.
            else: 
                warn('HTTP {0} from {1}. Image Download Failed'.format(response.status_code, redirecturl))

            # if we need to retry
            # Handle HTTP 429 Too Many Requests
            if self.response.status_code == 429:
                retry_after_time = self.response.headers['retry_after']
                if retry_after_time > 0:   
                time.sleep(1 + retry_after_time)
                self.retryrequest(url)        
            # Return nothing to signify a failed request.
            return None

    def retryrequest(self,url):
        '''and this is sent if we need to retry'''
        self.sendRequest(url)

    def downloadFile(self, url, filename, buffer=0):
        #file size in bytes.
        filesize = int(self.response.header['Content-Length'])    
        #bytes downloaded
        downloaded = 0
        numchunks = int(filesize / buffer)
        lastchunk = filesize % buffer
        with open(filename, 'a+b') as filestream:
            if self.response.header['Accept-Ranges'] != 'bytes' or buffer <= 0 or numchunks < 1:
                filestream.write(self.response.content)
                filestream.close()
                return None

            for i in range(numchunks):
                i =i
                headers = self.headers
                chunk = downloaded + buffer - 1
                headers['Range'] = 'bytes={0}-{1}'.format(downloaded, chunk)
                percentage = 100 * downloaded / filesize
                if self.response is None:
                    filestream.close()
                    return None
                filestream.write(self.response.contents)
                downloaded += buffer
            
            if lastchunk > 0:
                self.headers['Range'] ='bytes={0}-'.format(downloaded)
                percentage = 100.0
                self.setHeaders(headers)
                if self.response is None:
                    filestream.close()
                    return None
                filestream.write(response.contents)
                filestream.close()
            del self.headers['Range']

    def was_there_was_an_error(self, responsecode):
        ''' Basic prechecking before more advanced filtering of output
Returns False if no error
        '''
        # server side error]
        set1 = [404,504,503,500]
        set2 = [400,405,501]
        set3 = [500]
        if responsecode in set1 :
            blueprint("[-] Server side error - No Image Available in REST response")
            yellowboldprint("Error Code {}".format(responsecode))
            return True # "[-] Server side error - No Image Available in REST response"
        if responsecode in set2:
            redprint("[-] User error in Image Request")
            yellowboldprint("Error Code {}".format(responsecode))
            return True # "[-] User error in Image Request"
        if responsecode in set3:
            #unknown error
            blueprint("[-] Unknown Server Error - No Image Available in REST response")
            yellowboldprint("Error Code {}".format(responsecode))
            return True # "[-] Unknown Server Error - No Image Available in REST response"
        # no error!
        if responsecode == 200:
            return False

###############################################################################
#                MAIN CONTROL FLOW
###############################################################################
try:
    if __name__ == '__main__':
        try:
            bot.run(discord_bot_token, bot=True)
            if os.path.exists('./messagedatabase.db') == False:
                try:
                    DiscordMsgDB.create_all()
                    DiscordMsgDB.session.commit()
                    info_message("[+] Database Tables Created")
                except Exception:
                    errormessage("[-] Database Table Creation FAILED \n")
                try:
                    test_msg = DiscordMessage(sender = 'sender',
                                    time = 'time',
                                    content = 'content',
                                    file = 'file location, relative'
                                    )
                    addmsgtodb(test_msg)
                    info_message("[+] Test Commit SUCESSFUL, Continuing!\n")
                except Exception:
                    errormessage("[-] Test Commit FAILED \n") 
                try:
                    messagescraper = ScrapeChannel(channel,history_length)
                    messagescraper.dothethingjulie()
                except Exception:
                    errormessage("[-] Database Table Creation FAILED \n")
            else:
                warning_message('[+] Database already exists, skipping creation')
        except Exception:
            errormessage("[-] Database existence Check FAILED")
    else:
        print("wat")
except:
    redprint("[-] Error starting program")

