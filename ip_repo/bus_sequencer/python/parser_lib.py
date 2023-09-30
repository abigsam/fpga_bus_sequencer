from __future__ import unicode_literals

import sys
import os
import re


###################################################################################################
#Check all dependiences and install if missing
###################################################################################################
import subprocess
import pkg_resources
# required = {'pyparsing', 'pyleri', 'Arpeggio'}
required = {'pyparsing', 'pyleri'}
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
from typing import NamedTuple
import re

class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int

def parser_get_tokens(file_lines):
    keywords = {'STOP', 'WAIT', 'CMP', 'CMP_LAST', 'CMP_JMP', 'PAUSE', 'UNCOND_JMP', 'NOP',
                'I2C_START_WRITE', 'I2C_START_READ', 'I2C_STOP', 'I2C_SEND', 'I2C_RECEIVE_ACK', 'I2C_RECEIVE_NACK',
                'SPI_TRANSFER', 'SPI_HD_WRITE', 'SPI_HD_READ', 'equ', 'EQU'}
    token_specification = [
        ('COMMENT',     r'[;]{1}'),                 #Comment
        ('BUS_TYPE',    r'[.]{1}'),                 #Bus name quilifier ('.')
        ('HEX_BYTE',    r'0x[0-9a-fA-F]{1,2}'),     #HEX number
        ('ASSIGN',      r'equ|EQU'),                #Assignment operator
        ('ID',          r'[A-Za-z_][A-Za-z0-9_]+'), #Identifiers
        ('LABEL',       r'[:]{1}'),                 #Jump label
        ('NEWLINE',     r'\n'),                     #Line endings
        ('SKIP',        r'[ \t]+'),                 #Skip over spaces and tabs
        ('MISMATCH',    r'.'),                      #Any other character
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_num = 1
    line_start = 0
    comment_detected = 0
    #Check if get string or list of strings
    code_str = ""
    if not isinstance(file_lines, str):
        code_str = ''.join(file_lines)
    else:
        code_str = file_lines
    for mo in re.finditer(tok_regex, code_str):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start

        #If previous token was comment, skip all untill new line
        if comment_detected == 1:
            if kind == 'NEWLINE':
                comment_detected = 0
                line_start = mo.end()
                line_num += 1
            continue
        
        #Parse tokens
        if kind == 'COMMENT':
            comment_detected = 1
        elif kind == 'HEX_BYTE':
            value = int(value, 16)
        elif kind == 'ID':
            if value in keywords:
                kind = 'CMD'
            else:
                kind = 'ID'
        elif kind == 'NEWLINE':
            kind = value
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected on line {line_num}')
        #Save token if it not comment
        if comment_detected == 0:
            yield Token(kind, value, line_num, column)


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
# Local procedure
# Parse input string for constants
# Return: dictionary [constant name] = value
###################################################################################################
def local_parse_const(src_str):
    const_dict = {}
    from pyleri import (
        Grammar,
        Keyword,
        Regex,
        Sequence,
        Optional)

    #Create class for EQU/equ
    class ConstGrammar(Grammar):
        r_id = Regex('[a-zA-z][a-zA-Z0-9_]+')
        k_equ = Keyword('equ', ign_case=True)
        r_hex_byte = Regex('0x[0-9a-fA-F]{1,2}')
        r_comment = Regex('\s*[;].*')
        START = Sequence(r_id, k_equ, r_hex_byte, Optional(r_comment))
    const_grammar = ConstGrammar()

    #Parse program text
    for line in src_str.split("\n"):
        result = const_grammar.parse(line)
        if result.is_valid:
            lname = local_get_node_string(result.tree, "r_id")
            lvalue = int(local_get_node_string(result.tree, "r_hex_byte"), 16)
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
def local_parse_bus_type(src_str):
    bus_name = []

    from pyleri import (
        Grammar,
        Regex,
        Sequence,
        Optional)

    #Create class for EQU/equ
    class BusTypeGrammar(Grammar):
        r_id = Regex('[.][a-zA-z][a-zA-Z0-9_]+')
        r_comment = Regex('\s*[;].*')
        START = Sequence(r_id, Optional(r_comment))
    bus_grammar = BusTypeGrammar()

    #Parse program text
    for line in src_str.split("\n"):
        result = bus_grammar.parse(line)
        if result.is_valid:
            lname = local_get_node_string(result.tree, "r_id")
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
def local_parse_commands(src_str):
    commands = []

    from pyleri import (
        Grammar,
        Keyword,
        Sequence,
        Regex,
        Choice,
        Optional)

    #Create class for commands without arguments
    ign_case_no_arg = False
    class CmdNoArgumentsGrammar(Grammar):
        k_stop          = Keyword('STOP',             ign_case=ign_case_no_arg)
        k_pause         = Keyword('PAUSE',            ign_case=ign_case_no_arg)
        k_nop           = Keyword('NOP',              ign_case=ign_case_no_arg)
        k_i2c_stop      = Keyword('I2C_STOP',         ign_case=ign_case_no_arg)
        k_i2c_rack      = Keyword('I2C_RECEIVE_ACK',  ign_case=ign_case_no_arg)
        k_i2c_rnack     = Keyword('I2C_RECEIVE_NACK', ign_case=ign_case_no_arg)
        k_spi_hd_read   = Keyword('SPI_HD_READ',      ign_case=ign_case_no_arg)
        r_comment       = Regex('\s*[;].*')
        START = Sequence(Choice(k_stop, k_pause, k_nop, k_i2c_stop, k_i2c_rack,
                                k_i2c_rnack, k_spi_hd_read, most_greedy=False),
                        Optional(r_comment))
    cmd_no_arg_grammar = CmdNoArgumentsGrammar()

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
        r_id            = Regex('[a-zA-z][a-zA-Z0-9_]+')
        r_hex_byte      = Regex('0x[0-9a-fA-F]{1,2}')
        r_comment       = Regex('\s*[;].*')
        START = Sequence(Choice(k_wait, k_cmp, k_cmp_last, k_cmp_jump, k_uncond_jump,
                                k_i2c_swrite, k_i2c_sread, k_i2c_send, k_spi_transfer,
                                k_spi_hd_write, most_greedy=False),
                         Choice(r_id, r_hex_byte, most_greedy=False),
                         Optional(r_comment))
    cmd_with_arg_grammar = CmdWithArgumentsGrammar()

    #Parse program text
    lcnt = 0
    for line in src_str.split("\n"):
        #Parse commands without arguments
        result = cmd_no_arg_grammar.parse(line)
        if result.is_valid:
            lname = result.tree.children[0].children[0].string
            # print("DBG " + lname + " >>> " + str(lcnt))
            commands.append({lname, lcnt})
        else:
            #Parse commands with arguments
            result = cmd_with_arg_grammar.parse(line)
            if result.is_valid:
                seq_node = local_get_node(result.tree, "Sequence")
                lname = local_get_node(seq_node, "Choice", 0).string
                lvalue = local_get_node(seq_node, "Choice", 1).string
                # print("DBG " + lname + " : " + lvalue + " >>> " + str(lcnt))
                commands.append({lname, lcnt, lvalue})
        lcnt += 1

    #
    print("[PARSER] Was found " + str(len(commands)) + " command(s)")


###################################################################################################
# Local
# Parse for labels
###################################################################################################
def local_parse_labels(src_str):
    labels = []
    
    from pyleri import (
        Grammar,
        Keyword,
        Sequence,
        Regex,
        Choice,
        Optional)
    
    #Create grammar class
    class LabelsGrammar(Grammar):
        r_label_name  = Regex('[_][a-zA-Z][a-zA-Z0-9_]+')
        r_label_end   = Regex('[:]{1}')
        r_comment     = Regex('\s*[;].*')
        START = Sequence(r_label_name, r_label_end, Optional(r_comment))
    labels_grammar = LabelsGrammar()

    #Parse program text
    lcnt = 0
    for line in src_str.split("\n"):
        #Parse commands without arguments
        result = labels_grammar.parse(line)
        if result.is_valid:
            seq = local_get_node(result.tree, "Sequence", 0)
            lname = local_get_node(seq, "Regex", 0).string
            # print(" DBG --> " + lname)
            labels.append({lname, lcnt})
        lcnt += 1

    print("[PARSER] Was found " + str(len(labels)) + " label(s)")
    # for i in labels:
    #     print("DBG >>> ", end="")
    #     print(i)

    return labels


###################################################################################################
#Python Left-Right Parser
###################################################################################################
def parsering_program(src_str):
    print("[PARSER] Run parsing...")
    
    #Parse text
    const_dict = local_parse_const(src_str)
    bus_type = local_parse_bus_type(src_str)
    cmd_list = local_parse_commands(src_str)
    label_list = local_parse_labels(src_str)


###################################################################################################



###################################################################################################
# Try Arpeggio
###################################################################################################
# import os
from arpeggio import *
from arpeggio import RegExMatch as _

# Grammar
def comment():          return [_(r"//.*"), _(r"/\*.*\*/")]
def literal():          return _(r'\d*\.\d*|\d+|".*?"')
def symbol():           return _(r"\w+")
def operator():         return _(r"\+|\-|\*|\/|\=\=")
def operation():        return symbol, operator, [literal, functioncall]
def expression():       return [literal, operation, functioncall]
def expressionlist():   return expression, ZeroOrMore(",", expression)
def returnstatement():  return Kwd("return"), expression
def ifstatement():      return Kwd("if"), "(", expression, ")", block, Kwd("else"), block
def statement():        return [ifstatement, returnstatement], ";"
def block():            return "{", OneOrMore(statement), "}"
def parameterlist():    return "(", symbol, ZeroOrMore(",", symbol), ")"
def functioncall():     return symbol, "(", expressionlist, ")"
def function():         return Kwd("function"), symbol, parameterlist, block
def simpleLanguage():   return function

def test_arpeggio(src_str, debug=False):
    print("Run test arpeggio...")

    current_dir = os.path.dirname(__file__)
    test_program = open(os.path.join(current_dir, 'program.simple')).read()

    # Parser instantiation. simpleLanguage is the definition of the root rule
    # and comment is a grammar rule for comments.
    parser = ParserPython(simpleLanguage, comment, debug=debug)

    # parse_tree = parser.parse(src_str)
    parse_tree = parser.parse(test_program)

    print(parse_tree)

    class CalcVisitor(PTNodeVisitor):
        def visit_literal(self, node, children):
            # print(node)
            # return node
            return "literal"

        def visit_parameterlist(self, node, children):
            print(self)
            print(node)
            print(children)

    
    # result = visit_parse_tree(parse_tree, CalcVisitor(debug=debug))
    result = visit_parse_tree(parse_tree, CalcVisitor(debug=debug))

    print(result)


