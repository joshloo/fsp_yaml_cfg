## @ GenCfgData.py
#
# Copyright (c) 2014 - 2019, Intel Corporation. All rights reserved.<BR>
# SPDX-License-Identifier: BSD-2-Clause-Patent
#
##

from CfgHelper import *

class CGenCfgData:

    bits_width  = {'b':1, 'B':8, 'W':16, 'D':32, 'Q':64}

    special_key = {'STRUCT':'$STRUCT'}

    def __init__(self):
        self._builtin_option = {'$EN_DIS' : [('0', 'Disable'), ('1', 'Enable')]}
        self.initialize ()

    def initialize (self):
        self._cfg_tree  = {}
        self._cfg_list  = []
        self._cfg_page  = {'root': {'title': '', 'child': []}}
        self._cur_page  = ''
        self._var_dict  = {}

    def get_variable (self, var):
        if var in self._var_dict:
            return self._var_dict[var]

        if '__' in var:
            var  = var.replace ('__', '.')
            item = self.locate_cfg_item (var)
            return self.get_cfg_item_value (item['link'])

        raise Exception ("Cannot find variable '%s' !" % var)

    def eval (self, expr):
        expr_eval = ExpressionEval ()
        if '$' in expr:
            # translate variable format from $aaa.bbb to aaa__bbb to let AST recognize.
            # '__' is reserved and should not be used in any normal variable
            handler = lambda pattern: pattern.group(1).replace('.' , '__')
            expr = re.sub(r'\$([\w\.]+)', handler, expr)
        return expr_eval.eval(expr, self.get_variable)

    def get_cfg_list (self, page_id = None):
        if page_id is None:
            # return full list
            return self._cfg_list
        else:
            # build a new list for items under a page ID
            return [i for i in self._cfg_list if i['name'] and (i['page'] == page_id)]

    def get_cfg_page (self):
        return self._cfg_page

    def get_cfg_item_value (self, item, array = False):
        value_str = item['value']
        length    = item['length']
        return  self.get_value (value_str, length, array)


    def value_to_str (self, value):
        if isinstance(value, int):
            value_str = str(value)
        elif isinstance(value, bytes) or isinstance(value, bytearray):
            value_str = '{ ' + ', '.join(['0x%02x' % i for i in value]) + ' }'
        elif isinstance(value, str):
            value_str = "'" + value + "'"
        else:
            raise SystemExit ("Error: Invalid value type '%s' to set !" % type(value))
        return value_str


    def normalize_value (self, value_str, bit_length):
        if bit_length <= 8 * 8:
            is_array = False
        else:
            is_array = True
        values = self.parse_value (value_str, bit_length, is_array)
        if is_array:
            new_value = bytes_to_bracket_str (values)
        else:
            new_value = '0x%x' % values
        return new_value


    def get_value (self, value_str, bit_length, array = True):
        value_str = value_str.strip()
        if value_str[0] in '{' :
            value_str = value_str[1:-1].strip()
        value = 0
        for each in value_str.split(',')[::-1]:
            each = each.strip()
            value = (value << 8) | int(each, 0)
        if array:
            length = (bit_length + 7) // 8
            return value_to_bytearray (value, length)
        else:
            return value


    def parse_value (self, value_str, bit_length, array = True):
        length = (bit_length + 7) // 8
        if value_str[0] == '{':
            result = bytearray()
            bin_list = value_str[1:-1].split(',')
            value            = 0
            bit_len          = 0
            unit_len         = 1
            for idx, element in enumerate(bin_list):
                each = element.strip()
                if len(each) == 0:
                    continue

                in_bit_field = False
                if each[0] in "'" + '"':
                    each_value = bytearray(each[1:-1], 'utf-8')
                elif ':' in each:
                    match    = re.match("^(.+):(\d+)([b|B|W|D|Q])$", each)
                    if match is None:
                        raise SystemExit("Exception: Invald value list format '%s' !" % each)
                    if match.group(1) == '0' and match.group(2) == '0':
                        unit_len = CGenCfgData.bits_width[match.group(3)] // 8
                    cur_bit_len = int(match.group(2)) * CGenCfgData.bits_width[match.group(3)]
                    value   += ((self.eval(match.group(1)) & (1<<cur_bit_len) - 1)) << bit_len
                    bit_len += cur_bit_len
                    each_value = bytearray()
                    if idx + 1 < len(bin_list):
                        in_bit_field = True
                else:
                    each_value = value_to_bytearray(self.eval(each.strip()), unit_len)

                if not in_bit_field:
                    if bit_len > 0:
                        if bit_len % 8 != 0:
                            raise SystemExit("Exception: Invalid bit field alignment '%s' !" % value_str)
                        result.extend(value_to_bytes(value, bit_len // 8))
                    value   = 0
                    bit_len = 0

                result.extend(each_value)

        elif (value_str.startswith("'") and value_str.endswith("'")) or \
             (value_str.startswith('"') and value_str.endswith('"')):
            result = bytearray(value_str[1:-1], 'utf-8')  # Excluding quotes
        else:
            result = value_to_bytearray (self.eval(value_str), length)

        if len(result) < length:
            result.extend(b'\x00' * (length - len(result)))
        elif len(result) > length:
            raise SystemExit ("Exception: Value '%s' is too big to fit into %d bytes !" % (value_str, length))

        if array:
            return result
        else:
            return bytes_to_value(result)

        return result


    def get_cfg_item_options (self, item):
        tmp_list = []
        if  item['type'] == "Combo":
            if item['option'] in self._builtin_option:
                for op_val, op_str in self._builtin_option[item['option']]:
                    tmp_list.append((op_val, op_str))
            else:
                opt_list = item['option'].split(',')
                for option in opt_list:
                    option = option.strip()
                    try:
                        (op_val, op_str) = option.split(':')
                    except:
                        raise SystemExit ("Exception: Invalide option format '%s' !" % option)
                    tmp_list.append((op_val, op_str))
        return  tmp_list





    def locate_cfg_item (self, path):
        def _locate_cfg_item (root, path, level = 0):
            if len(path) == level:
                return root
            index = [idx for idx, item in enumerate(root) if path[level] == next(iter(item))]
            if len(index) == 0:
                raise SystemExit ('Not a valid CFG option: %s' % '.'.join(path[:level+1]))
            next_root = root[index[0]][path[level]]
            return _locate_cfg_item (next_root, path, level + 1)
        path_nodes = path.split('.')
        return _locate_cfg_item (self._cfg_tree, path_nodes)


    def traverse_cfg_tree (self, handler, root = None):
        def _traverse_cfg_tree (root, level = 0):
            for node in root:
                name = next(iter(node))
                cfgs = node[name]
                if type(cfgs) is list:
                    handler (name, cfgs, level)
                    level += 1
                    _traverse_cfg_tree (cfgs, level)
                    level -= 1
                else:
                    handler (name, cfgs, level)

        if root is None:
            root = self._cfg_tree
        _traverse_cfg_tree (root)


    def print_cfgs(self, root = None):
        def _print_cfgs (name, cfgs, level):
            if name[0] == '$':
                return
            if type(cfgs) is dict:
                if 'link' not in cfgs:
                    return
                act_cfg = cfgs['link']
                value   = act_cfg['value']
            else:
                act_cfg = cfgs[0]['$STRUCT']
                if 'value' in act_cfg:
                    value = self.normalize_value (str(act_cfg['value']), act_cfg['length'])
                else:
                    value = ''
            bit_len = act_cfg['length']
            offset  = (act_cfg['offset'] + 7) // 8
            length  = bit_len // 8
            bit_len = '(%db)' % bit_len if bit_len % 8 else '' * 4
            print('%04X:%04X%-6s %s%s : %s' % (offset, length, bit_len, '  ' * level, name, value))
        self.traverse_cfg_tree (_print_cfgs)


    def create_var_dict (self):
        def _create_var_dict (name, cfgs, level):
            cfg_hdr_len = 8
            if type(cfgs) is list:
                append = False
                if level <= 1:
                    append = True

                if append:
                    struct_info = cfgs[0][CGenCfgData.special_key['STRUCT']]
                    self._var_dict['_LENGTH_%s_' % name] = struct_info['length'] // 8
                    self._var_dict['_OFFSET_%s_' % name] = struct_info['offset'] // 8

        self._var_dict  = {}
        self.traverse_cfg_tree (_create_var_dict)
        self._var_dict['_LENGTH_'] = self._cfg_tree[0]['$STRUCT']['length'] // 8
        return 0


    def get_page_title(self, page_id, top = None):
        if top is None:
            top = self.get_cfg_page()['root']
        for node in top['child']:
            page_key = next(iter(node))
            if page_id == page_key:
                return node[page_key]['title']
            else:
                result = self.get_page_title (page_id, node[page_key])
                if result is not None:
                    return result
        return None


    def print_pages(self, top=None, level=0):
        if top is None:
            top = self.get_cfg_page()['root']
        for node in top['child']:
            page_id = next(iter(node))
            print('%s%s: %s' % ('  ' * level, page_id, node[page_id]['title']))
            level += 1
            self.print_pages(node[page_id], level)
            level -= 1


    def add_cfg_page(self, child, parent, title=''):
        def _add_cfg_page(cfg_page, child, parent):
            key = next(iter(cfg_page))
            if parent == key:
                cfg_page[key]['child'].append({child: {'title': title,
                                                       'child': []}})
                return True
            else:
                result = False
                for each in cfg_page[key]['child']:
                    if _add_cfg_page(each, child, parent):
                        result = True
                        break
                return result

        return _add_cfg_page(self._cfg_page, child, parent)


    def set_cur_page(self, page_str):
        if not page_str:
            return
        if ',' in page_str:
            page_list = page_str.split(',')
        else:
            page_list = [page_str]
        for page_str in page_list:
            parts = page_str.split(':')
            if len(parts) in [1, 3]:
                page = parts[0].strip()
                if len(parts) == 3:
                    # it is a new page definition, add it into tree
                    parent = parts[1] if parts[1] else 'root'
                    parent = parent.strip()
                    if not self.add_cfg_page(page, parent, parts[2]):
                        raise SystemExit("Error: Cannot find parent page '%s'!" % parent)
            else:
                raise SystemExit("Error: Invalid page format '%s' !" % page_str)
            self._cur_page = page


    def add_cfg_item(self, name, item, offset):

        self.set_cur_page (item.get('page', ''))

        if name[0] == '$':
            # skip all virtual node
            return 0

        length = item.get('length', 0)
        if type(length) is str:
            match = re.match("^(\d+)([b|B|W|D|Q])([B|W|D|Q]?)", length)
            if match:
                unit_len = CGenCfgData.bits_width[match.group(2)]
                length = int(match.group(1), 10) * unit_len
            else:
                raise SystemExit ("Exception: Invalid length field '%s' !" % length)
        else:
            # define is length in bytes
            length = length * 8
        if length == 0:
            return 0

        itype = str(item.get('type', 'reserved'))
        value = str(item.get('value', ''))
        if itype == 'EditText':
            value = "'%s'" % value
        elif ',' in value:
            value = '{ %s }' % value
        elif value:
            try:
                int(value, 0)
            except:
                if len(value) * 8 == length:
                    value = self.value_to_str(value.encode())


        cfg_item = dict()
        cfg_item['length'] = length
        cfg_item['offset'] = offset
        cfg_item['value']  = value
        cfg_item['type']   = itype
        cfg_item['cname']  = str(name)
        cfg_item['name']   = str(item.get('prompt', ''))
        cfg_item['help']   = str(item.get('help', ''))
        cfg_item['option'] = str(item.get('option', ''))
        cfg_item['condition'] = str(item.get('condition', ''))
        cfg_item['page']   = self._cur_page
        cfg_item['order']  = 0
        cfg_item['link']   = item
        item['link']       = cfg_item
        self._cfg_list.append(cfg_item)

        return length


    def build_cfg_list (self, top = None, path = [], info = {'offset': 0}):
        if top is None:
            top = self._cfg_tree
        # config structure
        start = info['offset']
        for node in top:
            cfg_name = next(iter(node))
            cfgs = node[cfg_name]
            if type(cfgs) is list:
                # config structure
                path.append(cfg_name)
                self.build_cfg_list(cfgs, path, info)
                path.pop()
            elif type(cfgs) is dict:
                # leaf config item
                length = self.add_cfg_item(cfg_name, cfgs, info['offset'])
                info['offset'] += length
            else:
                raise SystemExit("Error: Invalid CFG file format for %s !" % str(path))

        # check first element for strcut
        first = next(iter(top[0]))
        struct_str = CGenCfgData.special_key['STRUCT']
        if first != struct_str:
            top.insert(0, {struct_str: {}})
        struct_node = top[0][struct_str]
        struct_node['offset'] = start
        struct_node['length'] = info['offset'] - start
        if struct_node['length'] % 8 != 0:
            raise SystemExit("Error: Bits length not aligned for %s !" % str(path))


    def get_last_error (self):
        return ''



    def get_field_value (self, top = None):
        def _get_field_value (top):
            for node in top:
                cfg_name = next(iter(node))
                if cfg_name[0] == '$':
                    continue
                cfgs = node[cfg_name]
                if type(cfgs) is list:
                    _get_field_value (cfgs)
                elif type(cfgs) is dict:
                    if 'link' in cfgs:
                        act_cfg = cfgs['link']
                        value = self.get_value (act_cfg['value'], act_cfg['length'], False)
                        set_bits_to_bytes (result, act_cfg['offset'] - struct_info['offset'], act_cfg['length'], value)
        if top is None:
            top = self._cfg_tree

        struct_info = top[0][CGenCfgData.special_key['STRUCT']]
        result = bytearray (struct_info['length'] // 8)
        _get_field_value (top)
        return  result


    def set_field_value (self, top, value_bytes, force = False):
        def _set_field_value (top, force):
            for node in top:
                cfg_name = next(iter(node))
                if cfg_name[0] == '$':
                    continue
                cfgs = node[cfg_name]
                if type(cfgs) is list:
                     _set_field_value (cfgs, force)
                elif type(cfgs) is dict and ('link' in cfgs):
                     act_cfg = cfgs['link']
                     if force or act_cfg['value'] == '':
                         value = get_bits_from_bytes (full_bytes, act_cfg['offset'] - struct_info['offset'], act_cfg['length'])
                         if value > 0xffffffff:
                            act_cfg['value'] = bytes_to_bracket_str (value_to_bytes (value))
                         else:
                            act_cfg['value'] = '0x%x' % value

        if isinstance(top, list):
            # it is a structure
            struct_info = top[0][CGenCfgData.special_key['STRUCT']]
            length = struct_info['length'] // 8
            full_bytes = bytearray(value_bytes)
            if len(full_bytes) < length:
                full_bytes.extend(bytearray(length - len(value_bytes)))
            _set_field_value (top, force)
        else:
            # it is config option
            value_str = self.value_to_str (value_bytes)
            act_cfg = top['link']
            act_cfg['value'] = self.normalize_value (value_str, act_cfg['length'])


    def update_def_value (self):
        def _update_def_value (top):
            for node in top:
                cfg_name = next(iter(node))
                cfgs = node[cfg_name]
                if cfg_name.startswith('$STRUCT'):
                    if 'value' in cfgs:
                        value_bytes = value_to_bytearray (self.eval(str(cfgs['value'])), (cfgs['length'] + 7) // 8)
                        self.set_field_value (top, value_bytes)
                    continue
                cfgs = node[cfg_name]
                if type(cfgs) is list:
                    _update_def_value(cfgs)
                elif type(cfgs) is dict and cfg_name[0] != '$':
                    if 'link' in cfgs:
                        act_cfg = cfgs['link']
                        act_cfg['value'] = self.normalize_value (act_cfg['value'], act_cfg['length'])

        _update_def_value (self._cfg_tree)


    def evaluate_condition (self, path):
        cfg = self.locate_cfg_item (path)
        if 'link' not in cfg:
            return 0

        if not cfg['link']['condition']:
            return 1

        result = self.parse_value (cfg['link']['condition'], 8, False)
        return result


    def generate_binary (self):
        return self.get_field_value()


    def parse_yaml_file(self, tmp_file, cfg_file):
        self.initialize ()
        tmp = load_yaml (tmp_file)
        #tmp = {}
        #for each in res:
        #    tmp.update (each)
        YamlLoader.set_template(tmp)

        # Merge all configs to same level
        self._cfg_tree = load_yaml (cfg_file)
        #self._cfg_tree = []
        #for each in res:
        #    self._cfg_tree.extend(each)

        self.build_cfg_list()
        self.create_var_dict()
        self.update_def_value()
        return 0




class Test:
    def __init__ (self):
        self.cfg_data = CGenCfgData()
        self.cfg_data.parse_yaml_file('cfg_tmp.yaml', 'cfg_opt.yaml')

    def test_get_field_value (self):
        # get full
        result = self.cfg_data.get_field_value ()
        print_bytes (result, show_ascii = True)
        print ('')

        # get boot option1
        top = self.cfg_data.locate_cfg_item ('BOOT_OPTION_0.BootOption')
        result = self.cfg_data.get_field_value (top)
        print_bytes (result, show_ascii = True)
        print ('')

        top = self.cfg_data.locate_cfg_item ('GPIO_DATA.Gpio_A00.Config0')
        result = self.cfg_data.get_field_value (top)
        print_bytes (result, show_ascii = True)
        print ('')

        top = self.cfg_data.locate_cfg_item ('BOOT_OPTION_0.BootOption.ImageType')
        print (top['link']['value'])

        top = self.cfg_data.locate_cfg_item ('BOOT_OPTION_0.BootOption.BootImage')
        print (top['link']['value'])


    def test_set_field_value (self):
        top = self.cfg_data.locate_cfg_item ('BOOT_OPTION_0.BootOption')
        #self.cfg_data.set_cfg_value (top, bytearray(b'ABCD.RAW'))
        self.cfg_data.set_field_value (top, bytearray(b'HELLO'), True)


    def test_print_cfg (self):
        self.cfg_data.print_cfgs()

    def test_get_value (self):
        tests = [
          ('0x12347788',  8),
          ('"12"',  4),
          ("{'ABCD', 0x11}",  5),
          ('{ 0, 1, 0x2, 35 }',  4),
          ('{ 1:1b, 2:2b, 0x1F:5b, 0x44, 0x5566:16b }',   4),
          ('{ 0x11, 0x22, 0:1W, 0x1122, 0x3344, 0x88 }',  8),
          ('4+5*8 > 1',  4),
        ]
        for val, len in tests:
            tres = self.cfg_data.get_value (val, len)
            print_bytes (tres)


if __name__ == "__main__":
    # execute only if run as a script
    test = Test()

    test.cfg_data.print_cfgs()


