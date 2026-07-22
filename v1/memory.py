import numpy as np
import time
from abc import ABC, abstractmethod

# ==================== MEMORY INTERFACE ====================

class MemoryBackend(ABC):
    """Abstract interface for all memory backends."""
    
    @abstractmethod
    def read(self, address):
        """Read data from address."""
        pass
    
    @abstractmethod
    def write(self, address, data):
        """Write data to address."""
        pass
    
    @abstractmethod
    def get_stats(self):
        """Return performance statistics."""
        pass


# ==================== BACKEND 1: BOOLEAN SRAM ====================

class BooleanSRAM(MemoryBackend):
    """
    Accurate simulation using Boolean gates.
    Slow but matches the physical substrate exactly.
    """
    
    def __init__(self, size=256, bits=8):
        self.size = size
        self.bits = bits
        self.bit_mask = (1 << bits) - 1
        
        # Import your existing gate-based SRAM
        # (assuming you have SRAMCell and SRAMArray from before)
        from nubit import SRAMArray
        self.sram = SRAMArray(rows=size, cols=1, bits=bits)
        
        self.read_count = 0
        self.write_count = 0
        self.start_time = time.time()
    
    def read(self, address):
        """Read using Boolean gate simulation."""
        self.read_count += 1
        return self.sram.read(address)
    
    def write(self, address, data):
        """Write using Boolean gate simulation."""
        self.write_count += 1
        self.sram.write(address, data)
    
    def get_stats(self):
        elapsed = time.time() - self.start_time
        total_ops = self.read_count + self.write_count
        return {
            'backend': 'BooleanSRAM',
            'reads': self.read_count,
            'writes': self.write_count,
            'total_ops': total_ops,
            'elapsed': elapsed,
            'ops_per_sec': total_ops / elapsed if elapsed > 0 else 0,
            'accuracy': '100% (gate-level simulation)',
            'speed': 'Slow (Python object overhead)'
        }


# ==================== BACKEND 2: FAST NUMPY SRAM ====================

class FastSRAM(MemoryBackend):
    """
    High-performance NumPy-based SRAM.
    Fast but abstracts away gate-level details.
    """
    
    def __init__(self, size=256, bits=8):
        self.size = size
        self.bits = bits
        self.bit_mask = (1 << bits) - 1
        
        # NumPy array for fast storage
        self.memory = np.zeros(size, dtype=np.uint8)
        
        self.read_count = 0
        self.write_count = 0
        self.start_time = time.time()
    
    def read(self, address):
        """Read using direct array indexing."""
        self.read_count += 1
        if 0 <= address < self.size:
            return int(self.memory[address])
        return 0
    
    def write(self, address, data):
        """Write using direct array indexing."""
        self.write_count += 1
        if 0 <= address < self.size:
            self.memory[address] = data & self.bit_mask
    
    def read_batch(self, addresses):
        """Vectorized batch read."""
        valid = (addresses >= 0) & (addresses < self.size)
        result = np.zeros_like(addresses, dtype=np.uint8)
        result[valid] = self.memory[addresses[valid]]
        return result
    
    def write_batch(self, addresses, data_array):
        """Vectorized batch write."""
        valid = (addresses >= 0) & (addresses < self.size)
        self.memory[addresses[valid]] = data_array[valid] & self.bit_mask
    
    def get_stats(self):
        elapsed = time.time() - self.start_time
        total_ops = self.read_count + self.write_count
        return {
            'backend': 'FastSRAM',
            'reads': self.read_count,
            'writes': self.write_count,
            'total_ops': total_ops,
            'elapsed': elapsed,
            'ops_per_sec': total_ops / elapsed if elapsed > 0 else 0,
            'accuracy': '100% (bit-exact)',
            'speed': 'Fast (NumPy vectorized)'
        }


# ==================== BACKEND 3: MEMRISTOR SRAM ====================

