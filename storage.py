# storage.py

### Bus Communication

class UnifiedBus:
    """
    Simple 8-bit unified bus.
    """

    def __init__(self):
        # Bus lines
        self.addr = 0x00      # 8-bit address
        self.data_out = 0x00  # 8-bit data from ALU to memory
        self.data_in = 0x00   # 8-bit data from memory to ALU
        self.ctrl = 0x00      # 4-bit control

        # Status (from slaves)
        self.ready = 1
        self.error = 0

        # Connected devices
        self.devices = {}

        # Log
        self.last_op = "IDLE"
        self.cycles = 0

    # Control bit helpers
    @property
    def rd(self):
        return (self.ctrl >> 0) & 1

    @rd.setter
    def rd(self, value):
        self.ctrl = (self.ctrl & ~1) | (value & 1)

    @property
    def wr(self):
        return (self.ctrl >> 1) & 1

    @wr.setter
    def wr(self, value):
        self.ctrl = (self.ctrl & ~2) | ((value & 1) << 1)

    @property
    def sel(self):
        return (self.ctrl >> 2) & 1

    @sel.setter
    def sel(self, value):
        self.ctrl = (self.ctrl & ~4) | ((value & 1) << 2)

    @property
    def clk(self):
        return (self.ctrl >> 3) & 1

    @clk.setter
    def clk(self, value):
        self.ctrl = (self.ctrl & ~8) | ((value & 1) << 3)

    def connect(self, name, device, address_range=None):
        """
        Connect a device to the bus.

        device: Object with read(addr) and write(addr, data) methods
        address_range: (start, end) tuple for memory-mapped devices
        """
        self.devices[name] = {
            'device': device,
            'range': address_range
        }
        print(f"  Connected {name}")

    def read(self):
        """
        Perform a read operation on the bus.

        Returns: data read from device
        """
        self.cycles += 1

        # Find which device owns this address
        for name, info in self.devices.items():
            if info['range'] and info['range'][0] <= self.addr <= info['range'][1]:
                # Read from device
                self.data_in = info['device'].read(self.addr)
                self.ready = 1
                self.last_op = f"READ {self.addr:02X} -> {self.data_in:02X} from {name}"
                return self.data_in

        # If no device found
        self.error = 1
        self.last_op = f"READ {self.addr:02X} -> (no device)"
        return 0xFF

    def write(self):
        """
        Perform a write operation on the bus.

        Returns: True if successful
        """
        self.cycles += 1

        # Find which device owns this address
        for name, info in self.devices.items():
            if info['range'] and info['range'][0] <= self.addr <= info['range'][1]:
                # Write to device
                info['device'].write(self.addr, self.data_out)
                self.ready = 1
                self.last_op = f"WRITE {self.addr:02X} <- {self.data_out:02X} to {name}"
                return True

        # If no device found
        self.error = 1
        self.last_op = f"WRITE {self.addr:02X} <- {self.data_out:02X} to nowhere"
        return False

    def tick(self):
        """
        One bus cycle.
        Reads or writes based on control signals.
        """
        # Check control signals
        if self.sel == 1:
            # I/O (future)
            pass
        else:
            # Memory
            if self.rd == 1 and self.wr == 0:
                return self.read()
            elif self.wr == 1 and self.rd == 0:
                return self.write()
            else:
                # No operation
                self.last_op = "IDLE"
                return None


### Simple Memory (Reliable)

class SimpleMemory:
    """Simple memory backend for debug and testing."""

    def __init__(self, size=256):
        self.size = size
        self.data = [0] * size
        self.read_count = 0
        self.write_count = 0

    def read(self, addr):
        """Read from memory."""
        if 0 <= addr < self.size:
            self.read_count += 1
            return self.data[addr]
        return 0xFF

    def write(self, addr, data):
        """Write to memory."""
        if 0 <= addr < self.size:
            self.write_count += 1
            self.data[addr] = data & 0xFF

    def get_stats(self):
        """Return usage statistics."""
        return {
            'reads': self.read_count,
            'writes': self.write_count,
            'total_ops': self.read_count + self.write_count
        }

    def dump(self, start=0, end=None):
        """Dump memory contents."""
        if end is None:
            end = self.size
        return self.data[start:end]

### NumPy Memory (Performance)

class FastMemory:
    """NumPy-based memory backend (fast)."""

    def __init__(self, size=256):
        self.size = size
        self.data = np.zeros(size, dtype=np.uint8)
        self.read_count = 0
        self.write_count = 0

    def read(self, addr):
        if 0 <= addr < self.size:
            self.read_count += 1
            return int(self.data[addr])
        return 0xFF

    def write(self, addr, data):
        if 0 <= addr < self.size:
            self.write_count += 1
            self.data[addr] = data & 0xFF

    def get_stats(self):
        return {
            'reads': self.read_count,
            'writes': self.write_count,
            'total_ops': self.read_count + self.write_count
        }
