import sys
from rpython.rlib import jit

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

    def __init__(self, name, args = None):
        self.name = name
        if args is not None:
            self.args = args
        else:
            self.args = []

    def __str__(self):
        return "%s %s" % (self.name, self.args)

class Interpreter(object):

    def __init__(self, prog):
        self.prog = prog
        self.pc = 0
        self.stack = []
        self.vars = {}  # name -> val

    def dump_stack(self):
        print("debug (pc=%s): %s" % (self.pc, self.stack))

    def run(self):

        while True:

            jit_driver.jit_merge_point(pc = self.pc, self = self)

            if self.pc >= len(self.prog):
                break

            #self.dump_stack()
            command = self.prog[self.pc]

            #print command

            if command.name == "PUSH":
                self.stack.append(int(command.args[0]))

            elif command.name == "MUL":
                x = self.stack.pop()
                y = self.stack.pop()
                self.stack.append(x * y)

            elif command.name == "ADD":
                x = self.stack.pop()
                y = self.stack.pop()
                self.stack.append(x + y)

            elif command.name == "PRINT":
                print self.stack[-1]

            elif command.name == "CMP":
                x = self.stack.pop()
                y = self.stack.pop()

                if x == y:
                    self.stack.append(1)
                else:
                    self.stack.append(0)

            elif command.name == "CJMP":
                x = self.stack.pop()

                if x == 1:
                    self.pc = int(command.args[0])
                    continue

            elif command.name == "STORE":
                self.vars[command.args[0]] = self.stack.pop()

            elif command.name == "LOAD":
                self.stack.append(self.vars[command.args[0]])

            elif command.name == "JMP":
                self.pc = int(command.args[0])
                continue

            else:
                print("Unhandled bytecode: %s" % command)
                return 0

            self.pc += 1

        return 0

if __name__ == "__main__":
    main(sys.argv)

def main(args):
    prog = []
    try:
        with open(args[1], "r") as program_file:
            while True:
                line = program_file.readline().strip()
                if not line:
                    break
                # some lines are 'commented' with '#'
                if not line.startswith("#"):
                    command = line.split(" ")
                    prog.append(Op(command[0], len(command) > 1 and [command[1]] or None))
    except IndexError as e:
        print "[ERROR] Need an argument"
    except IOError as e:
        print "[ERROR] File not found: %s" % args[1]
    else:
        interp = Interpreter(prog)
        interp.run()

    return 0
