from ctypes import c_byte


CELLS_AMOUNT = 30000


class Interpreter:
    def __init__(self, additional_info=False):
        self.reset()
        self.additional_info = additional_info

    def reset(self):
        self.cells = [c_byte(0) for _ in range(CELLS_AMOUNT)]
        self.current_cell = 0
        self.nesting = 0

    def right(self):
        self.current_cell += 1
        if self.current_cell > CELLS_AMOUNT:
            self.current_cell = 0

    def left(self):
        self.current_cell -= 1
        if self.current_cell < 0:
            self.current_cell = CELLS_AMOUNT

    def add(self):
        self.cells[self.current_cell].value += 1

    def sub(self):
        self.cells[self.current_cell].value -= 1

    def print(self):
        print(chr(self.cells[self.current_cell].value), end='')

    def input(self):
        self.cells[self.current_cell].value = ord(input())

    def while_not_zero(self, code):
        '''
        :param code: the code inside the loop
        '''
        while self.cells[self.current_cell].value != 0:
            if self.additional_info:
                print(' ' * (self.nesting+1), end='')
                print(f'cell[{self.current_cell}] == {self.cells[self.current_cell].value} != 0')
            self.run(code)
        if self.additional_info:
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
                if not self.__is_run_restricted(): self.left()
            elif ch == '>':
                if not self.__is_run_restricted(): self.right()
            elif ch == '+':
                if not self.__is_run_restricted(): self.add()
            elif ch == '-':
                if not self.__is_run_restricted(): self.sub()
            elif ch == '.':
                if not self.__is_run_restricted(): self.print()
            elif ch == ',':
                if not self.__is_run_restricted(): self.input()
            elif ch == '[':
                self.nesting += 1
                code_block = ''
                block_start = i
                for j, loopch in enumerate(exec_code[block_start+1:]):
                    if loopch == ']':
                        self.nesting -= 1
                    elif loopch == '[':
                        self.nesting += 1
                    if self.nesting == 0:
                        # j is only relative end of block, so need to + block_start
                        block_end = block_start + j
                        code_block = exec_code[block_start + 1: block_end + 1]
                        break
            elif ch == ']':
                if not self.__is_run_restricted(): self.while_not_zero(code_block)
        # if self.current_cell == 7:
        #     import pdb
        #     pdb.set_trace()

    def print_cells(self):
        print('  Cell  |  Value  ')
        print('------------------')
        zeroes = 0
        for num, val in enumerate(self.cells):
            print(f'{str(num).rjust(8)}|{str(val).rjust(9)}', end='')
            if num == self.current_cell:
                print('  <--')
            else:
                print()
            if val == 0:
                zeroes += 1
            else:
                zeroes = 0
            if zeroes > 2:
                print('     .   .   .    ')
                break

    def __is_run_restricted(self):
        return self.nesting != 0


test_hello_world = "+++++++++++++++++++++++++++++++++++++++++++++"\
                   "+++++++++++++++++++++++++++.+++++++++++++++++"\
                   "++++++++++++.+++++++..+++.-------------------"\
                   "---------------------------------------------"\
                   "---------------.+++++++++++++++++++++++++++++"\
                   "++++++++++++++++++++++++++.++++++++++++++++++"\
                   "++++++.+++.------.--------.------------------"\
                   "---------------------------------------------"\
                   "----.-----------------------."
test_hello_world_opt = "++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++"\
                       ".>+.+++++++..+++.>++.<<+++++++++++++++.>.+++."\
                       "------.--------.>+.>."
test_wtf = ">++++[<++++++++>-]>++++++++[>++++<-]>>++>>>+>>>+<<<<<<<<<<"\
           "[-[->+<]>[-<+>>>.<<]>>>[[->++++++++[>++++<-]>.<<[->+<]+>[-"\
           ">++++++++++<<+>]>.[-]>]]+<<<[-[->+<]+>[-<+>>>-[->+<]++>[-<"\
           "->]<<<]<<<<]++++++++++.+++.[-]<]+++++"
test_pi_calculation = ">+++++++++++++++[<+>>>>>>>>++++++++++<<<<<<<-]>+++++[<+++++++++>-]+>>>>>>+[<<+++[>>[-<]<[>]<-]>>[>+>]<[<]>]>[[->>>>+<<<<]>>>+++>-]<[<<<<]<<<<<<<<+[->>>>>>>>>>>>[<+[->>>>+<<<<]>>>>>]<<<<[>>>>>[<<<<+>>>>-]<<<<<-[<<++++++++++>>-]>>>[<<[<+<<+>>>-]<[>+<-]<++<<+>>>>>>-]<<[-]<<-<[->>+<-[>>>]>[[<+>-]>+>>]<<<<<]>[-]>+<<<-[>>+<<-]<]<<<<+>>>>>>>>[-]>[<<<+>>>-]<<++++++++++<[->>+<-[>>>]>[[<+>-]>+>>]<<<<<]>[-]>+>[<<+<+>>>-]<<<<+<+>>[-[-[-[-[-[-[-[-[-<->[-<+<->>]]]]]]]]]]<[+++++[<<<++++++++<++++++++>>>>-]<<<<+<->>>>[>+<<<+++++++++<->>>-]<<<<<[>>+<<-]+<[->-<]>[>>.<<<<[+.[-]]>>-]>[>>.<<-]>[-]>[-]>>>[>>[<<<<<<<<+>>>>>>>>-]<<-]]>>[-]<<<[-]<<<<<<<<]++++++++++."

my_interp = Interpreter(additional_info=True)
# my_interp.run(test_wtf)
# my_interp.run(test_hello_world_opt)
my_interp.run(test_pi_calculation)
