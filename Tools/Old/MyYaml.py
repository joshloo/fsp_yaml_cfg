import os
import sys
import re
import time
import copy
import string
import pprint
from collections import OrderedDict

class ArgTemplate(string.Template):
    idpattern = '\([0-9]+\)'


class CFG_YAML():

    def __init__ (self):
        self.curr_ptr  = 0
        self._cfg_tree = None
        self._tmp_tree = None
        self.lines     = []

    @staticmethod
    def count_indent (line):
        return next((i for i, c in enumerate(line) if not c.isspace()), len(line))

    @staticmethod
    def dprint (*args):
        pass
        #print (*args)

    def process_expand (self, temp_name, prefix,  args):
        #self._tmp_tree[temp_name]
        #print (temp_name, prefix,  args)
        parts = args.split(',')
        parts = [i.strip() for i in parts]
        num = len(parts)
        arg_dict = dict(zip( ['(%d)' % (i + 1) for i in range(num)], parts))
        str_data = self._tmp_tree[temp_name]
        text = ArgTemplate(str_data).safe_substitute(arg_dict)
        current = CFG_YAML.count_indent (text)
        target  = CFG_YAML.count_indent (prefix) + 2
        padding = (target - current) * ' '
        text = [prefix + '\n'] + [padding + i + '\n' for i in text.splitlines()]
        return text

    def apply_template (self):
        # \s+\{\s*(\w+_TMPL)\s*:\s*\[(.+)]\s*\}
        # - CfgHeader    : !expand { CFGHDR_TMPL : [ FEATURES_CFG_DATA, 0x310, 0, 0 ] }
        expand_exp = re.compile (r'(.+:\s+)!expand\s+\{\s*(\w+_TMPL)\s*:\s*\[(.+)]\s*\}')
        new_lines = []
        for line in self.lines:
            match = expand_exp.match(line)
            if not match:
                new_lines.append (line)
                continue
            temp_name = match.group(2)
            if temp_name in self._tmp_tree:
                lines = self.process_expand (temp_name, match.group(1), match.group(3))
                new_lines.extend (lines)
            else:
                raise Exception ("Failed to find template '%s' !" % temp_name)
        self.lines = new_lines

    def load_file (self, yaml_file):
        self.index  = 0
        fi = open (yaml_file)
        self.lines = fi.readlines()
        fi.close ()

    def peek_line (self):
        if len(self.lines) == 0:
            return None
        else:
            return self.lines[0]


    def put_line (self, line):
        self.lines.insert (0, line)


    def get_line (self):
        if len(self.lines) == 0:
            return None
        else:
            return self.lines.pop(0)

    def get_multiple_line (self, indent):
        text   = ''
        newind = indent + 1
        while True:
            line   = self.peek_line ()
            if line is None:
                break
            newind = CFG_YAML.count_indent(line)
            if newind <= indent:
                break
            self.get_line ()
            if line.strip() != '':
                text = text + line
        return text

    def parse (self, curr = None, level = 0):
        child = None
        last_indent = None

        while True:
            line = self.get_line ()
            if line is None:
                break

            curr_line = line.strip()
            if not curr_line:
                continue

            indent  = CFG_YAML.count_indent(line)
            if last_indent is None:
                last_indent = indent

            if curr_line.endswith (': >'):
                line = self.get_multiple_line (indent)
                curr_line = curr_line + line

            if indent != last_indent:
                # put the line back to queue
                self.put_line (' ' * indent + curr_line)

            if indent > last_indent:
                if child is None:
                    #print (indent, last_indent)
                    #pprint.pprint (curr)
                    raise Exception ('Error: %s : (line)' % (curr_line))

                CFG_YAML.dprint ('#3', indent , last_indent)
                level += 1
                self.parse (child, level)
                level -= 1
                CFG_YAML.dprint ('#4', indent , last_indent)

                line = self.peek_line ()
                if line is not None:
                    curr_line = line.strip()
                    indent  = CFG_YAML.count_indent(line)
                    if indent >= last_indent:
                        self.get_line ()
                else:
                    indent = 0

            marker1 = curr_line[0]
            marker2 = curr_line[-1]
            if curr is None:
                curr = OrderedDict()

            if indent < last_indent:
                CFG_YAML.dprint ('#5', indent , last_indent, 'LVL %d' % level)
                return curr


            CFG_YAML.dprint ('#6', indent , last_indent, curr_line)
            start = 1 if marker1 == '-' else 0

            pos = curr_line.find(': ')
            if pos > 0:
                child = None
                key = curr_line[start:pos].strip()
                if curr_line[pos + 2] == '>':
                    curr[key] = curr_line[pos + 3:]
                else:
                    curr[key] = curr_line[pos + 2:].strip()
                CFG_YAML.dprint ('!1', curr)
            elif marker2 == ':':
                child = OrderedDict()
                key = curr_line[start:-1].strip()
                if key == '$ACTION':
                    key = '$ACTION_%02X' % self.index
                    self.index += 1
                curr[key] = child
                CFG_YAML.dprint ('!2', curr)
            else:
                child = None
                CFG_YAML.dprint ('!3', curr)
        return curr


    def traverse_cfg_tree (self, handler, root = None):
        def _traverse_cfg_tree (root, level = 0):
            if type(root) is OrderedDict:
                for key in root:
                    handler (key, root[key], level)
                    level += 1
                    _traverse_cfg_tree (root[key], level)
                    level -= 1

        if root is None:
            root = self._cfg_tree
        _traverse_cfg_tree (root)


    def FormatValue (self, field, text, indent = ''):
        if (not text.startswith('!expand')) and (': ' in text):
            text = text.replace(': ', "- ")
        lines = text.splitlines()
        if len(lines) == 1 and field != 'help':
            return text
        else:
            return '>\n   ' + '\n   '.join ([indent + i.lstrip() for i in lines])


    def print_cfgs(self, plevel = 2):
        def _print_cfgs (name, cfgs, level):
            offset  = 0
            length  = 0
            bit_len = ''
            value   = ''
            indent  = '  ' * level
            if type(cfgs) is str:
                if  '\n' in cfgs:
                    long_indent = indent + ' ' * 20
                    value = '>\n   ' + '\n   '.join ([long_indent + i.lstrip() for i in cfgs.splitlines()])
                else:
                    value = cfgs
            else:
                value = ''

            if level < plevel:
                print('%04X:%04X%-6s %s%s : %s' % (offset, length, bit_len, indent, name, value))

        self.traverse_cfg_tree (_print_cfgs)


    def load_yaml (self, tmp_file, opt_file):

        self.load_file	(tmp_file)
        self._tmp_tree = self.parse ()
        self.load_file	(opt_file)
        self.apply_template ()
        self._cfg_tree = self.parse ()
        return self._cfg_tree


if __name__ == "__main__":
    import time

    cfg_yaml = CFG_YAML()

    start = time.time()
    cfg_yaml.load_yaml ('cfg_tmp.yaml', 'cfg_opt.yaml')
    end = time.time()
    print ('Load config: %s' % (end - start))

    cfg_yaml.print_cfgs ()
    print ('Done')
