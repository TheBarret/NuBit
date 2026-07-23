// nb-asm.c - NuBit Assembler (COMPLETE FIXED)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdint.h>
#include <stdbool.h>

// ============================================================
// 1. OPCODE TABLE
// ============================================================

typedef struct {
    const char* name;
    uint8_t opcode;
    int operands;
    int format;            // 0=3reg, 1=2reg, 2=reg+imm4, 3=0reg
} Instruction;

Instruction instructions[] = {
    {"ADD",   0x0, 3, 0},
    {"SUB",   0x1, 3, 0},
    {"AND",   0x2, 3, 0},
    {"OR",    0x3, 3, 0},
    {"XOR",   0x4, 3, 0},
    {"MUL",   0x5, 3, 0},
    {"CMP",   0x6, 2, 1},
    {"LDI",   0x7, 2, 2},
    {"LDI16", 0x8, 1, 3},
    {"LD",    0x9, 2, 1},
    {"ST",    0xA, 2, 1},
    {"JMP",   0xB, 1, 3},
    {"JZ",    0xC, 1, 3},
    {"JNZ",   0xD, 1, 3},
    {"SYS",   0xE, 3, 0},
    {"HALT",  0xF, 0, 3}
};

int num_instructions = sizeof(instructions) / sizeof(instructions[0]);

// ============================================================
// 2. SYMBOL TABLE
// ============================================================

typedef struct {
    char name[64];
    uint16_t address;
} Symbol;

Symbol symbols[256];
int num_symbols = 0;

void add_symbol(const char* name, uint16_t address) {
    strcpy(symbols[num_symbols].name, name);
    symbols[num_symbols].address = address;
    num_symbols++;
}

int find_symbol(const char* name) {
    for (int i = 0; i < num_symbols; i++) {
        if (strcmp(symbols[i].name, name) == 0) {
            return symbols[i].address;
        }
    }
    return -1;
}

// ============================================================
// 3. OUTPUT BUFFER
// ============================================================

uint16_t output[65536];
int output_count = 0;

void emit(uint16_t word) {
    output[output_count++] = word;
}

// ============================================================
// 4. PARSING HELPERS
// ============================================================

char* trim(char* str) {
    while (isspace((unsigned char)*str)) str++;
    if (*str == 0) return str;
    char* end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    end[1] = '\0';
    return str;
}

int parse_register(const char* token) {
    if (token[0] != 'R' && token[0] != 'r') return -1;
    int reg = atoi(token + 1);
    if (reg < 0 || reg > 15) return -1;
    return reg;
}

uint16_t parse_number(const char* token) {
    if (strlen(token) > 2 && token[0] == '0' && token[1] == 'x') {
        return (uint16_t)strtol(token, NULL, 16);
    }
    return (uint16_t)atoi(token);
}

// ============================================================
// 5. TWO-STAGE ASSEMBLER
// ============================================================

// Stage 1: Parse labels and collect symbols
void stage1(FILE* file) {
    fseek(file, 0, SEEK_SET);
    char line[256];
    uint16_t address = 0;

    while (fgets(line, sizeof(line), file)) {
        char* trimmed = trim(line);
        if (*trimmed == 0 || *trimmed == ';') continue;

        // Check for label
        char* colon = strchr(trimmed, ':');
        if (colon) {
            *colon = '\0';
            char* label = trim(trimmed);
            if (*label) {
                add_symbol(label, address);
            }
            char* rest = colon + 1;
            char* rest_trimmed = trim(rest);
            if (*rest_trimmed == 0 || *rest_trimmed == ';') continue;
        }

        // Count words for address tracking
        char* token = strtok(trimmed, " ,\t");
        if (!token) continue;

        if (strcmp(token, ".word") == 0 || strcmp(token, ".d") == 0) {
            address += 1;
        } else if (strcmp(token, ".cstr") == 0 || strcmp(token, ".ascii") == 0) {
            char* rest = trimmed + strlen(token);
            char* start = strchr(rest, '"');
            if (start) {
                char* end = strchr(start + 1, '"');
                if (end) {
                    int len = end - start - 1;
                    address += len + 1;
                }
            }
        } else {
            for (int i = 0; i < num_instructions; i++) {
                if (strcasecmp(token, instructions[i].name) == 0) {
                    address += 1;
                    if (instructions[i].opcode == 0x8) { // LDI16
                        // LDI16 may have a label, which is a data word
                        // Count it as one extra word
                        char* rest = trimmed + strlen(token);
                        char* rest_trimmed = trim(rest);
                        if (*rest_trimmed != 0 && *rest_trimmed != ';') {
                            // There's a second argument (address label)
                            // Count it as a data word
                            address += 1;
                        }
                    }
                    break;
                }
            }
        }
    }
}

