#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# This file will mirror a website in a directory .
# You can use it to either backup important documentation
# or to impersonate for phishing
#
try:
    import os
    import sys
    from pathtools import path
    import argparse
    import subprocess
    import traceback
except Exception as derp:
    print('failure at imports')
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



def error_printer(message):
    exc_type, exc_value, exc_tb = sys.exc_info()
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    try:
        redprint( message + ''.join(trace.format_exception_only()))
        traceback.format_list(trace.extract_tb(trace)[-1:])[-1]
        blueprint('LINE NUMBER >>>' + str(exc_tb.tb_lineno))
    except Exception:
        yellow_bold_print("EXCEPTION IN ERROR HANDLER!!!")
        redprint(message + ''.join(trace.format_exception_only()))

test_url = 'https://book.rada.re/index.html'
parser = argparse.ArgumentParser(description='page mirroring tool utilizing wget via python scripting')
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
                                 help    = "Storage directory to place the downloaded files in, defaults to script working directory" )

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



if __name__ == "__main__":
    arguments  = parser.parse_args()
    wget_thing = GetPage(arguments.directory_prefix,
                         arguments.target,
                         arguments.useragent,
                         arguments.wget_options)
