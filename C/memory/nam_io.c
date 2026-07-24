// nam_io.c - NAM I/O Port Handlers
#include "nam.h"
#include "cpu.h"

static NAM nam;


// NAM I/O Handler
uint16_t nam_io_read(uint16_t port) {
    switch (port) {
        case NAM_CTRL:
            return 0;  // Write-only
        case NAM_ADDR:
            return nam.match_pattern;
        case NAM_DATA:
            return nam.match_data;
        case NAM_STATUS: {
            uint16_t status = NAM_STATUS_READY;
            if (nam.match_count > 0) {
                status |= NAM_STATUS_FOUND;
            }
            if (nam_get_match_count(&nam) >= NAM_ENTRIES) {
                status |= NAM_STATUS_FULL;
            }
            return status;
        }
        default:
            return 0xFFFF;
    }
}

void nam_io_write(uint16_t port, uint16_t value) {
    static uint16_t pending_pattern = 0;
    static uint16_t pending_data = 0;
    static int pending_op = 0;

    switch (port) {
        case NAM_CTRL: {
            pending_op = value;
            if (value & NAM_CTRL_SEARCH) {
                // Search for pattern in NAM_ADDR
                uint16_t result = nam_search(&nam, pending_pattern);
                // Result is available in NAM_DATA
            }
            if (value & NAM_CTRL_STORE) {
                // Store pattern/data
                nam_store(&nam, pending_pattern, pending_data);
            }
            if (value & NAM_CTRL_DELETE) {
                nam_delete(&nam, pending_pattern);
            }
            if (value & NAM_CTRL_CLEAR) {
                nam_clear(&nam);
            }
            if (value & NAM_CTRL_HAMMING) {
                nam_search_hamming(&nam, pending_pattern);
            }
            break;
        }
        case NAM_ADDR:
            pending_pattern = value;
            break;
        case NAM_DATA:
            pending_data = value;
            break;
        case NAM_STATUS:
            // Read-only
            break;
        default:
            break;
    }
}


// NAM Initialization for CPU Integration


void nam_system_init(void) {
    nam_init(&nam);
}

// modify bus_tick to route NAM I/O In bus.c,
// add this to the memory access logic:

/*
uint16_t bus_tick(Bus* bus) {
    // Check if address is in NAM I/O range
    if (bus->addr >= NAM_PORT_BASE && bus->addr <= 0xFFF7) {
        if (bus->rd) {
            bus->data_in = nam_io_read(bus->addr);
        } else if (bus->wr) {
            nam_io_write(bus->addr, bus->data_out);
        }
        return bus->data_in;
    }
    // ... existing memory logic ...
}
*/
