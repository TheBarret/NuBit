#!/bin/bash

echo "Compiling NuBit runtime..."

# Clean old files
rm -f *.o nubit

# Gates, adder, alu, cpu, bus
gcc -O3 -march=native -Wall -Wextra -c gates.c -o gates.o -DNDEBUG
gcc -O3 -march=native -Wall -Wextra -c adder.c -o adder.o -DNDEBUG
gcc -O3 -march=native -Wall -Wextra -c alu.c -o alu.o -DNDEBUG
gcc -O3 -march=native -Wall -Wextra -c cpu.c -o cpu.o -DNDEBUG
gcc -O2 -Wall -Wextra -c bus.c -o bus.o -DNDEBUG

# Application
gcc -O2 -Wall -Wextra -c main.c -o main.o -DNDEBUG
gcc -o nubit gates.o adder.o alu.o cpu.o bus.o main.o -DNDEBUG

# Assembler
gcc -o nb-asm nb-asm.c

# inform
if [ $? -eq 0 ]; then
    echo "Build successful!"
else
    echo "Build failed!"
    exit 1
fi
