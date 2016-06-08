import sys

from rpython.rlib import jit
from rpython.rlib.streamio import open_file_as_stream

def target(*args):
    return main, None

def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()

def get_location(pc, interpreter):
    return "%d: %s" % (pc, interpreter.prog[pc])

jit_driver = jit.JitDriver (
    greens = ["pc", "self"],
    reds = [],
    get_printable_location = get_location
)

class Op(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class StringOp(Op):
    def __init__(self, name, args):
        Op.__init__(self, name)
        self.args = args

class IntOp(Op):
    def __init__(self, name, args):
        Op.__init__(self, name)
        self.args = int(args)

opcodes = {}
for i, cmd in enumerate("PUSH POP JMP CJMP CMP LOAD STORE HALT CHALT ADD SUB MUL DIV MOD PRINT".split()):
    globals()[cmd] = i
    opcodes[cmd] = i

class Interpreter(object):

    operations = [ADD, SUB, MUL, DIV, MOD]

    def __init__(self, prog):
        self.prog = prog
        self.pc = 0
        self.stack = []
        self.vars = []
        self.var_offsets = {}

    def dump_stack(self):
        print("debug (pc = %s): %s" % (self.pc, self.stack))

    def get_variable(self, name):
        off = self.get_variable_off(name)
        return self.vars[off]

    @jit.elidable_promote()
    def get_variable_off(self, name):
        return self.var_offsets[name]

    def set_variable(self, name, val):
        off = self.var_offsets.get(name, -1)
        if off == -1:
            self.var_offsets[name] = len(self.vars)
            self.vars.append(val)
            return
        self.vars[off] = val

    def run(self):
        while self.pc < len(self.prog):
            jit_driver.jit_merge_point(pc = self.pc, self = self)
            command = self.prog[self.pc]
            if command.name == PUSH:
                assert isinstance(command, IntOp)
                self.stack.append(command.args)
            elif command.name == POP:
                assert isinstance(command, Op)
                self.stack.pop()
            elif command.name == PRINT:
                assert isinstance(command, Op)
                print self.stack[-1]
            elif command.name == STORE:
                assert isinstance(command, StringOp)
                self.set_variable(command.args, self.stack.pop())
            elif command.name == LOAD:
                assert isinstance(command, StringOp)
                self.stack.append(self.get_variable(command.args))
            elif command.name == JMP:
                assert isinstance(command, IntOp)
                self.pc = command.args
                continue
            elif command.name == CJMP:
                assert isinstance(command, IntOp)
                x = self.stack.pop()
                if x == 1:
                    self.pc = command.args
                    continue
            elif command.name == HALT:
                break
            # conditional halt
            elif command.name == CHALT:
                if self.stack[-1] == 1:
                    break
            elif command.name == CMP:
                x, y = self.stack.pop(), self.stack.pop()
                if x == y:
                    self.stack.append(1)
                else:
                    self.stack.append(0)
            elif command.name in Interpreter.operations:
                x, y = self.stack.pop(), self.stack.pop()
                if command.name == ADD:
                    self.stack.append(x + y)
                elif command.name == SUB:
                    self.stack.append(x - y)
                elif command.name == MUL:
                    self.stack.append(x * y)
                elif command.name == DIV:
                    #error
                    if y == 0:
                        pass
                    else :
                        self.stack.append(x // y)
                elif command.name == MOD:
                    #error
                    if y == 0:
                        pass
                    else :
                        self.stack.append(x % y)
            else:
                print("Unhandled bytecode: %s" % command)
                return 1
            self.pc += 1
        return 0

def main(args):
    prog = []
    try:
        program_file = open_file_as_stream(args[1])
        lines = program_file.readall().split("\n")
        program_file.close()
        for line in lines:
            line = line.strip()
            # some lines are 'commented' with '#'
            if not line.startswith("#") and line:
                command = line.split(" ")
                if command[0] == "LOAD" or command[0] == "STORE":
                    prog.append(StringOp(opcodes[command[0]], command[1]))
                elif command[0] == "PUSH" or command[0] == "JMP" or \
                    command[0] == "CJMP":
                    prog.append(IntOp(opcodes[command[0]], command[1]))
                else:
                    prog.append(Op(opcodes[command[0]]))
    except IndexError as e:
        print "[ERROR] Need an argument"
    except IOError as e:
        print "[ERROR] File not found: %s" % args[1]
    else:
        interp = Interpreter(prog)
        interp.run()
    return 0

if __name__ == "__main__":
    main(sys.argv)
