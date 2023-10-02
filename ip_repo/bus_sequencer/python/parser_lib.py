from __future__ import unicode_literals

import sys
import os
import re


###################################################################################################
#Check all dependiences and install if missing
###################################################################################################
import subprocess
import pkg_resources
# required = {'pyparsing', 'pyleri'}
required = {'pyleri'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
    print("[PARSER] Extension(s) " + str(missing) + " was suceesfully installed")


###################################################################################################
#Read asembler file
#Return file as a string
###################################################################################################
def parser_read_file(src_path, print_file):
    print ("[PARSER] Trying to open file <" + src_path + "> ...")
    asmf = open(src_path, "r")
    src_str = asmf.read()
    # lines_raw = asmf.readlines()
    # lines = []
    # #Remove trailing/leading spaces and empty lines
    # for line in lines_raw:
    #     if len(line.strip()) != 0:
    #         lines.append(line.strip(" "))
    # #Print lines if need
    # for line in lines:
    if print_file == "print file":
        print(src_str)
    asmf.close()
    print ("[PARSER] File <" + src_path + "> was read successfully")
    # return lines
    return src_str


###################################################################################################
# Token-based aproach
###################################################################################################
# from typing import NamedTuple
# import re

# class Token(NamedTuple):
#     type: str
#     value: str
#     line: int
#     column: int

# def parser_get_tokens(file_lines):
#     keywords = {'STOP', 'WAIT', 'CMP', 'CMP_LAST', 'CMP_JMP', 'PAUSE', 'UNCOND_JMP', 'NOP',
#                 'I2C_START_WRITE', 'I2C_START_READ', 'I2C_STOP', 'I2C_SEND', 'I2C_RECEIVE_ACK', 'I2C_RECEIVE_NACK',
#                 'SPI_TRANSFER', 'SPI_HD_WRITE', 'SPI_HD_READ', 'equ', 'EQU'}
#     token_specification = [
#         ('COMMENT',     r'[;]{1}'),                 #Comment
#         ('BUS_TYPE',    r'[.]{1}'),                 #Bus name quilifier ('.')
#         ('HEX_BYTE',    r'0x[0-9a-fA-F]{1,2}'),     #HEX number
#         ('ASSIGN',      r'equ|EQU'),                #Assignment operator
#         ('ID',          r'[A-Za-z_][A-Za-z0-9_]+'), #Identifiers
#         ('LABEL',       r'[:]{1}'),                 #Jump label
#         ('NEWLINE',     r'\n'),                     #Line endings
#         ('SKIP',        r'[ \t]+'),                 #Skip over spaces and tabs
#         ('MISMATCH',    r'.'),                      #Any other character
#     ]
#     tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
#     line_num = 1
#     line_start = 0
#     comment_detected = 0
#     #Check if get string or list of strings
#     code_str = ""
#     if not isinstance(file_lines, str):
#         code_str = ''.join(file_lines)
#     else:
#         code_str = file_lines
#     for mo in re.finditer(tok_regex, code_str):
#         kind = mo.lastgroup
#         value = mo.group()
#         column = mo.start() - line_start

#         #If previous token was comment, skip all untill new line
#         if comment_detected == 1:
#             if kind == 'NEWLINE':
#                 comment_detected = 0
#                 line_start = mo.end()
#                 line_num += 1
#             continue
        
#         #Parse tokens
#         if kind == 'COMMENT':
#             comment_detected = 1
#         elif kind == 'HEX_BYTE':
#             value = int(value, 16)
#         elif kind == 'ID':
#             if value in keywords:
#                 kind = 'CMD'
#             else:
#                 kind = 'ID'
#         elif kind == 'NEWLINE':
#             kind = value
#             line_start = mo.end()
#             line_num += 1
#             continue
#         elif kind == 'SKIP':
#             continue
#         elif kind == 'MISMATCH':
#             raise RuntimeError(f'{value!r} unexpected on line {line_num}')
#         #Save token if it not comment
#         if comment_detected == 0:
#             yield Token(kind, value, line_num, column)


###################################################################################################
# Local procedure
# Return node string by name
###################################################################################################
def local_get_node_string(tree, node_name):
    start = tree.children[0] \
        if tree.children else tree
    for node in start.children:
        if node.element.name == node_name:
            return node.string
    return 0

def local_get_node(tree, element_name, element_count = 0):
    cnt = 0
    for node in tree.children:
        if node.element.__class__.__name__ == element_name:
            if element_count == cnt:
                return node
        cnt += 1
    return 0


def local_dbg_show_tree(res):
    import json
    # Returns properties of a node object as a dictionary:
    def node_props(node, children):
        return {
            'start': node.start,
            'end': node.end,
            'name': node.element.name if hasattr(node.element, 'name') else None,
            'element': node.element.__class__.__name__,
            'string': node.string,
            'children': children}


    # Recursive method to get the children of a node object:
    def get_children(children):
        return [node_props(c, get_children(c.children)) for c in children]


    # View the parse tree:
    def view_parse_tree(res):
        start = res.tree.children[0] \
            if res.tree.children else res.tree
        return node_props(start, get_children(start.children))
    # def view_parse_tree(res):
    #     start = res.children[0] \
    #         if res.children else res
    #     return node_props(start, get_children(start.children))
    
    print(json.dumps(view_parse_tree(res), indent=2))

###################################################################################################


###################################################################################################
# Local
# Generate grammars for each elements
# Return dictionary of grammars
###################################################################################################
def local_parse_get_grammars():
    grammars_dict = {}
    # For more details see: https://github.com/cesbit/pyleri
    from pyleri import (
        Grammar,
        Keyword,
        Sequence,
        Regex,
        Choice,
        Optional)

    #Create common grammar elements ***************************************************************
    r_comment  = Regex('\s*[;].*')
    r_id       = Regex('[a-zA-z][a-zA-Z0-9_]+')
    r_hex_byte = Regex('0x[0-9a-fA-F]{1,2}')

    #Create class for EQU/equ *********************************************************************
    class ConstGrammar(Grammar):
        k_equ = Keyword('equ', ign_case=True)
        START = Sequence(r_id, k_equ, r_hex_byte, Optional(r_comment))
    grammars_dict["constants"] = ConstGrammar()

    #Create class for bus type ********************************************************************
    class BusTypeGrammar(Grammar):
        r_bus_id_start = Regex('[.]{1}')
        START = Sequence(r_bus_id_start, r_id, Optional(r_comment))
    grammars_dict["bus_type"] = BusTypeGrammar()

    #Create class for commands without arguments **************************************************
    ign_case_no_arg = False
    class CmdNoArgumentsGrammar(Grammar):
        k_stop          = Keyword('STOP',             ign_case=ign_case_no_arg)
        k_pause         = Keyword('PAUSE',            ign_case=ign_case_no_arg)
        k_nop           = Keyword('NOP',              ign_case=ign_case_no_arg)
        k_i2c_stop      = Keyword('I2C_STOP',         ign_case=ign_case_no_arg)
        k_i2c_rack      = Keyword('I2C_RECEIVE_ACK',  ign_case=ign_case_no_arg)
        k_i2c_rnack     = Keyword('I2C_RECEIVE_NACK', ign_case=ign_case_no_arg)
        k_spi_hd_read   = Keyword('SPI_HD_READ',      ign_case=ign_case_no_arg)
        START = Sequence(Choice(k_stop, k_pause, k_nop, k_i2c_stop, k_i2c_rack,
                                k_i2c_rnack, k_spi_hd_read, most_greedy=False),
                        Optional(r_comment))
    grammars_dict["commands_no_arg"] = CmdNoArgumentsGrammar()

    #Create class for commands with arguments *****************************************************
    ign_case_arg = False
    class CmdWithArgumentsGrammar(Grammar):
        k_wait          = Keyword('WAIT',            ign_case=ign_case_arg)
        k_cmp           = Keyword('CMP',             ign_case=ign_case_arg)
        k_cmp_last      = Keyword('CMP_LAST',        ign_case=ign_case_arg)
        k_cmp_jump      = Keyword('CMP_JMP',         ign_case=ign_case_arg)
        k_uncond_jump   = Keyword('UNCOND_JMP',      ign_case=ign_case_arg)
        k_i2c_swrite    = Keyword('I2C_START_WRITE', ign_case=ign_case_arg)
        k_i2c_sread     = Keyword('I2C_START_READ',  ign_case=ign_case_arg)
        k_i2c_send      = Keyword('I2C_SEND',        ign_case=ign_case_arg)
        k_spi_transfer  = Keyword('SPI_TRANSFER',    ign_case=ign_case_arg)
        k_spi_hd_write  = Keyword('SPI_HD_WRITE',    ign_case=ign_case_arg)
        START = Sequence(Choice(k_wait, k_cmp, k_cmp_last, k_cmp_jump, k_uncond_jump,
                                k_i2c_swrite, k_i2c_sread, k_i2c_send, k_spi_transfer,
                                k_spi_hd_write, most_greedy=False),
                         Choice(r_id, r_hex_byte, most_greedy=False),
                         Optional(r_comment))
    grammars_dict["commands_with_arg"] = CmdWithArgumentsGrammar()

    #Create class for labels **********************************************************************
    class LabelsGrammar(Grammar):
        r_label_name  = Regex('[_][a-zA-Z][a-zA-Z0-9_]+')
        r_label_end   = Regex('[:]{1}')
        START = Sequence(r_label_name, r_label_end, Optional(r_comment))
    grammars_dict["labels"] = LabelsGrammar()

    #Create class for comments and empty lines ****************************************************
    class CommentsEmptyGrammar(Grammar):
        r_empty   = Regex('\s*')
        START = Sequence(Optional(r_empty), Optional(r_comment))
    grammars_dict["comments"] = CommentsEmptyGrammar()

    return grammars_dict

def local_parse_check_valid_grammar(src_str, grammars_dict, dbg=False):
    line_cnt = 0
    for line in src_str.split("\n"):
        is_visited = 0
        for gname, grammar in grammars_dict.items():
            if grammar.parse(line).is_valid:
                if dbg:
                    print("[PARSER DBG] >>> line [" + str(line_cnt) + "] is parsed by <" + gname + ">")
                is_visited += 1
        if is_visited == 0:
            print("[PARSER] Error: line [" + str(line_cnt) + "] has no valid parser")
            print("[PARSER] >>>>>> " + line)
            return "UNVALID"
        line_cnt += 1
    return "VALID"
###################################################################################################



###################################################################################################
# Local procedure
# Parse input string for constants
# Return: dictionary [constant name] = value
###################################################################################################
def local_parse_const(src_str, grammar):
    const_dict = {}
    #Parse program text
    for line in src_str.split("\n"):
        result = grammar.parse(line)
        if result.is_valid:
            seq = local_get_node(result.tree, "Sequence")
            lname = local_get_node(seq, "Regex", 0).string
            lvalue = local_get_node(seq, "Regex", 2).string
            const_dict[lname] = lvalue
    
    #Output information about constants
    print("[PARSER] Was found " + str(len(const_dict)) + " constant(s)")
    # for lname, lvalue in const_dict.items():
    #     print("[PARSER] >>> " + lname + " = " + str(lvalue))

    return const_dict
###################################################################################################


###################################################################################################
# Local procedure
# Parse string for Bus type
###################################################################################################
def local_parse_bus_type(src_str, grammar):
    bus_name = []
    #Parse program text
    for line in src_str.split("\n"):
        result = grammar.parse(line)
        if result.is_valid:
            seq = local_get_node(result.tree, "Sequence")
            lname = local_get_node(seq, "Regex", 1).string
            bus_name.append(lname)
    #Output information
    print("[PARSER] Was found " + str(len(bus_name)) + " bus(es)")
    # for lname in bus_name:
    #     print("[PARSER] >>> " + lname)
    return bus_name


###################################################################################################
# Local procedure
# Parse string for commands
###################################################################################################
def local_parse_commands(src_str, grammars_dict):
    commands = []
    #Parse program text
    lcnt = 0
    for line in src_str.split("\n"):
        #Parse commands without arguments
        result = grammars_dict["commands_no_arg"].parse(line)
        if result.is_valid:
            seq_node = local_get_node(result.tree, "Sequence")
            lname = local_get_node(seq_node, "Choice").string
            # print("DBG " + lname + " >>> " + str(lcnt))
            commands.append([lname, lcnt])
        else:
            #Parse commands with arguments
            result = grammars_dict["commands_with_arg"].parse(line)
            if result.is_valid:
                seq_node = local_get_node(result.tree, "Sequence")
                lname = local_get_node(seq_node, "Choice", 0).string
                lvalue = local_get_node(seq_node, "Choice", 1).string
                # print("DBG " + lname + " : " + lvalue + " >>> " + str(lcnt))
                commands.append([lname, lvalue, lcnt])
        lcnt += 1
    #
    print("[PARSER] Was found " + str(len(commands)) + " command(s)")
    return commands


###################################################################################################
# Local
# Parse for labels
###################################################################################################
def local_parse_labels(src_str, grammar):
    labels = []
    #Parse program text
    lcnt = 0
    for line in src_str.split("\n"):
        #Parse commands without arguments
        result = grammar.parse(line)
        if result.is_valid:
            seq = local_get_node(result.tree, "Sequence", 0)
            lname = local_get_node(seq, "Regex", 0).string
            # print(" DBG --> " + lname)
            labels.append([lname, lcnt])
        lcnt += 1
    print("[PARSER] Was found " + str(len(labels)) + " label(s)")
    return labels


###################################################################################################
#Python Left-Right Parser
###################################################################################################
def parser_parse(src_str):
    print("[PARSER] Run parsing...")

    #Get grammars
    grammars_dict = local_parse_get_grammars()
    
    #Check if there invalid lines
    if "UNVALID" == local_parse_check_valid_grammar(src_str, grammars_dict):
        return 0

    #Parse text
    const_dict = local_parse_const(src_str, grammars_dict["constants"])
    bus_type   = local_parse_bus_type(src_str, grammars_dict["bus_type"])
    cmd_list   = local_parse_commands(src_str, grammars_dict)
    label_list = local_parse_labels(src_str, grammars_dict["labels"])

    print("[PARSER] Parsing successfully ended")

    return {"constants"  : const_dict,
            "bus_define" : bus_type,
            "commands"   : cmd_list,
            "labels"     : label_list
            }
###################################################################################################


###################################################################################################
# Local
# Builder checkers
###################################################################################################
def local_builder_check_bus(bus_identifiers):
    bus_type = ""
    for item in bus_identifiers:
        # print ("DBG " + item)
        if bus_type == "":
            if item == "start_i2c" or item == "start_spi":
                bus_type = "i2c" if item == "start_i2c" else \
                           "spi" if item == "start_spi" else \
                           "unknown"
        else:
            if item != "stop":
                print("[BUILDER] Error: after bud identifier should be \".stop\", but received " + item)
    if bus_type == "" or bus_type == "unknown":
        print("[BUILDER] Error: no valid bus identifier")
    else:
        print("[BUILDER] Found \"" + bus_type + "\" bus identifier")
    return bus_type


def local_builder_check_commands(cmd_list, bus_type):
    error_st = 0
    #Check for valid bus command
    spicmd_list = ("SPI_HD_READ", "SPI_TRANSFER", "SPI_HD_WRITE")
    i2c_cmd_list = ("I2C_STOP", "I2C_RECEIVE_ACK", "I2C_RECEIVE_NACK", "I2C_START_WRITE", "I2C_START_READ", "I2C_SEND")
    for cmd_config in cmd_list:
        if bus_type == "i2c":
            for spi_cmd in spicmd_list:
                if cmd_config[0] == spi_cmd:
                    error_st += 1
                    print("[BUILDER] Error: command <" + cmd_config[0] + "> cannot be used if bus \"i2c\" was choosen")
        elif bus_type == "spi":
            for i2c_cmd in i2c_cmd_list:
                if cmd_config[0] == i2c_cmd:
                    error_st += 1
                    print("[BUILDER] Error: command <" + cmd_config[0] + "> cannot be used if bus \"spi\" was choose")
    #Check if last command is "STOP"
    if cmd_list[-1][0] != "STOP":
        error_st += 1
        print("[BUILDER] Error: expecting last command \"STOP\" but received \"" + cmd_list[-1][0] + "\"")
    return error_st

def local_builder_replace_const(cmd_arg_list, const_dict, dbg=False):
    error_st = 0
    def is_cmd_has_arg(cmd):
        cmd_with_arg = ("WAIT", "CMP", "CMP_LAST", "I2C_START_WRITE", "I2C_START_READ", "I2C_SEND", "SPI_TRANSFER", "SPI_HD_WRITE")
        for cmd_arg in cmd_with_arg:
            if cmd == cmd_arg:
                return True
        return False
    
    def is_arg_const_name(arg_str):
        if arg_str[0:2] == "0x":
            return False
        return True

    if dbg:
        print("DBG >>> Before constants replacements")

    #Replace constants names for values
    cnt = 0
    for cmd_arg in cmd_arg_list:
        if dbg:
            print("DBG >>>     ", end="")
            print(cmd_arg)
        if is_cmd_has_arg(cmd_arg[0]):
            if is_arg_const_name(cmd_arg[1]):
                if cmd_arg[1] in const_dict:
                    upd_cmd_arg = cmd_arg
                    upd_cmd_arg[1] = const_dict[cmd_arg[1]]
                    cmd_arg_list[cnt] = upd_cmd_arg
                else:
                    print("[BUILDER] Error: command \"" + cmd_arg[0] + "\" expects undefined constant name \"" + cmd_arg[1] + "\"")
                    error_st +=1
        cnt += 1

    #Convert to int
    cnt = 0
    for cmd_arg in cmd_arg_list:
        if is_cmd_has_arg(cmd_arg[0]):
            upd_cmd_arg = cmd_arg
            upd_cmd_arg[1] = int(cmd_arg[1], 16)
            cmd_arg_list[cnt] = upd_cmd_arg
        cnt += 1

    if dbg:
        print("DBG >>> After constants replacements")
        for cmd_arg in cmd_arg_list:
            print("DBG >>>     ", end="")
            print(cmd_arg)

    return error_st


def local_builder_replace_labels(cmd_list, label_list, dbg=0):
    error_st = 0

    def is_cmd_jmp(cmd):
        jmp_cmds = ("CMP_JMP", "UNCOND_JMP")
        for item in jmp_cmds:
            if item == cmd:
                return True
        return False
    
    def is_label_in_list(label_list, label_name):
        for l_config in label_list:
            if l_config[0] == label_name:
                return True
        return False

    def get_label_lnum(label_list, label_name):
        for l in label_list:
            if l[0] == label_name:
                return l[1]
        return -1
    
    def get_next_cmd(cmd_list, label_num):
        cnt = 0
        for cmd in cmd_list:
            if cmd[-1] > label_num:
                return cnt
            cnt += 1
        return -1

    if dbg:
        print("DBG >>> Labels")
        for lb in label_list:
            print("DBG >>>     ", end="")
            print(lb)

    if dbg:
        print("DBG >>> Before labels replacements")

    cnt = 0
    for cmd in cmd_list:
        if dbg:
            print("DBG >>>     ", end="")
            print(cmd)
        if is_cmd_jmp(cmd[0]):
            # print("cmd[1] = " + cmd[1])
            if is_label_in_list(label_list, cmd[1]):
                line_num = get_label_lnum(label_list, cmd[1])
                jmp_to_cmd_num = get_next_cmd(cmd_list, line_num)
                cmd_upd = cmd
                cmd_upd[1] = jmp_to_cmd_num - cnt
                cmd_list[cnt] = cmd_upd
            else:
                print("[BUILDER] Error: command \"" + cmd[0] + "\" expects undefined label \"" + cmd[1] + "\"")
                error_st +=1
        cnt += 1
    
    if dbg:
        print("DBG >>> After labels replacements")
        for item in cmd_list:
            print("DBG >>>     ", end="")
            print(item)

    return error_st

###################################################################################################


###################################################################################################
# Local
# Convert to HEX each command
###################################################################################################
def local_build_convert_to_hex(commands_list):
    hex_list = []

    def conv_cmd(arg, instr, instr_type):
        tmp = (arg << 5) & 0x1FE0
        tmp |= (instr << 1) & 0x1e
        if instr_type == "TRANSFER":
            tmp |= 0x01
        return tmp

    for cmd_arg in commands_list:
        match cmd_arg[0]:
            #Commands without parameters
            case "STOP":
                hex_list.append(conv_cmd(0, 0b0000, "INSTR"))       # 00000000_0_000_0
            case "PAUSE":
                hex_list.append(conv_cmd(0, 0b0100, "INSTR"))       # 00000000_0_100_0
            case "NOP":
                hex_list.append(conv_cmd(0, 0b0110, "INSTR"))       # 00000000_0_110_0
            #I2C
            case "I2C_STOP":
                hex_list.append(conv_cmd(0, 0b0010, "TRANSFER")) # 00000000_0010_1
            case "I2C_RECEIVE_ACK":
                hex_list.append(conv_cmd(0, 0b1000, "TRANSFER")) # 00000000_1000_1
            case "I2C_RECEIVE_NACK":
                hex_list.append(conv_cmd(0, 0b0000, "TRANSFER")) # 00000000_0000_1
            #SPI
            case "SPI_HD_READ":
                hex_list.append(conv_cmd(0, 0b0000, "TRANSFER")) # 00000000_0000_1
            #
            #Commands with parameters
            case "WAIT":
                hex_list.append(conv_cmd(cmd_arg[1], 0b0001, "INSTR")) #  xxxxxxxx_0001_0
            case "CMP":
                hex_list.append(conv_cmd(cmd_arg[1], 0b0010, "INSTR")) #  xxxxxxxx_0010_0
            case "CMP_LAST":
                hex_list.append(conv_cmd(cmd_arg[1], 0b1010, "INSTR")) #  xxxxxxxx_1010_0
            case "CMP_JMP":
                if (cmd_arg[1] > 0):
                    hex_list.append(conv_cmd(cmd_arg[1],      0b0011, "INSTR")) #  xxxxxxxx_0011_0
                else:
                    hex_list.append(conv_cmd(abs(cmd_arg[1]), 0b1011, "INSTR")) #  xxxxxxxx_0011_0
            case "UNCOND_JMP":
                if (cmd_arg[1] > 0):
                    hex_list.append(conv_cmd(cmd_arg[1],      0b0101, "INSTR")) #  xxxxxxxx_0101_0
                else:
                    hex_list.append(conv_cmd(abs(cmd_arg[1]), 0b1101, "INSTR")) #  xxxxxxxx_0101_0
            case "I2C_START_WRITE":
                hex_list.append(conv_cmd(cmd_arg[1], 0b0101, "TRANSFER")) # 00000000_0101_1
            case "I2C_START_READ":
                hex_list.append(conv_cmd(cmd_arg[1], 0b0001, "TRANSFER")) # 00000000_0001_1
            case "I2C_SEND":
                hex_list.append(conv_cmd(cmd_arg[1], 0b0100, "TRANSFER")) # 00000000_0100_1
            #SPI
            case "SPI_TRANSFER":
                hex_list.append(conv_cmd(cmd_arg[1], 0b0000, "TRANSFER")) # 00000000_0000_1
            case "SPI_HD_WRITE":
                hex_list.append(conv_cmd(cmd_arg[1], 0b0001, "TRANSFER")) # 00000000_0001_1
    #
    return hex_list

def local_build_write_meminit(value_list, commands_list, init_type, bit_width, file_handler):

    def to_bin_str(value, bit_width):
        bin_s = bin(value)[2:]
        if len(bin_s) < bit_width:
            bin_s = "0"*(bit_width - len(bin_s)) + bin_s
        return bin_s
    
    def to_hex_str(value, bit_width):
        hex_s = hex(value)[2:]
        hex_width = bit_width//4 + 1 if bit_width%4 else 0
        if len(hex_s) < hex_width:
            hex_s = "0"*(hex_width - len(hex_s)) + hex_s
        return hex_s
    
    def list_to_str(list):
        olist = ""
        for item in list[:-1]:
            olist += str(item) if isinstance(item, int) else item
            olist += " "
        olist += "(line # " + str(list[-1]) + ")"
        return olist
    
    cnt = 0
    for value in value_list:
        cmd_code = to_hex_str(value, bit_width) if init_type == "hex" else to_bin_str(value, bit_width)
        line  = cmd_code + " "
        if init_type == "binary":
            line += "//HEX[" + to_hex_str(value, bit_width)
        else:
            line += "//BIN[" + to_bin_str(value, bit_width)
        line += "] -> " + list_to_str(commands_list[cnt]) + "\n"
        file_handler.write(line)

        cnt += 1
    

###################################################################################################

###################################################################################################
# Builder
# init_type : can be "hex" or "binary"
###################################################################################################
def parser_build(parsed_dict, init_type, out_file_path):
    from datetime import datetime

    print("[BUILDER] Run builder...")
    command_width_bits = 13
    #Check for bus
    bus_type = local_builder_check_bus(parsed_dict["bus_define"])
    if bus_type == "":
        return 0
    if local_builder_check_commands(parsed_dict["commands"], bus_type) > 0:
        return 0
    if local_builder_replace_const(parsed_dict["commands"], parsed_dict["constants"], False) > 0:
        return 0
    if local_builder_replace_labels(parsed_dict["commands"], parsed_dict["labels"], False) > 0:
        return 0
    #Changes are stored in dictionary after procedures above
    hex_list = local_build_convert_to_hex(parsed_dict["commands"])
    
    #Write to the file
    fw = open(out_file_path, 'w')
    fw.write("//************************************************************* \n")
    fw.write("// File name:  " + os.path.basename(out_file_path) + "\n")
    fw.write("// Init type:  " + init_type + "\n")
    fw.write("// Bus type:   " + parsed_dict["bus_define"][0] + "\n")
    fw.write("// Word width: " + str(command_width_bits) + " bits\n")
    fw.write("// Data:       " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
    fw.write("//************************************************************* \n")
    local_build_write_meminit(hex_list, parsed_dict["commands"], init_type, command_width_bits, fw)
    fw.close()

    print("[BUILDER] Build successfully ended")
    return 1


