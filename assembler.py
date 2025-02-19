import sys
import re

register_codes = {
    "zero": "00000",
    "ra": "00001",
    "sp": "00010", 
    "gp": "00011", 
    "tp": "00100",
    "t0": "00101", 
    "t1": "00110", 
    "t2": "00111", 
    "s0": "01000", 
    "fp": "01000",
    "s1": "01001",
    "a0": "01010",
    "a1": "01011",
    "a2": "01100", 
    "a3": "01101",
    "a4": "01110",
    "a5": "01111",
    "a6": "10000", 
    "a7": "10001", 
    "s2": "10010",
    "s3": "10011",
    "s4": "10100",
    "s5": "10101",
    "s6": "10110", 
    "s7": "10111",
    "s8": "11000",
    "s9": "11001",
    "s10": "11010", 
    "s11": "11011",
    "t3": "11100",
    "t4": "11101", 
    "t5": "11110", 
    "t6": "11111"
}
op = {
    "addi": "0010011",
    "add": "0110011", 
    "sub": "0110011", 
    "slt": "0110011",
    "srl": "0110011",
    "or": "0110011", 
    "xor": "0110011", 
    "lw": "0000011", 
    "jalr": "1100111", 
    "sw": "0100011", 
    "beq": "1100011", 
    "bne": "1100011", 
    "blt": "1100011", 
    "bge": "1100011", 
    "bltu": "1100011",
    "jal": "1101111", 
    "halt": "1111100"
}

func3_codes = {"add": "000",
               "sub": "000",
               "slt": "010", 
               "srl": "101", 
               "or": "110", 
               "xor": "100", 
                "addi": "000",
                "beq": "000",
                "bne": "001",
                "blt": "100",
                "bge": "101",
                "bltu": "110",
                "lw": "010", 
                "sw": "010", 
                "jalr": "000"}

func7_codes = {"add": "0000000",
               "sub": "0100000", 
               "slt": "0000000", 
               "srl": "0000000", 
               "or": "0000000",
               "xor": "0000000"}

def imm_to_bin(value, bits):
    return format(value & ((1 << bits) - 1), f'0{bits}b')

def validate_register(reg_name, line_num):
    reg_name = reg_name.strip().lower()
    if reg_name not in register_codes:
        sys.exit(f"Error: Register '{reg_name}' not found at line {line_num + 1}")
    return register_codes[reg_name]

def collect_labels(program):
    labels = {}
    instruction_count = 0
    for line_num, line in enumerate(program):
        parts = line.split()
        if parts and parts[0].endswith(":"):
            label_name = parts[0][:-1]
            if label_name in labels:
                sys.exit(f"Error: Duplicate label '{label_name}' at line {line_num + 1}")
            labels[label_name] = instruction_count * 4
        else:
            instruction_count += 1
    return labels
def convert_to_binary(inst, line_num, labels):
    parts = inst.replace(",", " ").split()
    parts = [p.strip() for p in parts if p.strip()]

    if len(parts) == 0 or parts[0].endswith(":"):
        return None

    opcode = parts[0]

    if opcode == "jal":
        imm = imm_to_bin(labels.get(parts[2], int(parts[2])), 20)
        return imm + validate_register(parts[1], line_num) + op["jal"]

    if opcode in func7_codes:
        return func7_codes[opcode] + validate_register(parts[3], line_num) + validate_register(parts[2], line_num) + func3_codes[opcode] + validate_register(parts[1], line_num) + op[opcode]
    
    if opcode in func3_codes:
        if "(" in parts[2]:
            match = re.match(r"(-?\d+)\((\w+)\)", parts[2])  
            if not match:
                sys.exit(f"Error: Invalid memory format '{parts[2]}' at line {line_num + 1}")
            imm, rs1 = imm_to_bin(int(match.group(1)), 12), validate_register(match.group(2), line_num)
        else:
            imm, rs1 = imm_to_bin(int(parts[3]), 12), validate_register(parts[2], line_num)
        return imm + rs1 + func3_codes[opcode] + validate_register(parts[1], line_num) + op[opcode]

    if opcode in ["beq", "bne", "blt", "bge", "bltu"]:
        imm = imm_to_bin(labels.get(parts[3], int(parts[3])), 12)
        return imm[:7] + validate_register(parts[2], line_num) + validate_register(parts[1], line_num) + func3_codes[opcode] + imm[7:] + op[opcode]
    
    if opcode == "halt":
        return "00000000000000000000000001100011"
    
    sys.exit(f"Error: Unknown instruction '{opcode}' at line {line_num + 1}")

