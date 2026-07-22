import numpy as np

class UnifiedBus:
    """
    Configurable unified bus supporting 8-bit and 16-bit architectures.
    """
    def __init__(self, addr_width=8, data_width=8):
        self.addr_width = addr_width
        self.data_width = data_width

        # Masks for automatic width enforcement
        self.addr_mask = (1 << addr_width) - 1
        self.data_mask = (1 << data_width) - 1

        # Pre-calculate hex string lengths for clean logging
        self.addr_hex_len = addr_width // 4
        self.data_hex_len = data_width // 4

        # Bus lines
        self.addr = 0
        self.data_out = 0
        self.data_in = 0
        self.ctrl = 0

        # Status
        self.ready = 1
        self.error = 0

        # Connected devices: {name: {'device': obj, 'range': (start, end)}}
        self.devices = {}

        # Diagnostics
        self.last_op = "IDLE"
        self.cycles = 0

    # --- Control Signal Properties ---
    @property
    def rd(self): return (self.ctrl >> 0) & 1
    @rd.setter
    def rd(self, value): self.ctrl = (self.ctrl & ~1) | (value & 1)

    @property
    def wr(self): return (self.ctrl >> 1) & 1
    @wr.setter
    def wr(self, value): self.ctrl = (self.ctrl & ~2) | ((value & 1) << 1)

    @property
    def sel(self): return (self.ctrl >> 2) & 1
    @sel.setter
    def sel(self, value): self.ctrl = (self.ctrl & ~4) | ((value & 1) << 2)

    @property
    def clk(self): return (self.ctrl >> 3) & 1
    @clk.setter
    def clk(self, value): self.ctrl = (self.ctrl & ~8) | ((value & 1) << 3)

    def connect(self, name, device, address_range=None):
        """Connect a device to the bus."""
        self.devices[name] = {
            'device': device,
            'range': address_range
        }

    def _find_device(self):
        """Internal helper to find the device owning the current address."""
        for name, info in self.devices.items():
            r = info['range']
            if r and r[0] <= self.addr <= r[1]:
                return name, info['device']
        return None, None

    def read(self):
        """Perform a read operation."""
        self.cycles += 1
        name, device = self._find_device()

        if device:
            # Mask data to bus width automatically
            self.data_in = device.read(self.addr) & self.data_mask
            self.ready = 1
            self.error = 0
            self.last_op = f"READ  {self.addr:0{self.addr_hex_len}X} -> {self.data_in:0{self.data_hex_len}X} [{name}]"
            return self.data_in

        # Bus float high (all 1s) if no device responds
        self.error = 1
        self.data_in = self.data_mask
        self.last_op = f"READ  {self.addr:0{self.addr_hex_len}X} -> ERR (No Device)"
        return self.data_in

    def write(self):
        """Perform a write operation."""
        self.cycles += 1
        name, device = self._find_device()

        if device:
            device.write(self.addr, self.data_out)
            self.ready = 1
            self.error = 0
            self.last_op = f"WRITE {self.addr:0{self.addr_hex_len}X} <- {self.data_out:0{self.data_hex_len}X} [{name}]"
            return True

        self.error = 1
        self.last_op = f"WRITE {self.addr:0{self.addr_hex_len}X} <- {self.data_out:0{self.data_hex_len}X} ERR (No Device)"
        return False

    def tick(self):
        """One bus cycle. Evaluates control signals."""
        # Note: 'sel' can be used later to differentiate Memory vs I/O space
        if self.rd and not self.wr:
            return self.read()
        elif self.wr and not self.rd:
            return self.write()
        else:
            self.last_op = "IDLE"
            return None


class Memory:
    """
    Unified memory backend supporting 8-bit and 16-bit widths.
    Can use pure Python lists or NumPy arrays for storage.
    """
    def __init__(self, size=256, data_width=8, backend='numpy'):
        self.size = size
        self.data_width = data_width
        self.data_mask = (1 << data_width) - 1

        # Select backend and appropriate data type
        if backend == 'numpy':
            dtype = np.uint8 if data_width == 8 else np.uint16
            self.data = np.zeros(size, dtype=dtype)
        elif backend == 'python':
            self.data = [0] * size
        else:
            raise ValueError("Backend must be 'numpy' or 'python'")

        self.read_count = 0
        self.write_count = 0

    def read(self, addr):
        if 0 <= addr < self.size:
            self.read_count += 1
            return int(self.data[addr])
        return self.data_mask

    def write(self, addr, data):
        if 0 <= addr < self.size:
            self.write_count += 1
            # Mask data to prevent overflow if a wider value is passed
            self.data[addr] = data & self.data_mask

    def get_stats(self):
        return {
            'reads': self.read_count,
            'writes': self.write_count,
            'total_ops': self.read_count + self.write_count
        }

    def dump(self, start=0, end=None):
        if end is None: end = self.size
        # Convert to standard list for uniform output format
        if isinstance(self.data, np.ndarray):
            return self.data[start:end].tolist()
        return self.data[start:end]
