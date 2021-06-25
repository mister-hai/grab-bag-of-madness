# -*- coding: utf-8 -*-
#!/usr/bin/python3.9
################################################################################
##  wat-is-dis - Vintage 2021 Python 3.9     ##
################################################################################                
#  YOU HAVE TO PROVIDE THE MODULES YOU CREATE AND THEY MUST FIT THE SPEC      ##
#                                   
#     You can fuck up the backend all you want but if I can't run the module 
#     you provide, nor understand it, you have to then follow the original 
#     terms of the GPLv3 and open source all modified code so I can see 
#     what's going on. 
# 
# Licenced under GPLv3-modified                                               ##
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
IMPORTANT!
    Flask throws errors in the linter, its all good.
    "session" and things for the database aren't created until you *start a session*
        Databases are missing methods until they are instantiated
"""
###############################################################################
#                Flask Server / Flask Routes / User Interface
###############################################################################

TESTING = True
import sys,os
import logging
import pkgutil
import inspect
import traceback
import threading
import subprocess
from pathlib import Path
from importlib import import_module
from sqlalchemy import create_engine
#from sqlalchemy import inspect

import warnings
from socket import gethostname
from IPython.lib import passwd
from IPython.terminal.ipapp import launch_new_instance

import flask
from flask_wtf import FlaskForm
from sqlalchemy.pool import StaticPool
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import DataRequired
from sqlalchemy_utils import database_exists
from flask import Flask, render_template, Response,request
from wtforms import Form, TextAreaField, validators, StringField
from flask import Flask, render_template, Response, Request ,Config

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
###############################################################################
#                           TEST  Core Imports
###############################################################################
import math
import numpy
from matplotlib import pyplot as plt 
###############################################################################
#                             TEST Local Imports
###############################################################################
from resources.src.util.Utils import modulo_multiply,modulo_pow,randombytepool
from resources.src.primitives.EllipticalCurve import EllipticalCurve,Point
from resources.src.util.stats.Entropy import Entropy

def TestEC(x,a,b)->None:
    e = EllipticalCurve(x, a, b)
    # # e.plot_curve().show()
    print(e)
    p = Point(e, 2, 5, "P")
    q = 4 * p
    q.name = "2P"
    e.plot_points([p, q])
    return (modulo_multiply(26, 19, 37))
###############################################################################
#                WTFORMS
###############################################################################

#wtforms stuff
class PlotInputForm(Form):
    plotinput = TextAreaField('',[validators.DataRequired()])
#example for reference
class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])

###############################################################################
#                LOGGING
###############################################################################
basic_items  = ['__name__', 'steps','success_message', 'failure_message', 'info_message']

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


is_method          = lambda func: inspect.getmembers(func, predicate=inspect.ismethod)
scanfilesbyextension = lambda directory,extension: [f for f in os.listdir(directory) if f.endswith(extension)]

def error_printer(message):
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
    PybashyDB = SQLAlchemy(PybashyDatabase)
    PybashyDB.init_app(PybashyDatabase)
    if TESTING == True:
        PybashyDB.metadata.clear()
except Exception:
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    error_message("[-] Database Initialization FAILED \n" + ''.join(tb.format_exception_only()))

###############################################################################
#                DATABASE MODELS
###############################################################################

class JSONCommand(PybashyDB.Model):
    __tablename__       = 'CommandSets'
    #__table_args__      = {'extend_existing': True}
    id                  = PybashyDB.Column(PybashyDB.Integer,
                                          index         = True,
                                          unique        = True,
                                          autoincrement = True)
    command_name                  = PybashyDB.Column(PybashyDB.String(256), primary_key   = True)                                          
    payload                       = PybashyDB.Column(PybashyDB.Text)

    def __repr__(self):
        return '''=========================================
CommandSet Name : {}
CommandSet_JSON : {} 
'''.format(self.command_name,
            self.payload
        )
#########################################################
###                    User MODEL
#########################################################
class CaptiveClient(PybashyDB.Model):
    __tablename__       = 'Hosts'
    #__table_args__      = {'extend_existing': True}
    id                  = PybashyDB.Column(PybashyDB.Integer,
                                          primary_key   = True,
                                          index         = True,
                                          unique        = True,
                                          autoincrement = True)
    username                  = PybashyDB.Column(PybashyDB.String(256))
    password                  = PybashyDB.Column(PybashyDB.String(256))

    def __repr__(self):
        return '''=========================================
Username : {}
Password : {} 
Email    : {}
'''.format(self.username,
            self.password
        )
    def is_active(self):
        """"""
        return self.active

    def logout(self):
        ''''''
        self.active = False

    def login(self):
        ''''''
        self.active = True 

    def get_id(self):
        #"""Return the email address to satisfy Flask-Login's requirements."""
        #return self.email
        pass
    
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

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
        PybashyDB.session.add(thingie)
        PybashyDB.session.commit
        redprint("=========Database Commit=======")
        greenprint(thingie)
        redprint("=========Database Commit=======")
    except Exception as derp:
        print(derp)
        print(makered("[-] add_to_db() FAILED"))

