import sys
import csv

class VirtualMachine:
    def __init__(self, memory_size=10000, num_registers=1000):
        self.memory = [0] * memory_size
        self.registers = [0] * num_registers
        self.instruction_pointer = 0

    def rotate_left_32bit(self, value, shift):
        shift = shift % 32
        value &= 0xFFFFFFFF
        return ((value << shift) & 0xFFFFFFFF) | (value >> (32 - shift))

    def execute_instructions(self, instructions):
        for idx, instr in enumerate(instructions):
            val = int.from_bytes(instr, 'big')
            A = (val >> 0) & 0xF

            if A == 10:
                # LOAD_CONST
                B = (val >> 4) & 0x3F
                C = (val >> 10) & 0x3FFF
                self.registers[B] = C
                # Debug
                print(f"Instr {idx}: LOAD_CONST -> R[{B}] = {C}")

            elif A == 6:
                # MEM_READ
                B = (val >> 4) & 0x3F
                C = (val >> 10) & 0x3F
                D = (val >> 16) & 0x7FFF
                addr = self.registers[C] + D
                if addr < 0 or addr >= len(self.memory):
                    raise IndexError(f"Instr {idx}: Memory read out of bounds: {addr}")
                self.registers[B] = self.memory[addr]
                # Debug
                print(f"Instr {idx}: MEM_READ -> R[{B}] = MEM[{addr}] ({self.memory[addr]})")

            elif A == 4:
                # MEM_WRITE
                B = (val >> 4) & 0x3F
                C = (val >> 10) & 0x3F
                D = (val >> 16) & 0x7FFF
                addr = self.registers[B] + D
                if addr < 0 or addr >= len(self.memory):
                    raise IndexError(f"Instr {idx}: Memory write out of bounds: {addr}")
                self.memory[addr] = self.registers[C]
                # Debug
                print(f"Instr {idx}: MEM_WRITE -> MEM[{addr}] = R[{C}] ({self.registers[C]})")

            elif A == 13:
                # ROTATE_LEFT
                B = (val >> 4) & 0x3F
                C = (val >> 10) & 0x3F
                D = (val >> 16) & 0x7FFFFFFF
                if D < 0 or D >= len(self.memory):
                    raise IndexError(f"Instr {idx}: Invalid memory address for shift: {D}")
                shift = self.memory[D]
                val_to_shift = self.registers[C]
                rotated = self.rotate_left_32bit(val_to_shift, shift)
                addr = self.registers[B]
                if addr < 0 or addr >= len(self.memory):
                    raise IndexError(f"Instr {idx}: Memory write out of bounds for ROTATE_LEFT: {addr}")
                self.memory[addr] = rotated
                # Debug
                print(f"Instr {idx}: ROTATE_LEFT -> MEM[{addr}] = rotate_left(R[{C}]={val_to_shift}, {shift} bits) = {rotated}")

            else:
                raise ValueError(f"Instr {idx}: Unknown opcode A={A}")

def load_binary(bin_path):
    instructions = []
    with open(bin_path, 'rb') as f:
        while True:
            chunk = f.read(7)
            if len(chunk) < 7:
                break
            instructions.append(chunk)
    return instructions

def save_memory_to_csv(file_path, memory, start, end):
    with open(file_path, 'w', newline='', encoding='utf-8') as fout:
        writer = csv.writer(fout)
        writer.writerow(["Address", "Value"])
        for i in range(start, end+1):
            writer.writerow([i, memory[i]])

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Использование: python interpreter.py <binary_file> <result_csv> <start> <end>")
        sys.exit(1)

    binary_file = sys.argv[1]
    result_csv = sys.argv[2]
    start = int(sys.argv[3])
    end = int(sys.argv[4])

    vm = VirtualMachine()
    instructions = load_binary(binary_file)
    vm.execute_instructions(instructions)
    save_memory_to_csv(result_csv, vm.memory, start, end)
