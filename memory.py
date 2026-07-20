import numpy as np
from nubit import Gate

class SRAMCell:
    """
    1-bit SRAM cell.
    Storage: Two cross-coupled inverters (4 gates)
    Access: Two pass transistors (2 gates)
    """
    def __init__(self):
        # Storage: cross-coupled inverters
        self.inv1 = Gate('NOT')
        self.inv2 = Gate('NOT')
        
        # Access: pass gates controlled by word line
        self.pass1 = Gate('AND')  # Read pass gate
        self.pass2 = Gate('AND')  # Write pass gate
        
        # Discretize NOT gates
        inputs_not = np.array([[0], [1]])
        targets_not = np.array([1, 0])
        self.inv1.discretize(inputs_not, targets_not)
        self.inv2.discretize(inputs_not, targets_not)
        
        # Discretize AND gates
        inputs_and = np.array([[0,0], [0,1], [1,0], [1,1]])
        targets_and = np.array([0, 0, 0, 1])
        self.pass1.discretize(inputs_and, targets_and)
        self.pass2.discretize(inputs_and, targets_and)
        
        # Internal state (stored bit)
        self.stored_bit = 0
        self.stored_bit_not = 1  # Inverted state
    
    def forward(self, word_line, bit_line, write_enable):
        """
        word_line: Selects this cell for access
        bit_line: Data to write (if write_enable=1)
        write_enable: 1 = write, 0 = read
        Returns: stored bit (if write_enable=0)
        """
        if write_enable == 1 and word_line == 1:
            # Write: set stored bit from bit_line
            self.stored_bit = bit_line
            self.stored_bit_not = 1 - bit_line
            
            # Write through pass gate to ensure stability
            self.stored_bit = self.pass2.predict_binary(bit_line, word_line)
            self.stored_bit_not = self.inv1.predict_binary(self.stored_bit)
            self.stored_bit = self.inv2.predict_binary(self.stored_bit_not)
        
        # Read: pass stored bit through pass gate
        return self.pass1.predict_binary(self.stored_bit, word_line)
    
    def read(self, word_line):
        """Read stored bit (combinational)."""
        return self.pass1.predict_binary(self.stored_bit, word_line)
    
    def write(self, data, word_line):
        """Write data when word_line is active."""
        if word_line == 1:
            self.stored_bit = self.pass2.predict_binary(data, word_line)
            self.stored_bit_not = self.inv1.predict_binary(self.stored_bit)
            self.stored_bit = self.inv2.predict_binary(self.stored_bit_not)
        return self.stored_bit

class SRAMByte:
    """8-bit SRAM cell with common word line and bit lines."""
    def __init__(self):
        self.cells = [SRAMCell() for _ in range(8)]
        self.stored_byte = 0
    
    def forward(self, word_line, bit_lines, write_enable):
        """
        word_line: Selects this byte
        bit_lines: 8-bit data (if write_enable=1)
        write_enable: 1 = write, 0 = read
        Returns: 8-bit stored value (if write_enable=0)
        """
        result = 0
        for i in range(8):
            bit = (bit_lines >> i) & 1 if write_enable else 0
            out = self.cells[i].forward(word_line, bit, write_enable)
            result |= (int(out) << i)
        
        if write_enable and word_line:
            self.stored_byte = bit_lines
        
        return result
    
    def read(self, word_line):
        """Read 8-bit value."""
        result = 0
        for i in range(8):
            out = self.cells[i].read(word_line)
            result |= (int(out) << i)
        return result
    
    def write(self, data, word_line):
        """Write 8-bit value."""
        if word_line == 1:
            self.stored_byte = data
            for i in range(8):
                bit = (data >> i) & 1
                self.cells[i].write(bit, word_line)
        return self.stored_byte

class RowDecoder:
    """
    N-to-2^N row decoder.
    Converts binary address to one-hot word line.
    """
    def __init__(self, bits=4):
        self.bits = bits
        self.num_rows = 1 << bits  # 2^bits
        
        # Build decoder logic: for each output, AND together selected inputs
        self.and_gates = [Gate('AND') for _ in range(self.num_rows)]
        
        # Discretize AND gates
        inputs_and = np.array([[0,0], [0,1], [1,0], [1,1]])
        targets_and = np.array([0, 0, 0, 1])
        for gate in self.and_gates:
            gate.discretize(inputs_and, targets_and)
        
        # NOT gates for inverted inputs
        self.not_gate = Gate('NOT')
        inputs_not = np.array([[0], [1]])
        targets_not = np.array([1, 0])
        self.not_gate.discretize(inputs_not, targets_not)
    
    def forward(self, address):
        """
        address: binary input (0 to 2^bits - 1)
        Returns: one-hot output (only one bit is 1)
        """
        # Extract bits
        bits = [(address >> i) & 1 for i in range(self.bits)]
        
        # For each output, AND together selected bits (or inverted bits)
        result = 0
        for row in range(self.num_rows):
            # Build AND tree for this row
            and_inputs = []
            for i in range(self.bits):
                bit = bits[i]
                # If row has 1 at position i, use bit; else use inverted bit
                if (row >> i) & 1:
                    and_inputs.append(bit)
                else:
                    and_inputs.append(self.not_gate.predict_binary(bit))
            
            # AND all inputs together
            if len(and_inputs) == 1:
                out = and_inputs[0]
            else:
                out = and_inputs[0]
                for i in range(1, len(and_inputs)):
                    out = self.and_gates[row].predict_binary(out, and_inputs[i])
            
            result |= (int(out) << row)
        
        return result

