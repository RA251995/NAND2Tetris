"""
VM Translator for HACK machine.
Convert VM code (.vm) to HACK assembly (.asm)
"""

import argparse
import logging
import os


class C_TYPE:
    C_ARITHMETIC = "C_ARITHMETIC"
    C_PUSH = "push"
    C_POP = "pop"
    C_LABEL = "label"
    C_GOTO = "goto"
    C_IF = "if-goto"
    C_FUNCTION = "function"
    C_RETURN = "return"
    C_CALL = "call"


class Parser:
    """
    Reads and parses VM file.

    Handles the parsing of a single .vm file.
    Reads a VM command, parses the command into its lexical components,
    and provides convenient access to these components.
    Ignore whitespace and comments
    """

    def __init__(self, filename: str):
        """
        Opens the input (source VM code) file
        """
        logging.debug(f"Reading `{filename}` file")
        with open(filename, "r") as file:
            self.lines = file.readlines()
        self.line_offset = 0  # Offset to next line to parse
        self.current_cmd = None
        self.current_cmd_type = None

    def hasMoreLines(self) -> bool:
        """
        Checks if there is more work to do
        """
        ret_val = False
        # Move line offset to next command
        start_offset = self.line_offset
        for line in self.lines[start_offset:]:
            # logging.debug(f"Reading line {self.line_offset}: `{line}`")
            # Remove comments and
            # strip leading and trailing whitespaces
            line = line.split("//")[0].strip()
            self.line_offset += 1
            if len(line) > 0:  # If not empty line or comment line
                ret_val = True
                break  # Exit loop on command
        return ret_val

    def advance(self) -> str:
        """
        Gets the next command and makes it the current instruction
        """
        line = self.lines[self.line_offset - 1]
        self.current_cmd = line.split("//")[0].strip()
        logging.debug(
            f"Processing {self.line_offset - 1}: `{self.current_cmd}`")

    def commandType(self) -> str:
        """
        Returns the type of the current command.
        C_ARITHMETIC: if the current command is an arithmentic-logical command;
        C_PUSH / C_POP: if the current command is one of push / pop command types;
        C_LABEL / C_GOTO / C_IF: if the current command is one of branching commands
        """
        cmd = self.current_cmd
        self.current_cmd_type = None
        first_word = cmd.split()[0]
        if first_word in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
            self.current_cmd_type = C_TYPE.C_ARITHMETIC
        elif first_word == "pop":
            self.current_cmd_type = C_TYPE.C_POP
        elif first_word == "push":
            self.current_cmd_type = C_TYPE.C_PUSH
        elif first_word == "label":
            self.current_cmd_type = C_TYPE.C_LABEL
        elif first_word == "goto":
            self.current_cmd_type = C_TYPE.C_GOTO
        elif first_word == "if-goto":
            self.current_cmd_type = C_TYPE.C_IF
        else:
            raise RuntimeError(f"Unknown command type: `{self.current_cmd}`")
        logging.debug(f"Command type: `{self.current_cmd_type}`")
        return self.current_cmd_type

    def arg1(self) -> str:
        """
        Returns the first argument of the current command.
        In the case of C_ARITHMETIC, the command itself is returned
        """
        first_arg = None
        if self.current_cmd_type in C_TYPE.C_ARITHMETIC:
            first_arg = self.current_cmd.split()[0]
        elif self.current_cmd_type in [C_TYPE.C_PUSH, C_TYPE.C_POP, C_TYPE.C_LABEL, C_TYPE.C_GOTO, C_TYPE.C_IF]:
            # `segment` is the first argument for push and pop and
            # `label` is the first argument for branching commands
            first_arg = self.current_cmd.split()[1]
        logging.debug(f"First argument: `{first_arg}`")
        return first_arg

    def arg2(self) -> int:
        """
        Returns the second argument of the current command.
        Called only if the current command is C_PUSH, C_POP
        """
        if self.current_cmd_type not in [C_TYPE.C_PUSH, C_TYPE.C_POP]:
            raise RuntimeError(f"arg2 not valid for `{self.current_cmd}`")

        # `index` is the second argument for push and pop
        second_arg = int(self.current_cmd.split()[2])
        logging.debug(f"Second argument: `{second_arg}`")
        return second_arg