def ReturnClientVar(client, var):
    return client.query.filter_by(var)

def ReturnClientById(idnum):
    PybashyDB.session.query(idnum)

def queryusers(username):
    PybashyDb.session.query(CaptiveClient).filter_by(username = username)

def add_cmd_to_db(cmd_to_add):
    """
    "name" is the primary key of DB, is unique
    """
    try:
        if PybashyDB.session.query(cmd_to_add).filter_by(name=cmd_to_add.name).scalar() is not None:
            info_message('[+] Duplicate Entry Avoided : ' + cmd_to_add.name)
        # and doesnt get added
        else: # and it does if it doesnt... which works out somehow ;p
            PybashyDB.session.add(cmd_to_add)
            info_message('[+] Command Added To Database : ' + cmd_to_add.name)
    except Exception:
        error_printer("[-] add_cmd_to_db() FAILED")

def DoesUsernameExist(username):
    """
    "name" is the primary key of DB, is unique
    """
    try:
        if PybashyDB.session.query(CaptiveClient).filter_by(name=username).scalar() is not None:
            info_message('[-] CaptiveUser {} Does Not Exist'.format(username))
            return None
        else:
            info_message('[-] CaptiveUser {} Exists'.format(username))
            return True
    except Exception:
        error_printer("[-] DoesUsernameExist() FAILED")

def update_db():
    try:
        PybashyDB.session.commit()
    except Exception as derp:
        print(derp.with_traceback)
        print(makered("[-] Update_db FAILED"))

def does_exists(self,Table, Row):
    try:
        if PybashyDB.session.query(Table.id).filter_by(name=Row).first() is not None:
            info_message('[+] Client {} Exists'.format(Row))
            return True
        else:
            return False        
    except Exception:
        error_printer('[-] Database VERIFICATION FAILED!')

#########################################################
###         INITIALIZE DATABASE TABLES
#########################################################
testuser = CaptiveClient(username = "johnmclaine",password= "machinegun")

try:
    PybashyDB.create_all()
    PybashyDB.session.commit()
except Exception:
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    error_message("[-] Database Table Creation FAILED \n" + ''.join(tb.format_exception_only()))

greenprint("[+] Database Loaded!")

###############################################################################
#                FLASK SERVER CLASS
###############################################################################
# still use a CSRF despite it being local development mode
# you know know!
appname = "electron-app"
app = Flask(appname)
csrf = CSRFProtect(app)
os.environ['WTF_CSRF_SECRET_KEY'] = 'a random string'
os.environ['FLASK_ENV'] = "development"

