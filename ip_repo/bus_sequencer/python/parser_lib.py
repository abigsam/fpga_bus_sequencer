import sys
import os
import re


###################################################################################################
#Check all dependiences and install if missing
###################################################################################################
import subprocess
import pkg_resources
required = {'pyparsing', 'pyleri'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
    print("[PARSER] Extension(s) " + str(missing) + " was suceesfully installed")


###################################################################################################
#Read asembler file
#Return as list of strings
###################################################################################################
def parser_read_file(src_path, print_file):
    print ("[PARSER] Trying to open file <" + src_path + "> ...")
    asmf = open(src_path, "r")
    lines = asmf.readlines()
    if print_file == "print file":
        for line in lines:
            print(line)
            print("\n")
    asmf.close()
    print ("[PARSER] File <" + src_path + "> was read successfully\n")
    return lines


###################################################################################################
#Python Left-Right Parser
###################################################################################################