// Stage 2: Generate code
void stage2(FILE* file) {
    fseek(file, 0, SEEK_SET);
    char line[256];
    output_count = 0;

    while (fgets(line, sizeof(line), file)) {
        char* trimmed = trim(line);
        if (*trimmed == 0 || *trimmed == ';') continue;

        // Strip label if present
        char* colon = strchr(trimmed, ':');
        if (colon) {
            char* rest = colon + 1;
            trimmed = trim(rest);
            if (*trimmed == 0 || *trimmed == ';') continue;
        }

        // Parse instruction
        char* token = strtok(trimmed, " ,\t");
        if (!token) continue;

        // Handle directives
        if (strcmp(token, ".word") == 0 || strcmp(token, ".d") == 0) {
            char* value_token = strtok(NULL, " ,\t");
            if (value_token) {
                uint16_t val = parse_number(value_token);
                emit(val);
            }
            continue;
        }

        if (strcmp(token, ".cstr") == 0 || strcmp(token, ".ascii") == 0) {
            char* rest = trimmed + strlen(token);
            char* start = strchr(rest, '"');
            if (start) {
                char* end = strchr(start + 1, '"');
                if (end) {
                    *end = '\0';
                    char* str_content = start + 1;
                    for (int i = 0; str_content[i]; i++) {
                        emit((uint16_t)str_content[i]);
                    }
                    emit(0);
                }
            }
            continue;
        }

        // Look up instruction
        int opcode = -1;
        int format = -1;

        for (int i = 0; i < num_instructions; i++) {
            if (strcasecmp(token, instructions[i].name) == 0) {
                opcode = instructions[i].opcode;
                format = instructions[i].format;
                break;
            }
        }

        if (opcode == -1) {
            fprintf(stderr, "ERROR: Unknown instruction '%s'\n", token);
            continue;
        }

        // Parse operands
        char* operands[3] = {0, 0, 0};
        int op_count = 0;

        char* operand = strtok(NULL, " ,\t");
        while (operand && op_count < 3) {
            operands[op_count++] = operand;
            operand = strtok(NULL, " ,\t");
        }

        // Encode instruction
        uint16_t encoded = 0;
        encoded |= (opcode << 12);

        // Special handling for SYS
        if (opcode == 0xE) {  // SYS
            int syscall_id = 0;
            int arg1_reg = 0;
            int arg2_reg = 0;

            if (op_count >= 1) syscall_id = parse_number(operands[0]);
            if (op_count >= 2) arg1_reg = parse_register(operands[1]);
            if (op_count >= 3) arg2_reg = parse_register(operands[2]);

            encoded |= (syscall_id << 8);
            encoded |= (arg1_reg << 4);
            encoded |= arg2_reg;
            emit(encoded);
            continue;
        }

        // Special handling for LDI16
        if (opcode == 0x8) {  // LDI16 Rd, label
            int dest_reg = 0;
            uint16_t data_word = 0;
            int has_data = 0;

            if (op_count >= 1) {
                dest_reg = parse_register(operands[0]);
            }

            // Check for second operand (address label or immediate)
            if (op_count >= 2) {
                int sym_addr = find_symbol(operands[1]);
                if (sym_addr >= 0) {
                    data_word = sym_addr;
                    has_data = 1;
                } else {
                    data_word = parse_number(operands[1]);
                    has_data = 1;
                }
            }

            // Emit LDI16 instruction
            encoded |= (dest_reg << 8);
            emit(encoded);

            // Emit data word if provided
            if (has_data) {
                emit(data_word);
            }
            continue;
        }

        // Parse registers for other instructions
        int regs[3] = {0, 0, 0};
        int reg_count = 0;
        int imm_val = 0;

        for (int i = 0; i < op_count; i++) {
            int reg = parse_register(operands[i]);
            if (reg >= 0) {
                regs[reg_count++] = reg;
            } else {
                int sym_addr = find_symbol(operands[i]);
                if (sym_addr >= 0) {
                    imm_val = sym_addr;
                    reg_count++;
                } else {
                    imm_val = parse_number(operands[i]);
                    reg_count++;
                }
            }
        }

        // Special handling for jump instructions
        if (opcode == 0xB || opcode == 0xC || opcode == 0xD) {  // JMP, JZ, JNZ
            if (op_count >= 1) {
                int src_reg = parse_register(operands[0]);
                encoded |= (src_reg << 4);
            }
            emit(encoded);
            continue;
        }

        // Handle based on format
        switch (format) {
            case 0: // 3-reg: ADD, SUB, AND, OR, XOR, MUL
                if (reg_count >= 3) {
                    encoded |= (regs[0] << 8);
                    encoded |= (regs[1] << 4);
                    encoded |= regs[2];
                }
                break;
            case 1: // 2-reg: CMP, LD, ST
                if (reg_count >= 2) {
                    encoded |= (regs[0] << 8);
                    encoded |= (regs[1] << 4);
                }
                break;
            case 2: // reg+imm4: LDI
                if (reg_count >= 1) {
                    encoded |= (regs[0] << 8);
                    encoded |= (imm_val & 0xF);
                }
                break;
            case 3: // 0-reg: HALT
                break;
            default:
                break;
        }

        emit(encoded);
    }
}

// ============================================================
// 6. MAIN
// ============================================================

int main(int argc, char** argv) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s -i <filename>\n", argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "-i") != 0) {
        fprintf(stderr, "Usage: %s -i <filename>\n", argv[0]);
        return 1;
    }

    char* filename = argv[2];
    FILE* file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Error: Could not open file '%s'\n", filename);
        return 1;
    }

    // Stage 1: Collect symbols
    stage1(file);

    // Stage 2: Generate code
    stage2(file);

    fclose(file);

    // Output hex - one word per line
    for (int i = 0; i < output_count; i++) {
        printf("%04X\n", output[i]);
    }

    return 0;
}
