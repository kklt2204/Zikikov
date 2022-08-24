



class Table:

    DTC_STATUS = {0: 'No error type available', 4: 'Error not present now, but already stored',
                  5: 'Error present now and already stored', 8: 'Error not present now, but already stored',
                  9: 'Error present now and already stored', 12: 'Error not present now, but already stored',
                  13: 'Error present now and already stored',
                  32: 'Error not present now, but already stored',
                  33: 'Error present now and already stored', 36: 'Error not present now, but already stored',
                  37: 'Error present now and already stored',
                  40: 'Error not present now, but already stored',
                  41: 'Error present now and already stored', 44: 'Error not present now, but already stored',
                  45: 'Error present now and already stored', 64: 'Unknown type of error',
                  68: 'Error stored',
                  69: 'Error stored', 72: 'Error stored', 73: 'Error stored', 76: 'Error stored', 77: 'Error stored',
                  96: 'Error stored', 97: 'Error stored', 100: 'Error stored',
                  101: 'Error stored',
                  104: 'Error stored', 105: 'Error stored', 108: 'Error stored', 109: 'Error stored',
                  16: 'Test conditions fulfilled', 17: 'Test conditions not yet fulfilled',
                  128: 'Error would not cause a warning lamp to light up',
                  129: 'Error would cause a warning lamp to light up', 255: 'Unknown type of error'}

    SVK_CODE = {0: '-', 1: 'HWEL', 2: 'HWAP', 3: 'HWFR', 4: 'GWTB', 5: 'CAFD', 6: 'BTLD', 7: 'FLSL', 8: 'SWFL',
                9: 'SWFF', 10: 'SWPF', 11: 'ONPS', 12: 'IBAD', 13: 'SWFK', 15: 'FAFP',
                16: 'FCFA', 26: 'TLRT', 27: 'TPRG', 28: 'BLUP', 29: 'FLUP', 160: 'ENTD', 161: 'NAVD', 162: 'FCFN',
                192: 'SWUP', 193: 'SWIP', 255: '-'}