class FlaskServer():
    '''Starts a flask server for an Electron Instance to query'''
    def __init__(self,appname:str,
                #notebooktoserve:str,
                jupyteripaddr:str,
                jupyterport:str,
                flaskipaddr:str,
                flaskport:str)->None:
        self.flaskport = flaskport
        self.flaskipaddr = flaskipaddr
        #self.notebooktoserve = notebooktoserve
        self.jupyterport = jupyterport
        self.jupyteripaddr = jupyteripaddr
        self.runapp()

    def runapp(self):
        csrf.init_app(app)

def polymorphfunction(newfunctionname:str):
    '''dynamically creates new functions with the given name and parameters
    used in the creation of new routes for display of documentation'''
    evalstring = '''def {functionname}({kwargsdict}):

    '''.format(functionname = newfunctionname)
    eval(evalstring)

#three possible ways to make a directory of routes?


#list documents first
# turn each result into link
@app.route("/docs/docslist/")
def documentationlisting():
    docsfolder = "/docs/"
    # scans from root of electron folder
    documentation_directory = os.getcwd() + docsfolder
    directory_listing = scanfilesbyextension(documentation_directory,".html")
    #with open('/docs/' + str(docpage) + '.html', 'r') as f:
    #    content = f.read()
    return flask.render_template('docslist.html', directorylist = directory_listing)

#route to the specific document
@app.route('/docs/show/<string:document>', methods=['GET'])
def showdocumentationfile(document):
    with open('/docs/' + str(document) + '.html', 'r') as f:
        content = f.read()
    return content

@app.route("/ellipticalcurveplot")
def plot(app):
    form = PlotInputForm(request.form)
    #this is how you retrieve form field data
    #without WTForms
    x1 = request.form['x1']
    a = request.form['a']
    b = request.form['b']
    TestEC(x1,a,b)
    app.render_template('ellipticalcurveplotting.html', form=form)

@app.route('/notebook')
def notebook(notebooktoserve,jupyteripadd,jupyterport,flaskport,flaskipaddr):
    #'''Starts a jupyter server'''
    #if request.method == 'POST' :#and form.validate():
    notebook = JupyterServer(jupyteripaddr = jupyteripadd,
                        jupyterport = jupyterport,
                        flaskport = flaskport,
                        #notebookpath = notebooktoserve,
                        flaskipaddr = flaskipaddr)
    # simply serve the iframe if started in a seperate script
    if (__name__ == "main"):                                     
        notebook.runserver(notebooktoserve)
    notebookrender = notebook.iframehtml
    return notebookrender

def output(filename):
    '''This is the function that outputs data to the browser screen
    feed it a filename'''
    if request.method == 'POST':
        render_template(filename+ '.html')

def add_endpoint(endpoint=None, endpoint_name=None, handler=None):
    app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))


class EndpointAction(object):

    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        self.action()
        return self.response

###############################################################################
#           Flask - Jupyter Server / Jupyter Notebook Configuration
###############################################################################

class JupyterServer():
    '''Handler for Jupyter Notebooks to render them in the browser dynamically

JUPYTER_CONFIG_DIR   config file location
JUPYTER_CONFIG_PATH  config file locations
JUPYTER_PATH         datafile directory locations
JUPYTER_DATA_DIR     data file location
JUPYTER_RUNTIME_DIR  runtime file location
'''
    def __init__(self,
                 jupyteripaddr:str,
                 jupyterport:str,
                 flaskport:str, 
                 flaskipaddr:str,)->None:
                # notebookpath:str)->None:
        self.jupyterport = jupyterport
        self.jupyteripaddr = jupyteripaddr
        self.flaskport = flaskport
        self.flaskipaddr = flaskipaddr
        #self.notebookpath = notebookpath
        #self.jupyteripaddr = gethostname()
        self.notebookpath = "notebook.html"
        self.jupyterurl =  "http://{}:{}/{}".format(self.jupyteripaddr,
                                                    self.jupyterport,
                                                    self.notebookpath)
        self.iframehtml  = '''
<iframe width="1000" height="1000"  src="http://{jupyteripaddr}:{jupyterport}/{notebookpath}"/>
'''.format(jupyteripaddr = self.jupyteripaddr,
           jupyterport   = self.jupyterport,
           notebookpath  = self.notebookpath)
        # set config to be in pwd
        self.notebookconfig = '''
c.NotebookApp.allow_origin = '*' #Basic permission
c.NotebookApp.disable_check_xsrf = True #Otherwise Jupyter restricts you modifying the Iframed Notebook
c.NotebookApp.ip = '{jupyteripaddr}' #Appears in the top browser bar when you launch jupyter
c.NotebookApp.port = {jupyterport} #Your choice of port
c.NotebookApp.token = '' #In my case I didn't want to deal with security
c.NotebookApp.trust_xheaders = True #May or may not make a difference to you
c.NotebookApp.allow_root = True

c.NotebookApp.tornado_settings = {
'headers': {
'Content-Security-Policy': "frame-ancestors 'http://127.0.0.1:{flaskport}/' 'self' "
}
} #assuming your Flask localhost is 127.0.0.1:5000

'''.format(jupyteripaddr = self.jupyteripaddr,
           jupyterport   = self.jupyterport,
           flaskport     = self.flaskport)

