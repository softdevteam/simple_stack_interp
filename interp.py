import sys

def main(args):

    prog = [
        Op("PUSH", ["-1000000"]),
        Op("STORE", ["i"]),
        Op("LOAD", ["i"]),
        Op("PUSH", ["0"]),
        Op("CMP"),
        Op("CJMP", ["999"]),
        Op("LOAD", ["i"]),
        #Op("PRINT"),

        Op("PUSH", ["1"]),
        Op("ADD"),
        Op("STORE", ["i"]),
        Op("JMP", ["2"])
    ]
    interp = Interpreter(prog)
    interp.run()

    return 0

def target(*args):
    return main, None

def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JITPolicy()


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
        #print("debug (pc=%s): %s" % (self.pc, self.stack))
        pass

    def run(self):

        while True:

            if self.pc >= len(self.prog):
                break

            self.dump_stack()
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
    # make a program in-memory

    main(None)
