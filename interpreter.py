import os
import sys
import pathlib
import argparse
from ctypes import c_ubyte


CELLS_AMOUNT = 128


class Interpreter:
    def __init__(self, additional_info=False):
        self.reset()
        self.additional_info = additional_info

    def reset(self):
        self.cells = [c_ubyte(0) for _ in range(CELLS_AMOUNT)]
        self.cell_pointer = 0
        self.inst_pointer = 0
        self.stack = []
        self.bindings = {
            '>': self.right,
            '<': self.left,
            '+': self.add,
            '-': self.sub,
            '.': self.print,
            ',': self.input,
            '[': self.begin_loop,
            ']': self.end_loop,
        }

    def right(self):
        self.cell_pointer += 1
        if self.cell_pointer > CELLS_AMOUNT - 1:
            self.cell_pointer = 0

    def left(self):
        self.cell_pointer -= 1
        if self.cell_pointer < 0:
            self.cell_pointer = CELLS_AMOUNT - 1

    def add(self):
        self.cells[self.cell_pointer].value += 1

    def sub(self):
        self.cells[self.cell_pointer].value -= 1

    def print(self):
        print(chr(self.cells[self.cell_pointer].value), end='')

    def input(self):
        self.cells[self.cell_pointer].value = ord(input()[0])

    def begin_loop(self):
        # end_loop_pos = self.stack[-1][1] if self.stack else None
        # loop_borders = (self.inst_pointer, end_loop_pos)
        # if self.cells[self.cell_pointer].value != 0:
        #     # TODO: try not to use stack check
        #     if loop_borders not in self.stack:
        #         self.stack.append(loop_borders)  # loop initializing
        # else:
        #     if self.stack:
        #         self.stack.pop()
        #     self.inst_pointer = end_loop_pos

        # FIXME: second nested loop is not created, cause we know end_loop_pos
        #  (can reproduce via .\interpreter.py -f .\samples\nested_loops_test.bf -d)
        end_loop_pos = self.stack[-1][1] if self.stack else None
        loop_borders = (self.inst_pointer, end_loop_pos)
        # on first entry of loop we dont know where is end of it
        if not end_loop_pos:
            self.stack.append(loop_borders)  # loop initializing
        # self.stack.append(loop_borders)  # loop initializing
        if self.cells[self.cell_pointer].value == 0:
            self.stack.pop()
            # self.inst_pointer = end_loop_pos + 1  # jumps incorrect
            self.inst_pointer = end_loop_pos

    def end_loop(self):
        loop_borders = (self.stack.pop()[0], self.inst_pointer)
        self.stack.append(loop_borders)
        # jump to begin of loop (-1, cause in run() loop will be +1)
        self.inst_pointer = self.stack[-1][0] - 1

    def minify(self, code):
        return ''.join(ch for ch in code if ch in r'><+-.,[]')

    def run(self, code):
        minified_code = self.minify(code)
        while self.inst_pointer < len(minified_code):
            if self.additional_info:
                print(f'inst_pointer: {self.inst_pointer}')
                print(f'cell_pointer: {self.cell_pointer}')
                print(f'value: {self.cells[self.cell_pointer].value}')
                print(f'operator: {minified_code[self.inst_pointer]}')
                print(f'callable_fn: {self.bindings[minified_code[self.inst_pointer]].__name__}()')
                print(f'stack: {self.stack}')
                print('----------------------------------------------')
            # if self.inst_pointer == 108:
            #     import pdb
            #     pdb.set_trace()
            self.bindings[minified_code[self.inst_pointer]]()
            self.inst_pointer += 1

    def run_shell(self):
        print('Shell mode')
        while True:
            self.print_cells()
            query = input('(bf): ')
            self.run(query)

    def print_cells(self, wide=4):
        print('Cell '.rjust(8), end='')
        for num, _ in enumerate(self.cells, self.cell_pointer - wide):
            if num < 0:
                corrected_num = CELLS_AMOUNT + num
            elif num >= CELLS_AMOUNT:
                corrected_num = num - CELLS_AMOUNT
            else:
                corrected_num = num
            print(f'| {str(corrected_num).rjust(6)}', end='')
            if num == self.cell_pointer+wide:
                break
        print('\n' + '-' * 8 * (2 * (wide + 1)) + '-')
        print('Value '.rjust(8), end='')
        # for num, byte in enumerate(self.cells, self.current_cell-wide):
        #     print(f'| {str(byte.value).rjust(6)}', end='')
        #     if num == self.current_cell+wide:
        #         break
        # NOTE: i love enumerate, but commented loop is broken =(
        num = self.cell_pointer - wide - 1
        while num != self.cell_pointer+wide:
            num += 1
            if num < 0:
                num += CELLS_AMOUNT
            elif num >= CELLS_AMOUNT:
                num -= CELLS_AMOUNT
            print(f'| {str(self.cells[num].value).rjust(6)}', end='')

        print('\n' + ' ' * int(8 * (2 * (wide + 1)) / 2) + '     ^')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='brainf_interpreter - just another interpreter of famous language')
    ap.add_argument('-f',
                    dest='source_file',
                    help='file with source code')
    ap.add_argument('-d',
                    action='store_true',
                    dest='debug_output',
                    default=False,
                    help='print debug info')
    args = ap.parse_args()

    interp = Interpreter(args.debug_output)

    if args.source_file:
        with open(pathlib.Path(args.source_file), 'r') as f:
            code = f.read()
            interp.run(code)
    else:
        try:
            interp.run_shell()
        except KeyboardInterrupt:
            print('\nExiting')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