## still in __init__  ...
#        self.writeconfig()
    def showconfig(self,printoreturn = "print"):
        '''"print" to print to STDOUT
"return" to return the value
'''
        if printoreturn == "print":
            print(self.notebookconfig)
        elif printoreturn == "return":
            return self.notebookconfig

    def writeconfig(self,configfile):
        #write to config
        config = open(configfile,'w')
        config.write(self.notebookconfig)
        config.close()
    
    def runserver(self):
        warnings.filterwarnings("ignore", module = "zmq.*")
        sys.argv.append("notebook")
        sys.argv.append("--IPKernelApp.pylab='inline'")
        sys.argv.append("--NotebookApp.ip=" + self.jupyteripaddr)
        sys.argv.append("--NotebookApp.open_browser=False")
        #sys.argv.append("--NotebookApp.password=" + passwd())
        launch_new_instance()



################################################################################
##############           SYSTEM AND ENVIRONMENT                #################
################################################################################
class GenPerpThreader():
    '''
    General Purpose threading implementation that accepts a generic programmatic entity
    '''
    def __init__(self,function_to_thread):
        self.thread_function = function_to_thread
        self.function_name   = getattr(self.thread_function.__name__)
        self.threader(self.thread_function,self.function_name)

    def threader(self, thread_function, name):
        info_message("Thread {}: starting".format(self.function_name))
        thread = threading.Thread(None,self.thread_function, self.function_name)
        thread.start()
        info_message("Thread {}: finishing".format(name))

###############################################################################
#          Linux command scheduler/pool
###############################################################################

class Command():
    def __init__(self, cmd_name , command_struct):
        '''init stuff
        ONLY ONE COMMAND, WILL THROW ERROR IF NOT TO SPEC
        '''
        self.name                = cmd_name
        try:
            self.cmd_line        = command_struct.get("command")
            self.info_message    = command_struct.get("info_message")
            self.success_message = command_struct.get("success_message")
            self.failure_message = command_struct.get("failure_message")
        except Exception:
            error_printer("[-] JSON Input Failed to MATCH SPECIFICATION!\n\n    ")

    def __repr__(self):
        greenprint("Command:")
        print(self.name)
        greenprint("Command String:")
        print(self.cmd_line)

class CommandSet():
    def __init__(self):
        self.name         = ''
        self.__name__     = self.name
        self.__qualname__ = self.__name__
    
    def AddCommandDict(self, cmd_name, new_command_dict):
        '''Creates a new Command() from a step and assigns to self'''
        try:
            new_command = Command(cmd_name, new_command_dict)
            setattr(self , new_command.name, new_command)
        except Exception:
            error_printer('[-] Interpreter Message: CommandSet() Could not Init')  

