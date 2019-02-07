import math
_prefix = {
    -8: ('y', 1e-24),  # yocto
    -7: ('z', 1e-21),  # zepto
    -6: ('a', 1e-18),  # atto
    -5: ('f', 1e-15),  # femto
    -4: ('p', 1e-12),  # pico
    -3: ('n', 1e-9),   # nano
    -2: ('µ', 1e-6),   # micro
    -1: ('m', 1e-3),   # mili
#    'c': 1e-2,   # centi
#    'd': 1e-1,   # deci
    0: ('', 1),
    1: ('k', 1e3),    # kilo
    2: ('M', 1e6),    # mega
    3: ('G', 1e9),    # giga
    4: ('T', 1e12),   # tera
    5: ('P', 1e15),   # peta
    6: ('E', 1e18),   # exa
    7: ('Z', 1e21),   # zetta
    8: ('Y', 1e24),   # yotta
}

def convertSI(number, precision=3):
    if number == 0:
        return "0"
    index = math.trunc(math.log10(abs(number))/3)
    if number < 1 and number > -1:
        index -= 1
    strFormat = "%%.%df%s" % (abs(int(precision)), _prefix[index][0])
    ret = strFormat % (number/_prefix[index][1])
    return ret
