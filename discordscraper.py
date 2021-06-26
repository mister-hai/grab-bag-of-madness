# -*- coding: utf-8 -*-
################################################################################
## Message Scraper for discord archival                                       ##
################################################################################
# Copyright (c) 2020 Adam Galindo                                             ##
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
import sys,os
import pandas
import logging
import pkgutil
import inspect
import traceback
import threading
import subprocess
from json import loads
from sys import stderr
from time import sleep
from time import mktime
from pathlib import Path
from random import choice
from datetime import date
from os import _exit as exit
from json import loads, dump
from mimetypes import MimeTypes
from signal import SIGINT, signal
from importlib import import_module
from sys import stderr, version_info
from os import makedirs, getcwd, path
from http.client import HTTPSConnection
from datetime import datetime, timedelta

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
client = discord.Client()
guild = discord.Guild
SAVETOCSV = arguments.
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
yellow_bold_print = lambda text: print(Fore.YELLOW + Style.BRIGHT + ' {} '.format(text) + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
makeyellow        = lambda text: Fore.YELLOW + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else text
makered           = lambda text: Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makegreen         = lambda text: Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makeblue          = lambda text: Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
debug_message     = lambda message: logger.debug(blueprint(message)) 
info_message      = lambda message: logger.info(greenprint(message))   
warning_message   = lambda message: logger.warning(yellow_bold_print(message)) 
error_message     = lambda message: logger.error(redprint(message)) 
critical_message  = lambda message: logger.critical(yellow_bold_print(message))
scanfilesbyextension = lambda directory,extension: [f for f in os.listdir(directory) if f.endswith(extension)]

greenprint("[+] Variables Set!")

def errormessage(message):
    exc_type, exc_value, exc_tb = sys.exc_info()
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    try:
        redprint( message + ''.join(trace.format_exception_only()))
        #traceback.format_list(trace.extract_tb(trace)[-1:])[-1]
        blueprint('LINE NUMBER >>>' + str(exc_tb.tb_lineno))
    except Exception:
        yellow_bold_print("EXCEPTION IN ERROR HANDLER!!!")
        redprint(message + ''.join(trace.format_exception_only()))

################################################################################
##############                      CONFIG                     #################
################################################################################
TEST_DB            = 'sqlite://'
DATABASE           = ""
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
    message   = DiscordMsgDB.Column(DiscordMsgDB.Text)
    #filelocation
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

imagesaveformat = ".png"
imagedirectory = os.getcwd() + "/images/"
directory_listing = scanfilesbyextension(imagedirectory,arguments.imagesaveformat)
#function to call the scraper class when ordered
@bot.event
async def scrapemessages(message,limit):
    asdf = ChannelScraper(channel="",server= "")
    #itterate over messages in channel until limit is reached
    for msg in message.channel.history(limit):
        if msg.author != client.user:
            messageContent = message.content
            messageattachments = message.attachments
            ## shove into pandas DF
            data = pandas.DataFrame(columns=['sender', 'time', 'content','file'])
            #if attachments
            if len(messageattachments) > 0:
                for attachment in messageattachments:
                    if attachment.url != None:
                        pass
                    if attachment.filename.endswith(".jpg" or ".png" or ".gif"):
                        imagesaver = SaveDiscordImage(attachment,arguments.saveformat)
                        pass
                    else:
                        break
            data = data.append({'sender': msg.author.name,
                                'time'   : msg.created_at,
                                'content' : msg.content},
                                ignore_index=True)
            if SAVETOCSV == True:
                file_location = arguments.dbname + str(today) # Set the string to where you want the file to be saved to
                data.to_csv(file_location)
            elif SAVETOCSV == False:
                asdf.channelscrapetodb(data)
        #stop at limit
        if len(data) == limit:
            break



###############################################################################
#                IMAGE SAVING CLASS
###############################################################################
randomimagename = lambda string: str(os.urandom(12)) + ".png"
class SaveDiscordImage():
    def __init__(self,  imagedata:bytes, base64orfile = "file", filename = str(os.urandom(12)) + ".png"):
        try:
            self.image_as_base64 = base64orfile
            if self.image_as_base64 == "file":
                try:
                    self.filename    = filename
                    greenprint("[+] Saving image as {}".format(self.filename))
                    self.image_storage = PIL.Image.open(imagedata)
                    self.image_storage.save(self.filename, format = "png")                       
                    self.image_storage.close()
                except Exception:
                    errormessage("[-] Exception when opening or writing image file")
        # we want a base64 string
            elif self.image_as_base64 == True :
                self.image_storage = self.encode_image_to_base64(self.image_storage)
            else:
                raise ValueError
        except:
            errormessage("[-] Error with Class Variable self.base64_save")

class HTTPDownloadRequest(object):
    '''refactoring to be generic, was based on discord'''
    def __init__(self):
        # Create a blank dictionary to serve as our request header class variable.
        self.headers = {}

    def setHeaders(self, headers):
        self.headers = {
            'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) \
                          AppleWebKit/537.36 (KHTML, like Gecko) \
                          discord/0.0.309 Chrome/83.0.4103.122 \
                          Electron/9.3.5 Safari/537.36", 
                        #'Authorization': discord_bot_token
                        }
    
    def sendRequest(self, urlstr):
        urlparts = urlstr.split('/')
        urlpath = '/{0}'.format('/'.join(urlparts[3:]))
        connection = HTTPSConnection(urlparts[2], 443)
        connection.request('GET', urlpath, headers=self.headers)
        response = connection.getresponse()
        if TESTING == True:
            for header in response.getheaders():
                if header[0] == 'Retry-After':
                    debugprint(header)

        # Return the response if the connection was successful.
        if 199 < response.status < 300:
            return response
        
        #run this function again if we hit a redirect page.
        elif 299 < response.status < 400:
            # Grab the URL that we're redirecting to.
            url = response.getheader('Location')
            domain = url.split('/')[2].split(':')[0]
            # If the domain is a part of Discord then re-run this function.
            if domain in ['discordapp.com', 'discord.com']:
                self.sendRequest(url)
            
            # Throw a warning message to acknowledge an untrusted redirect.
            warn('Ignored unsafe redirect to {0}.'.format(url))
        # Otherwise throw a warning message to acknowledge a failed connection.
        else: 
            warn('HTTP {0} from {1}.'.format(response.status, url))
        
        # Handle HTTP 429 Too Many Requests
        if response.status == 429:
            retry_after = loads(response.read()).get('retry_after', None)
            if retry_after:   
                # Sleep for 1 extra second as buffer
                sleep(1 + retry_after)
                return self.sendRequest(url)
        # Return nothing to signify a failed request.
        return None

    def downloadFile(self, url, filename, buffer=0):
        # Grab the folder path from the full file name.
        filepath = path.split(filename)[0]
        # Determine if the file path exists, if not then create it.
        if not path.exists(filepath):
            makedirs(filepath)     
        # file already exists, skip everything
        if path.isfile(filename):
            return None
        response = self.sendRequest(url)
        if response is None:
            return None      
        #file size in bytes.
        filesize = int(response.getheader('Content-Length'))    
        #bytes downloaded
        downloaded = 0
        numchunks = int(filesize / buffer)
        lastchunk = filesize % buffer

        with open(filename, 'a+b') as filestream:
            if response.getheader('Accept-Ranges') != 'bytes' or buffer <= 0 or numchunks < 1:
                print('\rDownloading {0}...'.format(' ' * 7), end='')
                filestream.write(response.read())
                filestream.close()
                return None

            for i in range(numchunks):
                i =i
                request = HTTPDownloadRequest()
                headers = self.headers
                chunk = downloaded + buffer - 1
                headers.update({'Range': 'bytes={0}-{1}'.format(downloaded, chunk)})
                percentage = 100 * downloaded / filesize
                request.setHeaders(headers)
                response = request.sendRequest(url)
                if response is None:
                    filestream.close()
                    return None
                print('\rDownloading {0:3.2f}%...'.format(percentage), end='')
                filestream.write(response.read())
                downloaded += buffer
            
            if lastchunk > 0:
                request = HTTPDownloadRequest()
                headers = self.headers
                headers.update({'Range': 'bytes={0}-'.format(downloaded)})
                percentage = 100.0
                request.setHeaders(headers)
                response = request.sendRequest(url)
                if response is None:
                    filestream.close()
                    return None
                print('\rDownloading {0:3.2f}%...'.format(percentage), end='')
                filestream.write(response.read())
                filestream.close()
            del self.headers['Range']

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
    yellowprint('[WARN] {0}\n'.format(message))

###############################################################################
#                CHANNEL SCRAPING CLASS
###############################################################################
class ChannelScraper():
    def __init__(self,channel,server):
    def channelscrapetodb(self,dataframe:pandas.DataFrame):#,thing_to_get):
        messagesent = DiscordMessage(sender = dataframe['sender'],
                        time = dataframe['time'],
                        content = dataframe['content'],
                        file = dataframe['file'])
        addmsgtodb(messagesent)
    

        filterfield = ""
        filterstring = ""
        data = pandas.DataFrame(columns=['content', 'time', 'sender',"file"])
        try:
            #entrypoint for data
            self.dataframes = [] #pandas.read_html(self.thing_to_get)
            for dataframe in self.dataframes:
                if dataframe.columns[0][0] in self.sections_to_grab:
                    dataframe.columns = ['channel','time','sender','content','file']
                    for row in range(0, len(dataframe.index)):
                        if dataframe.iloc[row][filterfield] == filterstring:
                            warning_message("[-] PANDAS - input : {} : discarded from rows".format(dataframe.iloc[row][filterstring]))
                        else :
                            messagesent = DiscordMessage(sender = dataframe.iloc[row]['sender'],
                                            time = dataframe.iloc[row]['time'],
                                            content = dataframe.iloc[row]['content'],
                                            file = dataframe.iloc[row]['file'],
                                            )
                        addmsgtodb(messagesent)
        except Exception:
            errormessage("[-] WikiScraper FAILEDFAILED")


greenprint("[+] Loaded Discord commands")


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
parser.add_argument('--saveimageas',
                                 dest    = 'saveformat',
                                 action  = "store" ,
                                 default = "file", 
                                 help    = "Options: 'file', 'base64. Determines if images are saved in the DB as text or externally as files" )
parser.add_argument('--messagelimit',
                                 dest    = 'limit',
                                 action  = "store" ,
                                 default = "10000", 
                                 help    = "Number of messages to download" )
parser.add_argument('--databasename',
                                 dest    = 'dbname',
                                 action  = "store" ,
                                 default = "discordmessagehistory.db", 
                                 help    = "Name of the file to save the database as" )
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
log_file            = 'LOGGING LOGGER LOG'
logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s', filemode='w')
logger              = logging.getLogger()
script_cwd          = Path().absolute()
script_osdir        = Path(__file__).parent.absolute()
redprint          = lambda text: print(Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
blueprint         = lambda text: print(Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
greenprint        = lambda text: print(Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
yellow_bold_print = lambda text: print(Fore.YELLOW + Style.BRIGHT + ' {} '.format(text) + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
makeyellow        = lambda text: Fore.YELLOW + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else text
makered           = lambda text: Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makegreen         = lambda text: Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makeblue          = lambda text: Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
debug_message     = lambda message: logger.debug(blueprint(message)) 
info_message      = lambda message: logger.info(greenprint(message))   
warning_message   = lambda message: logger.warning(yellow_bold_print(message)) 
error_message     = lambda message: logger.error(redprint(message)) 
critical_message  = lambda message: logger.critical(yellow_bold_print(message))

def errormessage(message):
    exc_type, exc_value, exc_tb = sys.exc_info()
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    try:
        redprint( message + ''.join(trace.format_exception_only()))
        #traceback.format_list(trace.extract_tb(trace)[-1:])[-1]
        blueprint('LINE NUMBER >>>' + str(exc_tb.tb_lineno))
    except Exception:
        yellow_bold_print("EXCEPTION IN ERROR HANDLER!!!")
        redprint(message + ''.join(trace.format_exception_only()))

################################################################################
##############                      CONFIG                     #################
################################################################################
TEST_DB            = 'sqlite://'
DATABASE           = "captive portal"
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
    message   = DiscordMsgDB.Column(DiscordMsgDB.Text)
    #filelocation
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


def check_if_plants_exist_bool(plant_name):
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

        info_message('[+] Database Table {} EXISTS'.format(name))
        return True
    except Exception:
        errormessage("[-] TABLE {} does NOT EXIST!".format(name))


###############################################################################
#                DISCORD COMMANDS
###############################################################################
client = discord.Client()
from datetime import date
SAVETOCSV = False
today = date.today()

# WHEN STARTED, APPLY DIRECTLY TO FOREHEAD
@bot.event
async def on_ready():
    print("Discrod Scraper ALPHA")
    await bot.change_presence(activity=discord.Game(name="Chembot - type .help"))
    #await lookup_bot.connect()

limit = 10000
saveformat = "file"
#function to call the scraper class when ordered
@bot.event
async def scrapemessages(message,limit):
    asdf = ChannelScraper(channel="",server= "")
    #itterate over messages in channel until limit is reached
    for msg in message.channel.history(limit):
        if msg.author != client.user:
            messageContent = message.content
            messageattachments = message.attachments
            ## shove into pandas DF
            data = pandas.DataFrame(columns=['sender', 'time', 'content','file'])
            #if attachments
            if len(messageattachments) > 0:
                for attachment in messageattachments:
                    if attachment.filename.endswith(".jpg" or ".png" or ".gif"):
                        imagesaver = SaveDiscordImage(attachment,saveformat)
                        pass
                    else:
                        break
            data = data.append({'sender': msg.author.name,
                                'time'   : msg.created_at,
                                'content' : msg.content},
                                ignore_index=True)
            if SAVETOCSV == True:
                file_location = "discordmessagedata.csv" + str(today) # Set the string to where you want the file to be saved to
                data.to_csv(file_location)
            elif SAVETOCSV == False:
                asdf.channelscrapetodb(data)
        #stop at limit
        if len(data) == limit:
            break



###############################################################################
#                IMAGE SAVING CLASS
###############################################################################
class SaveDiscordImage():
    def __init__(self,  imagedata:bytes, base64orfile = "file"):
        try:
            self.image_as_base64 = base64orfile
            if image_as_base64 == "file":
                try:
                    self.filename    = str(os.urandom(12)) + ".png"
                    greenprint("[+] Saving image as {}".format(self.filename))
                    self.image_storage = PIL.Image.open(imagedata)
                    self.image_storage.save(self.filename, format = "png")                       
                    self.image_storage.close()
                except Exception as derp:
                    errormessage("[-] Exception when opening or writing image file")
        # we want a base64 string
            elif image_as_base64 == True :
                self.image_storage = self.encode_image_to_base64(self.image_storage)
            else:
                raise ValueError
        except:
            errormessage("[-] Error with Class Variable self.base64_save")


###############################################################################
#                CHANNEL SCRAPING CLASS
###############################################################################
class ChannelScraper():
    def __init__(self,channel,server):
        guild = discord.Guild

    def channelscrapetodb(self,dataframe:pandas.DataFrame):#,thing_to_get):
        messagesent = DiscordMessage(sender = dataframe['sender'],
                        time = dataframe['time'],
                        content = dataframe['content'],
                        file = dataframe['file'])
        addmsgtodb(messagesent)
    

        filterfield = ""
        filterstring = ""
        data = pandas.DataFrame(columns=['content', 'time', 'sender',"file"])
        try:
            #entrypoint for data
            self.dataframes = [] #pandas.read_html(self.thing_to_get)
            for dataframe in self.dataframes:
                if dataframe.columns[0][0] in self.sections_to_grab:
                    dataframe.columns = ['channel','time','sender','content','file']
                    for row in range(0, len(dataframe.index)):
                        if dataframe.iloc[row][filterfield] == filterstring:
                            warning_message("[-] PANDAS - input : {} : discarded from rows".format(dataframe.iloc[row][filterstring]))
                        else :
                            messagesent = DiscordMessage(sender = dataframe.iloc[row]['sender'],
                                            time = dataframe.iloc[row]['time'],
                                            content = dataframe.iloc[row]['content'],
                                            file = dataframe.iloc[row]['file'],
                                            )
                        addmsgtodb(messagesent)
        except Exception:
            errormessage("[-] WikiScraper FAILEDFAILED")


greenprint("[+] Loaded Discord commands")
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