class FunctionSet(CommandSet):
    def __init__(self):
        self.name         = ''
        self.__name__     = self.name
        self.__qualname__ = self.__name__

class ExecutionPool():
    def __init__(self):
        self.set_actions = {}

    def addtopool(self):
        ''' Yeahhhh... its about time to write the CRUDREST functions'''
        pass

    def get_actions_from_set(self, command_set : CommandSet):
        for attribute in command_set.items():
            if attribute.startswith("__") != True:
                self.set_actions.update({attribute : getattr(command_set,attribute)})

    def run_set(self, command_set : CommandSet):
        for field_name, field_object in command_set.items:
            if field_name in basic_items:
                command_line    = getattr(field_object,'cmd_line')
                success_message = getattr(field_object,'success_message')
                failure_message = getattr(field_object,'failure_message')
                info_message    = getattr(field_object,'info_message')
                yellow_bold_print(info_message)
                try:
                    self.exec_command(command_line)
                    print(success_message)
                except Exception:
                    error_printer(failure_message)

    def run_function(self,command_set, function_to_run ):
        '''
        '''
        try:
            #requesting a specific Command()
            command_object  = command_set.command_list.get(function_to_run)
            command_line    = getattr(command_object,'cmd_line')
            success_message = getattr(command_object,'success_message')
            failure_message = getattr(command_object,'failure_message')
            info_message    = getattr(command_object,'info_message')
            yellow_bold_print(info_message)
            try:
                self.exec_command(command_line)
                print(success_message)
            except Exception:
                error_printer(failure_message)
            # running the whole CommandSet()
        except Exception:
            error_printer(failure_message)

    def exec_command(self, command, blocking = True, shell_env = True):
        '''TODO: add formatting'''
        try:
            if blocking == True:
                step = subprocess.Popen(command,shell=shell_env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                output, error = step.communicate()
                for output_line in output.decode().split('\n'):
                    info_message(output_line)
                for error_lines in error.decode().split('\n'):
                    critical_message(error_lines)
                return step
            elif blocking == False:
                # TODO: not implemented yet                
                pass
        except Exception as derp:
            yellow_bold_print("[-] Interpreter Message: exec_command() failed!")
            return derp

class PybashyRunFunction():
    ''' 
    This is the class you should use to run one off functions, established inline,
    deep in a complex structure that you do not wish to pick apart
    The function should contain only a "steps" variable and format()
    ''' 
    def __init__(self, FunctionToRun):
        NewFunctionSet       = FunctionSet()
        #get name of function
        NewFunctionSet.name  = getattr(FunctionToRun, "__name__")
        steps              = getattr(FunctionToRun, "steps")
        #itterate over the steps to get each individual action/command
        # added to the FunctionSet as a Command() via the 
        for step in steps:
            for command_name in step.keys():
                cmd_dict = step.get(command_name)
                #add the step to the functionset()
                NewFunctionSet.AddCommandDict(command_name,cmd_dict)

class PybashyRunSingleJSON():
    ''' 
    This is the class you should use to run one off commands, established inline,
    deep in a complex structure that you do not wish to pick apart
    The input should contain only a single json Command() item and format()
    {   
        "IPTablesAcceptNAT": {
            "command"         : "iptables -t nat -I PREROUTING 1 -s {} -j ACCEPT".format(self.remote_IP),
            "info_message"    : "[+] Accept All Incomming On NAT Subnet",
            "success_message" : "[+] Command Sucessful", 
            "failure_message" : "[-] Command Failed! Check the logfile!"           
        }
    }
    ''' 
    def __init__(self, JSONCommandToRun:dict):
        # grab the name
        NewCommandName = JSONCommandToRun.keys[0]
        # craft the command
        NewCommand = Command(NewCommandName,JSONCommandToRun)
        # init an execution pool to run commands
        execpool   = ExecutionPool()
        # run the command in a new thread
        GenPerpThreader(execpool.exec_command(NewCommand))
        # huh... I hope that really is all it takes... that seemed simple!
