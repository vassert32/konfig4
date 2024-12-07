import sys
import csv

# Определение опкодов
OPCODES = {
    "LOAD_CONST": 10,
    "MEM_READ": 6,
    "MEM_WRITE": 4,
    "ROTATE_LEFT": 13
}

def assemble_load_const(A, B, C):
    # Формат: A(4 бит), B(6 бит), C(14 бит)
    val = (A & 0xF) | ((B & 0x3F) << 4) | ((C & 0x3FFF) << 10)
    return val.to_bytes(7, byteorder='big')

def assemble_mem_read(A, B, C, D):
    # Формат: A(4 бит), B(6 бит), C(6 бит), D(15 бит)
    val = (A & 0xF) | ((B & 0x3F) << 4) | ((C & 0x3F) << 10) | ((D & 0x7FFF) << 16)
    return val.to_bytes(7, byteorder='big')

def assemble_mem_write(A, B, C, D):
    # Формат: A(4 бит), B(6 бит), C(6 бит), D(15 бит)
    val = (A & 0xF) | ((B & 0x3F) << 4) | ((C & 0x3F) << 10) | ((D & 0x7FFF) << 16)
    return val.to_bytes(7, byteorder='big')

def assemble_rotate_left(A, B, C, D):

    val = (A & 0xF) | ((B & 0x3F) << 4) | ((C & 0x3F) << 10) | ((D & 0x7FFFFFFF) << 16)
    return val.to_bytes(7, byteorder='big')

def parse_line(line):
    # Удаление комментариев
    if '#' in line:
        line = line[:line.index('#')]
    parts = line.strip().split()
    if not parts:
        return None

    cmd = parts[0]
    if cmd not in OPCODES:
        raise ValueError(f"Неизвестная команда: {cmd}")

    args = {}
    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=')
            args[key] = int(value)

    A = args.get('A', OPCODES.get(cmd))
    if A is None:
        raise ValueError(f"Неизвестная команда или не указан A: {cmd}")
    B = args.get('B', 0)
    C = args.get('C', 0)
    D = args.get('D', 0)

    if cmd == "LOAD_CONST":
        binary = assemble_load_const(A, B, C)
    elif cmd == "MEM_READ":
        binary = assemble_mem_read(A, B, C, D)
    elif cmd == "MEM_WRITE":
        binary = assemble_mem_write(A, B, C, D)
    elif cmd == "ROTATE_LEFT":
        binary = assemble_rotate_left(A, B, C, D)
    else:
        raise ValueError(f"Unsupported command: {cmd}")

    hexbytes = binary.hex()
    return (cmd, A, B, C, D, hexbytes, binary)

def assemble(input_path, output_bin_path, output_log_path):
    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_bin_path, 'wb') as fout, \
         open(output_log_path, 'w', newline='', encoding='utf-8') as flog:

        writer = csv.writer(flog)
        writer.writerow(["Command", "A", "B", "C", "D", "HexBytes"])

        for line in fin:
            parsed = parse_line(line)
            if parsed:
                cmd, A, B, C, D, hexbytes, binary = parsed
                fout.write(binary)
                writer.writerow([cmd, A, B, C, D, hexbytes])

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Использование: python assembler.py <input_file> <output_bin_file> <log_csv_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_bin = sys.argv[2]
    log_file = sys.argv[3]

    assemble(input_file, output_bin, log_file)