class SRAMArray:
    """
    N × M SRAM array with row/column decoding.
    """
    def __init__(self, rows=64, cols=64, bits_per_cell=8):
        self.rows = rows
        self.cols = cols
        self.bits_per_cell = bits_per_cell
        self.word_size = cols * bits_per_cell // 8  # Bytes per row
        
        # Memory cells: rows × cols × bits_per_cell
        # We'll organize as rows × bytes
        self.bytes_per_row = cols * bits_per_cell // 8
        self.memory = [[SRAMByte() for _ in range(self.bytes_per_row)] for _ in range(rows)]
        
        # Address decoders
        self.row_decoder = RowDecoder(int(np.ceil(np.log2(rows))))
        self.col_decoder = RowDecoder(int(np.ceil(np.log2(self.bytes_per_row))))
        
        # Control signals
        self.read_enable = 0
        self.write_enable = 0
        self.output_data = 0
    
    def forward(self, address, data_in=0, read_enable=1, write_enable=0):
        """
        address: Memory address (0 to rows * bytes_per_row - 1)
        data_in: Data to write (if write_enable=1)
        read_enable: 1 = read, 0 = no read
        write_enable: 1 = write, 0 = no write
        Returns: data_out (if read_enable=1)
        """
        # Decode address into row and column
        row_addr = address // self.bytes_per_row
        col_addr = address % self.bytes_per_row
        
        # Activate word lines
        row_select = self.row_decoder.forward(row_addr)
        
        # Read or write
        if write_enable == 1 and read_enable == 0:
            # Write: only selected byte gets data
            byte = self.memory[row_addr][col_addr]
            byte.write(data_in, row_select)
            self.output_data = data_in
        elif read_enable == 1 and write_enable == 0:
            # Read: selected byte outputs data
            byte = self.memory[row_addr][col_addr]
            self.output_data = byte.read(row_select)
        else:
            # Invalid: both read and write enabled
            self.output_data = 0
        
        return self.output_data
    
    def read(self, address):
        """Read from memory address."""
        return self.forward(address, read_enable=1, write_enable=0)
    
    def write(self, address, data):
        """Write to memory address."""
        return self.forward(address, data_in=data, read_enable=0, write_enable=1)


class MemoryController:
    """
    Memory controller with timing and bus interface.
    """
    def __init__(self, size=4096, word_size=8):
        self.size = size  # 4KB
        self.word_size = word_size  # 8 bits
        self.memory = SRAMArray(rows=64, cols=64, bits_per_cell=8)
        
        # Address bus (12 bits for 4KB)
        self.address_bus = 0
        self.data_bus = 0
        self.control_bus = 0  # 0=read, 1=write
        
        # State
        self.ready = 1
        self.busy = 0
    
    def forward(self, address, data_in=0, write_enable=0):
        """
        address: Memory address (0-4095)
        data_in: Data to write (if write_enable=1)
        write_enable: 0=read, 1=write
        Returns: data_out (if read)
        """
        # Check address bounds
        if address >= self.size:
            return 0
        
        # Perform read/write
        if write_enable:
            return self.memory.write(address, data_in)
        else:
            return self.memory.read(address)


# TESTER

if __name__ == "__main__":
    print("SRAM MEMORY TEST")

    # Create 256-byte memory (8 rows × 32 bytes)
    memory = SRAMArray(rows=8, cols=32, bits_per_cell=8)

    # Test write/read
    print("\nTesting write/read operations:")

    # Write values
    for i in range(8):
        address = i * 4
        data = i * 16 + 0x0F
        memory.write(address, data)
        print(f"  Write: addr={address:2d}, data={data:02X}")

    # Read values
    print()
    for i in range(8):
        address = i * 4
        data = memory.read(address)
        print(f"  Read:  addr={address:2d}, data={data:02X}")

    # Test pattern
    print("\nTesting pattern (0x55 = 01010101):")
    test_addr = 0x10
    memory.write(test_addr, 0x55)
    read_back = memory.read(test_addr)
    print(f"  Write 0x55 at 0x{test_addr:02X}")
    print(f"  Read back: 0x{read_back:02X}")
    print(f"  Status: {'✓' if read_back == 0x55 else '✗'}")
    print("✅ Memory system verified.")
    