class CodeWriter:
    """
    Generates the assembly code that realizes the parsed command
    """

    def __init__(self, filename: str):
        """
        Opens the output (destination ASM code) file
        """
        logging.debug(f"Opening `{filename}` file")
        self.file = open(filename, "w")
        self.vm_filename = os.path.splitext(os.path.basename(filename))[0]
        self.label_idx = 0

    def close(self):
        """
        Closes the output (destination ASM code) file
        """
        logging.debug(f"Closing output file")
        self.file.close()

    def writeArithmetic(self, command: str):
        """
        Writes to the output file the assembly code that implements
        the given arithmetic-logical command
        """
        self.file.write(f"// {command}\n")
        if command in ["add", "sub", "eq", "gt", "lt", "and", "or"]:
            self.file.write("@SP\n")
            self.file.write("M=M-1\n")
            self.file.write("A=M\n")
            self.file.write("D=M\n")
            self.file.write("@SP\n")
            self.file.write("M=M-1\n")
            self.file.write("A=M\n")
            if command == "add":
                self.file.write("M=D+M\n")
            elif command == "sub":
                self.file.write("M=M-D\n")
            elif command == "and":
                self.file.write("M=D&M\n")
            elif command == "or":
                self.file.write("M=D|M\n")
            elif command in ["eq", "gt", "lt"]:
                self.file.write("D=M-D\n")
                self.file.write(f"@SET_TRUE.{self.label_idx}\n")
                if command == "eq":
                    self.file.write("D;JEQ\n")
                elif command == "gt":
                    self.file.write("D;JGT\n")
                elif command == "lt":
                    self.file.write("D;JLT\n")
                self.file.write("D=0\n")
                self.file.write(f"@PUSH_RES.{self.label_idx}\n")
                self.file.write("0;JMP\n")
                self.file.write(f"(SET_TRUE.{self.label_idx})\n")
                self.file.write("D=-1\n")
                self.file.write(f"(PUSH_RES.{self.label_idx})\n")
                self.file.write("@SP\n")
                self.file.write("A=M\n")
                self.file.write("M=D\n")
                self.label_idx += 1
            self.file.write("@SP\n")
            self.file.write("M=M+1\n")
        elif command in ["neg", "not"]:
            self.file.write("@SP\n")
            self.file.write("A=M-1\n")
            if command == "neg":
                self.file.write("M=-M\n")
            elif command == "not":
                self.file.write("M=!M\n")
        else:
            raise RuntimeError(f"Unknown command: {command}")

    def writePushPop(self, command: str, segment: str, index: int):
        """
        Writes to the output file the assembly code that implements
        the given push / pop command

        Args:
            command: C_PUSH / C_POP
        """
        self.file.write(f"// {command} {segment} {index}\n")
        if command == C_TYPE.C_PUSH:
            if segment in ["constant", "static", "pointer"]:
                if segment == "constant":
                    self.file.write(f"@{index}\n")
                    self.file.write("D=A\n")
                elif segment == "static":
                    self.file.write(f"@{self.vm_filename}.{index}\n")
                    self.file.write("D=M\n")
                elif segment == "pointer":
                    if index == 0:
                        BASE_ADDR_SYMBOL = "THIS"
                    elif index == 1:
                        BASE_ADDR_SYMBOL = "THAT"
                    else:
                        raise RuntimeError(f"Invalid index in command: `{
                                           command} {segment} {index}`")
                    self.file.write(f"@{BASE_ADDR_SYMBOL}\n")
                    self.file.write("D=M\n")
                self.file.write("@SP\n")
                self.file.write("A=M\n")
                self.file.write("M=D\n")
                self.file.write("@SP\n")
                self.file.write("M=M+1\n")
            elif segment in ["local", "argument", "this", "that", "temp"]:
                if segment in ["local", "argument", "this", "that"]:
                    if segment == "local":
                        BASE_ADDR_SYMBOL = "LCL"
                    elif segment == "argument":
                        BASE_ADDR_SYMBOL = "ARG"
                    elif segment == "this":
                        BASE_ADDR_SYMBOL = "THIS"
                    if segment == "that":
                        BASE_ADDR_SYMBOL = "THAT"
                    self.file.write(f"@{BASE_ADDR_SYMBOL}\n")
                    self.file.write("D=M\n")
                elif segment == "temp":
                    self.file.write("@5\n")
                    self.file.write("D=A\n")
                self.file.write(f"@{index}\n")
                self.file.write("A=D+A\n")
                self.file.write("D=M\n")
                self.file.write("@SP\n")
                self.file.write("A=M\n")
                self.file.write("M=D\n")
                self.file.write("@SP\n")
                self.file.write("M=M+1\n")
            else:
                raise RuntimeError(f"Invalid segment in command: `{
                                   command} {segment} {index}`")
        elif command == C_TYPE.C_POP:
            if segment in ["local", "argument", "this", "that", "temp"]:
                if segment in ["local", "argument", "this", "that"]:
                    if segment == "local":
                        BASE_ADDR_SYMBOL = "LCL"
                    elif segment == "argument":
                        BASE_ADDR_SYMBOL = "ARG"
                    elif segment == "this":
                        BASE_ADDR_SYMBOL = "THIS"
                    if segment == "that":
                        BASE_ADDR_SYMBOL = "THAT"
                    self.file.write(f"@{BASE_ADDR_SYMBOL}\n")
                    self.file.write("D=M\n")
                elif segment == "temp":
                    self.file.write("@5\n")
                    self.file.write("D=A\n")
                self.file.write(f"@{index}\n")
                self.file.write("D=D+A\n")
                self.file.write("@R13\n")
                self.file.write("M=D\n")
                self.file.write("@SP\n")
                self.file.write("M=M-1\n")
                self.file.write("A=M\n")
                self.file.write("D=M\n")
                self.file.write("@R13\n")
                self.file.write("A=M\n")
                self.file.write("M=D\n")
            elif segment in ["static", "pointer"]:
                self.file.write("@SP\n")
                self.file.write("AM=M-1\n")
                self.file.write("D=M\n")
                if segment == "static":
                    self.file.write(f"@{self.vm_filename}.{index}\n")
                elif segment == "pointer":
                    if index == 0:
                        BASE_ADDR_SYMBOL = "THIS"
                    elif index == 1:
                        BASE_ADDR_SYMBOL = "THAT"
                    else:
                        raise RuntimeError(f"Invalid index in command: `{
                                           command} {segment} {index}`")
                    self.file.write(f"@{BASE_ADDR_SYMBOL}\n")
                self.file.write("M=D\n")
            else:
                raise RuntimeError(f"Invalid segment in command: `{
                                   command} {segment} {index}`")

    def writeLabel(self, label: str):
        """
        Writes assembly code that effects the `label` command
        """
        self.file.write(f"// label {label}\n")
        self.file.write(f"({label})\n")

    def writeGoto(self, label: str):
        """
        Write assembly code that effects the `goto` command
        """
        self.file.write(f"// goto {label}\n")
        self.file.write(f"@{label}\n")
        self.file.write(f"0;JMP\n")

    def writeIf(self, label: str):
        """
        Write assembly code that effects the `if-goto` command
        """
        self.file.write(f"// if-goto {label}\n")
        self.file.write("@SP\n")
        self.file.write("AM=M-1\n")
        self.file.write("D=M\n")
        self.file.write(f"@{label}\n")
        self.file.write(f"D;JNE\n")

    def writeFunction(self, functionName: str, nArgs: int):
        """
        Write assembly code that effects the `call` command
        """
        self.file.write(f"// function {functionName} {nArgs}\n")

    def writeReturn(self):
        """
        Write assembly code that effects the `return` command
        """
        self.file.write(f"// return\n")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(module)s : %(funcName)s | %(message)s",
    )

    # Parse argument
    parser = argparse.ArgumentParser(
        description="VM Translator for HACK machine (.vm -> .asm)"
    )
    parser.add_argument("vm_filename", type=str, help="VM file to translate")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        print("Enable debug")

    in_filename = args.vm_filename
    base_filename, _ = os.path.splitext(in_filename)
    out_filename = f"{base_filename}.asm"

    parser = Parser(in_filename)
    writer = CodeWriter(out_filename)

    while parser.hasMoreLines():
        parser.advance()
        cmd_type = parser.commandType()
        first_arg = parser.arg1()
        if cmd_type in [C_TYPE.C_PUSH, C_TYPE.C_POP]:
            index = parser.arg2()
            writer.writePushPop(cmd_type, first_arg, index)
        elif cmd_type == C_TYPE.C_ARITHMETIC:
            writer.writeArithmetic(first_arg)
        elif cmd_type == C_TYPE.C_LABEL:
            writer.writeLabel(first_arg)
        elif cmd_type == C_TYPE.C_GOTO:
            writer.writeGoto(first_arg)
        elif cmd_type == C_TYPE.C_IF:
            writer.writeIf(first_arg)
        else:
            raise RuntimeError(f"Unknown command type: {cmd_type}")

    writer.close()
