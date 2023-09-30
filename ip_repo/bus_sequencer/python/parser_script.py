###################################################################################################
# File: parser_script.py
# Command:
# python ./ip_repo/bus_sequencer/python/parser_script.py ./sequence_prog.txt null
###################################################################################################

import sys
import os
from parser_lib import *


#Check number of passed parameters
if (len(sys.argv) < 3):
    print("Python script requered at least 2 parameters") #Parameter [0] is script path
    exit()

#Readout configurations
# script_path = os.path.abspath(sys.argv[0])
asm_src = os.path.abspath(sys.argv[1])
memout_path = os.path.abspath(sys.argv[2])

#Read input file
src_str = parser_read_file(asm_src, "no print file")


#Check tokenizer
# token_list = parser_get_tokens(src_str)
# token_analysys(token_list)

#Run parsing
parsering_program(src_str)


# test_arpeggio(True)
# tree = test_arpeggio(src_str)
