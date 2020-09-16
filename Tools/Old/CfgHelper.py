## @ GenCfgData.py
#
# Copyright (c) 2014 - 2019, Intel Corporation. All rights reserved.<BR>
# SPDX-License-Identifier: BSD-2-Clause-Patent
#
##

import os
import re
import sys
import struct
import marshal
import pprint
import string
import io
from string import Template
from functools import reduce
from datetime import date
from ruamel import yaml

import operator as op
import ast

def print_bytes (data, indent=0, offset=0, show_ascii = False):
    bytes_per_line = 16
    printable = ' ' + string.ascii_letters + string.digits + string.punctuation
    str_fmt = '{:s}{:04x}: {:%ds} {:s}' % (bytes_per_line * 3)
    bytes_per_line
    data_array = bytearray(data)
    for idx in range(0, len(data_array), bytes_per_line):
        hex_str = ' '.join('%02X' % val for val in data_array[idx:idx + bytes_per_line])
        asc_str = ''.join('%c' % (val if (chr(val) in printable) else '.')
                          for val in data_array[idx:idx + bytes_per_line])
        print (str_fmt.format(indent * ' ', offset + idx, hex_str, ' ' + asc_str if show_ascii else ''))


def bytes_to_value (bytes):
    return reduce(lambda x,y: (x<<8)|y,  bytes[::-1] )


def bytes_to_bracket_str (bytes):
    return '{ %s }' % (', '.join('0x%02X' % i for i in bytes))


def value_to_bytes (value, length):
    return [(value>>(i*8) & 0xff) for i in range(length)]


def value_to_bytearray (value, length):
    return bytearray(value_to_bytes(value, length))


def get_bits_from_bytes (bytes, start, length):
    value  = bytes_to_value (bytes)
    bitlen = 8 * len(bytes)
    fmt    = "{0:0%db}" % bitlen
    start  = bitlen - start
    if start < 0 or start < length:
        raise Exception ('Invalid bit start and length !')
    bval  = fmt.format(value)[start - length : start]
    return int (bval, 2)


def set_bits_to_bytes (bytes, start, length, bvalue):
    value  = bytes_to_value (bytes)
    bitlen = 8 * len(bytes)
    fmt1   = "{0:0%db}" % bitlen
    fmt2   = "{0:0%db}" % length
    oldval = fmt1.format(value)[::-1]
    update = fmt2.format(bvalue)[-length:][::-1]
    newval = oldval[:start] + update + oldval[start + length:]
    bytes[:] = value_to_bytes (int(newval[::-1], 2), len(bytes))


class ArgTemplate(string.Template):
    idpattern = '\([0-9]+\)'


class YamlLoader(yaml.SafeLoader):

    template = {}

    def __init__(self, stream, version):
        super(YamlLoader, self).__init__(stream, version)
        self.mx = {}

    @staticmethod
    def set_template(template):
        YamlLoader.template = template

    def include(self, node):
        with open(node.value, 'r') as f:
            return yaml.safe_load(f)

    def expand(self, node):
        mapping = self.construct_mapping(node)
        key = next(iter(mapping))
        mapping[key] = self.construct_sequence(node.value[0][1])
        arg_dict = dict(zip(
            ['(%d)' % (i + 1) for i in range(len(mapping[key]))], [str(
                i) for i in mapping[key]]))
        for karg in arg_dict:
            if '#' in arg_dict[karg] and arg_dict[karg][0] not in "'" + '"':
                arg_dict[karg] = "'" + arg_dict[karg] + "'"
        if key in YamlLoader.template:
            str_data = '\n%s\n' % YamlLoader.template[key]
            text = ArgTemplate(str_data).safe_substitute(arg_dict)
        else:
            text = ''
        return yaml.safe_load(text)


yaml.add_constructor("!include", YamlLoader.include, Loader=yaml.SafeLoader)
yaml.add_constructor('!expand',  YamlLoader.expand,  Loader=yaml.SafeLoader)


def load_yaml(file):
    body = None
    with open(file, 'r') as stream:
        try:
            body = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise SystemExit('Exception: %s' % exc)
    return body


class ExpressionEval(ast.NodeVisitor):
    operators = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.floordiv,
        ast.Mod: op.mod,
        ast.Eq: op.eq,
        ast.NotEq: op.ne,
        ast.Gt: op.gt,
        ast.Lt: op.lt,
        ast.GtE: op.ge,
        ast.LtE: op.le,
        ast.BitXor: op.xor,
        ast.BitAnd: op.and_,
        ast.BitOr: op.or_,
        ast.USub: op.neg
    }

    def __init__(self):
        self._debug = False
        self._expression = ''
        self._namespace = {}
        self._get_variable = None

    def format_expr(self, expr):
        # Replace all $xxx.yyy.zzz to xxx_yyy_zzz
        formatter = lambda pattern: pattern.group(1).replace('.', '__')
        new_expr = re.sub(r'(?<![\.\w])\$([\w\.]+)', formatter, expr)
        return new_expr

    def eval(self, expr, vars={}):
        self._expression = self.format_expr(expr)
        if type(vars) is dict:
            self._namespace = vars
            self._get_variable = None
        else:
            self._namespace = {}
            self._get_variable = vars
        node = ast.parse(self._expression, mode='eval')
        result = self.visit(node.body)
        if self._debug:
            print ('EVAL [ %s ] = %s' % (expr, str(result)))
        return result

    def visit_Name(self, node):
        if self._get_variable is not None:
            return self._get_variable(node.id)
        else:
            return self._namespace[node.id]

    def visit_Num(self, node):
        return node.n

    def visit_NameConstant(self, node):
        return node.value

    def visit_BoolOp(self, node):
        result = False
        if isinstance(node.op, ast.And):
            for value in node.values:
                result = self.visit(value)
                if not result:
                    break
        elif isinstance(node.op, ast.Or):
            for value in node.values:
                result = self._eval(value)
                if result:
                    break
        return True if result else False

    def visit_UnaryOp(self, node):
        val = self.visit(node.operand)
        return operators[type(node.op)](val)

    def visit_BinOp(self, node):
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)
        return ExpressionEval.operators[type(node.op)](lhs, rhs)

    def visit_Compare(self, node):
        right = self.visit(node.left)
        result = True
        for operation, comp in zip(node.ops, node.comparators):
            if not result:
                break
            left = right
            right = self.visit(comp)
            result = ExpressionEval.operators[type(operation)](left, right)
        return result

    def generic_visit(self, node):
        raise ValueError("malformed node or string: " + repr(node))


if __name__ == "__main__":
    import time

    start = time.time()
    tmp = load_yaml ('cfg_tmp.yaml')
    end = time.time()
    print ('Load template: %s' % (end - start))

    #tmp = {}
    #for each in res:
    #    tmp.update (each)
    YamlLoader.set_template(tmp)
    start = time.time()
    cfg = load_yaml ('cfg_opt.yaml')
    end = time.time()
    print ('Load  configs: %s' % (end - start))

    #cfg = []
    #for each in res:
    #   cfg.extend(each)
    #pprint.pprint(cfg)

    print ('Done')
