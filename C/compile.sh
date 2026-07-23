#!/bin/bash

echo "Compiling NuBit runtime..."

# Clean old files
rm -f *.o nubit

# Compile with optimizations
#echo "gates..."
#gcc -O3 -march=native -Wall -Wextra -c gates.c -o gates.o -DNDEBUG
#echo "adder..."
#gcc -O3 -march=native -Wall -Wextra -c adder.c -o adder.o -DNDEBUG
#echo "alu16..."
#gcc -O3 -march=native -Wall -Wextra -c alu.c -o alu.o -DNDEBUG
#echo "cpu16..."
#gcc -O3 -march=native -Wall -Wextra -c cpu.c -o cpu.o -DNDEBUG
#echo "assembler..."
#gcc -o nb-asm nb-asm.c
#echo "bus..."
#gcc -O2 -Wall -Wextra -c bus.c -o bus.o -DNDEBUG
#echo "entrypoint..."
#gcc -O3 -march=native -Wall -Wextra main.c gates.o adder.o alu.o cpu.o -o nubit -lm -DNDEBUG

gcc -O2 -Wall -Wextra -c gates.c -o gates.o -DNDEBUG
gcc -O2 -Wall -Wextra -c adder.c -o adder.o -DNDEBUG
gcc -O2 -Wall -Wextra -c alu.c -o alu.o -DNDEBUG
gcc -O2 -Wall -Wextra -c cpu.c -o cpu.o -DNDEBUG
gcc -O2 -Wall -Wextra -c bus.c -o bus.o -DNDEBUG
gcc -O2 -Wall -Wextra -c main.c -o main.o -DNDEBUG

gcc -o nubit gates.o adder.o alu.o cpu.o bus.o main.o -DNDEBUG
gcc -o nb-asm nb-asm.c


if [ $? -eq 0 ]; then
    echo "Build successful!"
else
    echo "Build failed!"
    exit 1
fi