class MemristorSRAM(MemoryBackend):
    """
    Simulates memristor crossbar memory.
    Models resistance states, write endurance, variability.
    """
    
    def __init__(self, size=256, bits=8):
        self.size = size
        self.bits = bits
        self.bit_mask = (1 << bits) - 1
        
        # Memristor states: high resistance = 0, low resistance = 1
        # Store as float to model analog resistance states
        self.resistance_states = np.ones((size, bits)) * 1e6  # High resistance (0)
        
        # Memristor characteristics
        self.write_endurance = 1e6  # Max write cycles per cell
        self.write_cycles = np.zeros((size, bits), dtype=np.int64)
        self.variability = 0.05  # 5% resistance variation
        
        # Thresholds for reading
        self.r_low = 1e3  # Low resistance threshold
        self.r_high = 1e5  # High resistance threshold
        
        self.read_count = 0
        self.write_count = 0
        self.start_time = time.time()
    
    def _read_resistance(self, address, bit):
        """Read resistance state with variability."""
        base_r = self.resistance_states[address, bit]
        noise = np.random.normal(0, self.variability * base_r)
        return base_r + noise
    
    def _write_resistance(self, address, bit, value):
        """Write resistance state."""
        if value == 1:
            self.resistance_states[address, bit] = self.r_low
        else:
            self.resistance_states[address, bit] = self.r_high
        
        self.write_cycles[address, bit] += 1
        
        # Check endurance
        if self.write_cycles[address, bit] > self.write_endurance:
            print(f"Warning: Cell [{address},{bit}] exceeded write endurance!")
    
    def read(self, address):
        """Read by sensing resistance states."""
        self.read_count += 1
        if not (0 <= address < self.size):
            return 0
        
        data = 0
        for bit in range(self.bits):
            r = self._read_resistance(address, bit)
            # Determine if high or low resistance
            bit_value = 1 if r < (self.r_low + self.r_high) / 2 else 0
            data |= (bit_value << bit)
        
        return data
    
    def write(self, address, data):
        """Write by switching resistance states."""
        self.write_count += 1
        if not (0 <= address < self.size):
            return
        
        for bit in range(self.bits):
            bit_value = (data >> bit) & 1
            self._write_resistance(address, bit, bit_value)
    
    def get_stats(self):
        elapsed = time.time() - self.start_time
        total_ops = self.read_count + self.write_count
        avg_writes = np.mean(self.write_cycles)
        max_writes = np.max(self.write_cycles)
        
        return {
            'backend': 'MemristorSRAM',
            'reads': self.read_count,
            'writes': self.write_count,
            'total_ops': total_ops,
            'elapsed': elapsed,
            'ops_per_sec': total_ops / elapsed if elapsed > 0 else 0,
            'accuracy': 'Analog (resistance states)',
            'speed': 'Medium (models physical effects)',
            'avg_write_cycles': avg_writes,
            'max_write_cycles': max_writes,
            'endurance_limit': self.write_endurance
        }


# ==================== BACKEND 4: REGISTER FILE ====================

class RegisterFileBackend(MemoryBackend):
    """
    Small, fast register file.
    Limited size but extremely fast access.
    """
    
    def __init__(self, num_regs=16, bits=8):
        self.size = num_regs
        self.bits = bits
        self.bit_mask = (1 << bits) - 1
        
        self.registers = np.zeros(num_regs, dtype=np.uint8)
        
        self.read_count = 0
        self.write_count = 0
        self.start_time = time.time()
    
    def read(self, address):
        """Read register."""
        self.read_count += 1
        if 0 <= address < self.size:
            return int(self.registers[address])
        return 0
    
    def write(self, address, data):
        """Write register."""
        self.write_count += 1
        if 0 <= address < self.size:
            self.registers[address] = data & self.bit_mask
    
    def get_stats(self):
        elapsed = time.time() - self.start_time
        total_ops = self.read_count + self.write_count
        return {
            'backend': 'RegisterFileBackend',
            'reads': self.read_count,
            'writes': self.write_count,
            'total_ops': total_ops,
            'elapsed': elapsed,
            'ops_per_sec': total_ops / elapsed if elapsed > 0 else 0,
            'accuracy': '100% (register-level)',
            'speed': 'Fastest (small, direct access)',
            'num_registers': self.size
        }


# ==================== MEMORY CONTROLLER ====================

class MemoryController:
    """
    Unified memory interface with backend selection.
    Allows mixing different memory technologies.
    """
    
    def __init__(self, default_backend='fast'):
        self.backends = {}
        self.active_backend = None
        
        # Initialize all backends
        self.register_backend('boolean', BooleanSRAM(size=256, bits=8))
        self.register_backend('fast', FastSRAM(size=256, bits=8))
        self.register_backend('memristor', MemristorSRAM(size=256, bits=8))
        self.register_backend('registers', RegisterFileBackend(num_regs=16, bits=8))
        
        # Set default
        self.select_backend(default_backend)
    
    def register_backend(self, name, backend):
        """Register a new memory backend."""
        self.backends[name] = backend
    
    def select_backend(self, name):
        """Switch to a different backend."""
        if name in self.backends:
            self.active_backend = self.backends[name]
            print(f"Switched to {name} backend")
        else:
            raise ValueError(f"Backend '{name}' not found")
    
    def read(self, address):
        """Read from active backend."""
        return self.active_backend.read(address)
    
    def write(self, address, data):
        """Write to active backend."""
        self.active_backend.write(address, data)
    
    def get_stats(self):
        """Get stats from all backends."""
        stats = {}
        for name, backend in self.backends.items():
            stats[name] = backend.get_stats()
        return stats
    
    def print_stats(self):
        """Print formatted stats."""
        print("\n" + "=" * 70)
        print("MEMORY BACKEND STATISTICS")
        print("=" * 70)
        
        for name, stats in self.get_stats().items():
            print(f"\n[{name.upper()}]")
            print(f"  Backend: {stats['backend']}")
            print(f"  Reads: {stats['reads']:,}")
            print(f"  Writes: {stats['writes']:,}")
            print(f"  Total ops: {stats['total_ops']:,}")
            print(f"  Elapsed: {stats['elapsed']:.3f}s")
            print(f"  Ops/sec: {stats['ops_per_sec']:,.0f}")
            print(f"  Accuracy: {stats['accuracy']}")
            print(f"  Speed: {stats['speed']}")
            
            # Backend-specific stats
            if 'avg_write_cycles' in stats:
                print(f"  Avg write cycles: {stats['avg_write_cycles']:.1f}")
                print(f"  Max write cycles: {stats['max_write_cycles']}")
            if 'num_registers' in stats:
                print(f"  Num registers: {stats['num_registers']}")
