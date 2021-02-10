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
        self.current_cell = 0
        self.nesting = 0
        self.stack = []

    def right(self):
        self.current_cell += 1
        if self.current_cell > CELLS_AMOUNT - 1:
            self.current_cell = 0

    def left(self):
        self.current_cell -= 1
        if self.current_cell < 0:
            self.current_cell = CELLS_AMOUNT - 1

    def add(self):
        self.cells[self.current_cell].value += 1

    def sub(self):
        self.cells[self.current_cell].value -= 1

    def print(self):
        print(chr(self.cells[self.current_cell].value), end='')

    def input(self):
        self.cells[self.current_cell].value = ord(input()[0])

    def begin_loop(self):
        self.stack.append(int(self.current_cell))

    def while_not_zero(self, code):
        '''
        :param code: the code inside the loop
        '''
        if self.additional_info:
            print(f'Loop start on {self.current_cell} cell')
        print(self.stack)
        checking_cell = self.stack.pop()
        while self.cells[checking_cell].value != 0:
            if self.additional_info:
                print(' ' * (self.nesting+1), end='')
                print(f'cell[{checking_cell}] == {self.cells[checking_cell].value} != 0')
            self.run(code)
        if self.additional_info:
            print(f'cell[{checking_cell}] == {self.cells[checking_cell].value}')
            print('End of loop - return back')

    def minify(self, code):
        return ''.join(ch for ch in code if ch in r'><+-.,[]')

    def run(self, code):
        if self.additional_info:
            print(' ' * (self.nesting + 1), end='')
            print(f'Executing: "{code}"')
        exec_code = self.minify(code)
        for i, ch in enumerate(exec_code):
            if ch == '<':
                # if not self.__is_run_restricted(): self.left()
                self.left()
            elif ch == '>':
                # if not self.__is_run_restricted(): self.right()
                self.right()
            elif ch == '+':
                # if not self.__is_run_restricted(): self.add()
                self.add()
            elif ch == '-':
                # if not self.__is_run_restricted(): self.sub()
                self.sub()
            elif ch == '.':
                # if not self.__is_run_restricted(): self.print()
                self.print()
            elif ch == ',':
                # if not self.__is_run_restricted(): self.input()
                self.input()
            elif ch == '[':
                self.nesting += 1
                code_block = ''
                block_start = i
                for j, loopch in enumerate(exec_code[block_start+1:]):
                    # import pdb; pdb.set_trace()
                    code_block += loopch
                    if loopch == ']':
                        self.nesting -= 1
                    elif loopch == '[':
                        self.nesting += 1
                    if self.nesting == 0:
                        # FIXME: find a way to drop last ']' more accurately
                        code_block = code_block[:-1]
                        break
            elif ch == ']':
                # if not self.__is_run_restricted(): self.while_not_zero(code_block)
                self.while_not_zero(code_block)

    def run_shell(self):
        print('Shell mode')
        while True:
            self.print_cells()
            query = input('(bf): ')
            self.run(query)

    def print_cells(self, wide=4):
        print('Cell '.rjust(8), end='')
        for num, _ in enumerate(self.cells, self.current_cell-wide):
            if num < 0:
                corrected_num = CELLS_AMOUNT + num
            elif num >= CELLS_AMOUNT:
                corrected_num = num - CELLS_AMOUNT
            else:
                corrected_num = num
            print(f'| {str(corrected_num).rjust(6)}', end='')
            if num == self.current_cell+wide:
                break
        print('\n' + '-' * 8 * (2 * (wide + 1)) + '-')
        print('Value '.rjust(8), end='')
        # for num, byte in enumerate(self.cells, self.current_cell-wide):
        #     print(f'| {str(byte.value).rjust(6)}', end='')
        #     if num == self.current_cell+wide:
        #         break
        # NOTE: i love enumerate, but commented loop is broken =(
        num = self.current_cell - wide - 1
        while num != self.current_cell+wide:
            num += 1
            if num < 0:
                num += CELLS_AMOUNT
            elif num >= CELLS_AMOUNT:
                num -= CELLS_AMOUNT
            print(f'| {str(self.cells[num].value).rjust(6)}', end='')

        print('\n' + ' ' * int(8 * (2 * (wide + 1)) / 2) + '     ^')

    def __is_run_restricted(self):
        return self.nesting != 0


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
            source_code = f.read()
            interp.run(source_code)
    else:
        try:
            interp.run_shell()
        except KeyboardInterrupt:
            print('\nExiting')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
