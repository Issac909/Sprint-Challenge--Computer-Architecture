import sys

# Operation Tables
binary_op = {
    0b00000001: 'HLT',
    0b10000010: 'LDI',
    0b01000111: 'PRN',
    0b01000101: 'PUSH',
    0b01000110: 'POP',
    0b01010000: 'CALL',
    0b00010001: 'RET',
    0b01010100: 'JMP',
    0b01010101: 'JEQ',
    0b01010110: 'JNE'
}

math_op = {
    "ADD": 0b10100000,
    "SUB": 0b10100001,
    "MUL": 0b10100010,
    'CMP': 0b10100111
}

# Global Constants
SP = 7  # Stack Pointer

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        # Registers
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.operand_a = None
        self.operand_b = None

        # Internal Registers
        self.PC = 0  # Program Counter
        self.MAR = None  # Memory Address Register
        self.MDR = None  # Memory Data Register

        self.FL = 0b00000000  # Flags

        # Branch Table
        self.instructions = {}
        self.instructions['HLT'] = self.halt
        self.instructions['LDI'] = self.ldi
        self.instructions['PRN'] = self.prn
        self.instructions['PUSH'] = self.push
        self.instructions['POP'] = self.pop
        self.instructions['CALL'] = self.call
        self.instructions['RET'] = self.ret
        self.instructions['JMP'] = self.jmp
        self.instructions['JEQ'] = self.jeq
        self.instructions['JNE'] = self.jne

    def call(self):
        """Calls a subroutine (function) at the address stored in the register."""
        self.reg[SP] -= 1

        # address of the instruction
        instruction_address = self.PC + 2

        # pushing the address of the instruction onto the stack
        self.ram[self.reg[SP]] = instruction_address

        # PC is set to the address stored in the register
        register = self.operand_a

        self.PC = self.reg[register]

    def ret(self):
        self.PC = self.ram[self.reg[SP]]

        self.reg[SP] += 1

    def jmp(self):
        """Jump to the address stored in the given register."""
        address = self.reg[self.operand_a]

        print("JUMPING")
        self.PC = address

    def jeq(self):
        """If `equal` flag is set (true), jump to the address stored in the given register."""
        address = self.reg[self.operand_a]

        if self.FL & 0b00000001 == 1:
            self.PC = address
        else:
            self.PC += 2

    def jne(self):
        """If `E` flag is clear (false, 0), jump to the address stored in the given register."""
        address = self.reg[self.operand_a]

        if self.FL & 0b00000001 == 0:
            self.PC = address
        else:
            self.PC += 2

    def halt(self):
        """Exit the current program"""
        sys.exit()

    def ldi(self):
        """Load value to register"""
        self.reg[self.operand_a] = self.operand_b

    def prn(self):
        """Print the value in a register"""
        print(self.reg[self.operand_a])

    def push(self):
        """Push the value in the given register to the top of the stack"""
        # decrement the SP
        global SP

        self.reg[SP] -= 1

        # copy the value in the given register to the address pointed to by SP
        value = self.reg[self.operand_a]

        self.ram[self.reg[SP]] = value

    def pop(self):
        """Pop the value at the top of the stack into the given register"""
        global SP

        value = self.ram[self.reg[SP]]

        # given register from argument
        register = self.operand_a

        # copying the value from memory to the given register
        self.reg[register] = value

        # increment SP
        self.reg[SP] += 1

    def ram_read(self, address):
        """Accepts an address to read and returns the value stored there"""
        self.MAR = address
        self.MDR = self.ram[address]
        return self.ram[address]

    def ram_write(self, value, address):
        """Accepts a value to write, and the address to write it to"""
        self.MAR = address
        self.MDR = value
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("ERROR: Must have file name")
            sys.exit(1)

        filename = sys.argv[1]

        try:
            address = 0
            # Open the file
            with open(filename) as program:
                # Read all the lines
                for instruction in program:
                    # Parse out comments
                    comment_split = instruction.strip().split("#")

                    # Cast the numbers from strings to ints
                    value = comment_split[0].strip()

                    # Ignore blank lines
                    if value == "":
                        continue

                    num = int(value, 2)
                    self.ram[address] = num
                    address += 1

        except FileNotFoundError:
            print("File not found")
            sys.exit(2)

    def ALU(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == math_op["ADD"]:
            print("ADDING")
            self.reg[reg_a] += self.reg[reg_b]

        elif op == math_op["SUB"]:
            print("SUBTRACTING")
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == math_op["MUL"]:
            print("MULTIPYING")
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == math_op["CMP"]:
            """Compare the values in two registers."""
            valueA = self.reg[self.operand_a]
            valueB = self.reg[self.operand_b]

            if valueA == valueB:
                self.FL = 0b00000001

            if valueA < valueB:
                self.FL = 0b00000100

            if valueA > valueB:
                self.FL = 0b00000010
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            # self.fl,
            # self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def move_PC(self, ireg):
        """Accepts an Instruction Register.\n
        Increments the PC by the number of arguments returned by the ireg."""

        # increment the PC only if the instruction doesn't set it
        if (ireg << 3) % 255 >> 7 != 1:
            self.PC += (ireg >> 6) + 1

    def run(self):
        """Run the CPU."""
        while True:
            # read the memory address that's stored in register PC,
            # store that result in ireg (Instruction Register).
            # This can just be a local variable
            ireg = self.ram_read(self.PC)

            # using ram_read(), read the bytes at PC+1 and PC+2 from RAM into variables
            self.operand_a = self.ram_read(self.PC + 1)
            self.operand_b = self.ram_read(self.PC + 2)

            # depending on the value of the oPCode, perform the actions needed for the instruction

            # if arithmathetic bit is on, run math operation
            if (ireg << 2) % 255 >> 7 == 1:
                self.ALU(ireg, self.operand_a, self.operand_b)
                self.move_PC(ireg)

            # else, run basic operations
            elif (ireg << 2) % 255 >> 7 == 0:
                self.instructions[binary_op[ireg]]()
                self.move_PC(ireg)

            # if instruction is unrecognized, exit
            else:
                print(f"Space dog did not understand that command: {ireg}")
                print(self.trace())
                sys.exit(1)