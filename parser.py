import os, sys
import copy

class Parser:
    empty_line_d = {
        'filename': None,
        'fn_name': None,
        'line_number': None,
        'time': None,
        'lines': [],
        'attrs': {},
        'calls': [],
    }

    empty_call_d = {
        'filename': None,
        'fn_name': None,
        'times_called': 0,
        'time': None,
    }

    def __init__(self):
        self.filename_trans = {}
        self.fn_name_trans = {}

        self.global_attrs = {}

        self.lines_to_build = []
        self.cur_line_d = None

    def get_cur_line_d(self, force_new=False):
        if self.cur_line_d is None:
            self.cur_line_d = copy.deepcopy(self.empty_line_d)
        elif force_new:
            print(self.cur_line_d)
            self.cur_line_d = copy.deepcopy(self.empty_line_d)

        return self.cur_line_d

    def parse_line_attr(self, line):
        k,v = line.split(':', 2)
        if self.cur_line_d is None:
            self.global_attrs[k] = v.strip()
        else:
            self.cur_line_d['attrs'][k] = v.strip()

    def de_trans(self, line, trans):
        post = line.split('=', 2)[1]
        trans_no = None
        rest = None

        if post[0] == '(':
            trans_no, rest = post[1:].split(')', 2)
        else:
            rest = post

        care_name = None
        if trans_no.strip() and not rest.strip():
            care_name = trans.get(trans_no.strip())
        elif trans_no.strip() and rest.strip():
            care_name = rest.strip()
            trans[trans_no.strip()] = care_name
        elif rest.strip():
            care_name = rest.strip()

        return care_name

    def parse_line_filename(self, line):
        fn_name = self.de_trans(line, self.filename_trans)

        line_d = self.get_cur_line_d()
        line_d['filename'] = fn_name

    def parse_line_fn_call(self, line):
        fn_name = self.de_trans(line, self.fn_name_trans)

        line_d = self.get_cur_line_d()
        line_d['fn_name'] = fn_name

    def parse_line_number(self, line):
        line_no, time = line.split(' ')

        line_d = self.get_cur_line_d()
        line_d['line_number'] = line_no
        line_d['time'] = time

    def parse_line_empty(self, line):
        if self.cur_line_d is None:
            return

        print(self.cur_line_d)
        print('\n'.join(self.lines_to_build))
        self.cur_line_d = copy.deepcopy(self.empty_line_d)
        self.lines_to_build = []

    def parse_line(self, line):
        if ':' in line and '::' not in line:
            self.parse_line_attr(line)
        else:
            self.lines_to_build.append(line)
            if 'fn=' in line:
                self.parse_line_filename(line)
            elif 'fl=' in line:
                self.parse_line_fn_call(line)
            elif not line.strip():
                self.parse_line_empty(line)
            elif all(x.isdigit() for x in line.split(' ')):
                self.parse_line_number(line)

    def parse_file(self, filename):
        with open(filename) as fd:
            for i, line in enumerate(fd):
                self.parse_line(line)
                if i >= 1000: break

        print('\n'.join(self.lines_to_build))
        print(self.cur_line_d)
        print(self.global_attrs)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        p = Parser()
        p.parse_file(sys.argv[1])
    else:
        print('Usage:')
        print('    python {0} <filename>'.format(sys.argv[0]))
