#!/bin/bash

echo "Compiling NuBit runtime..."

# Clean old files
rm -f *.o nubit

# Compile with optimizations
echo "gates..."
gcc -O3 -march=native -Wall -Wextra -c gates.c -o gates.o

echo "adder..."
gcc -O3 -march=native -Wall -Wextra -c adder.c -o adder.o

echo "alu16..."
gcc -O3 -march=native -Wall -Wextra -c alu.c -o alu.o

echo "cpu16..."
gcc -O3 -march=native -Wall -Wextra -c cpu.c -o cpu.o

echo "entrypoint..."
gcc -O3 -march=native -Wall -Wextra main.c gates.o adder.o alu.o cpu.o -o nubit -lm

if [ $? -eq 0 ]; then
    echo "Build successful!"
    ./nubit
else
    echo "Build failed!"
    exit 1
fi
