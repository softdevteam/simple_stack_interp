import interp

def test_push001():
	prog = []
	command = ["PUSH", "13"]
	push_command = interp.IntOp(interp.opcodes[command[0]], command[1])
	prog.append(push_command)
	interpreter = interp.Interpreter(prog)
	interpreter.run()
	assert interpreter.stack[-1] == 13

def test_pop001():
	prog = [ interp.IntOp(interp.opcodes["PUSH"], "13"),
			interp.IntOp(interp.opcodes["PUSH"], "25"),
			interp.IntOp(interp.opcodes["PUSH"], "30"),
			interp.Op(interp.opcodes["POP"]) ]

	interpreter = interp.Interpreter(prog)
	interpreter.run()
	assert interpreter.stack[-1] == 25
	assert len(interpreter.stack) == 2

def test_add001():
	prog = [ interp.IntOp(interp.opcodes["PUSH"], "13"),
			interp.IntOp(interp.opcodes["PUSH"], "25"),
			interp.IntOp(interp.opcodes["PUSH"], "30"),
			interp.Op(interp.opcodes["ADD"]) ]

	interpreter = interp.Interpreter(prog)
	interpreter.run()
	assert interpreter.stack[-1] == 55
	assert len(interpreter.stack) == 2
