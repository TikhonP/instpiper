import ctypes
import pyparsenames as pn
import sys
import numpy as np
import os


dir_path = os.path.dirname(os.path.realpath(__file__))
so_file = os.path.join(dir_path, 'parsenames.so')
names_path = os.path.join(dir_path, 'names/yob2018.txt')

class genderName(ctypes.Structure):
    _fields_ = [('name', ctypes.POINTER(ctypes.c_char)),
                ('gender', ctypes.c_char),
                ('popularity', ctypes.c_int),
                ]


genderName._fields_.append(('next', ctypes.POINTER(genderName)))

parsenames = ctypes.CDLL(so_file)

parsenames.readdata.argtypes = [ctypes.POINTER(ctypes.c_char), ]
parsenames.readdata.restype = ctypes.POINTER(genderName)

parsenames.release.argtypes = [ctypes.POINTER(genderName)]

parsenames.gender.restype = ctypes.c_char
parsenames.gender.argtypes = [
    ctypes.POINTER(genderName),
    ctypes.POINTER(ctypes.c_char),
    ctypes.POINTER(ctypes.c_double),
]


class closeMatches:
    def __init__(self):
        self.sp = parsenames.readdata(names_path.encode('utf-8'))

    def find(self, name, translit=True):
        """find gender by name.

        name: string
        translit: bool, include or not python translit, default True
        returns tuple gender (char) and score
        """
        
        if translit:
            name = pn.translitt(name)
        score = ctypes.c_double(0.)
        a = parsenames.gender(self.sp, name.encode(
            'utf-8'), ctypes.byref(score))
        a = a.decode('utf-8')
        if a != 'E':
            return (a, float(score.value))
        elif score.value == 0.5:
            return [None]
        else:
            a = pn.closeMatches(name)
            return a

    def __del__(self):
        parsenames.release(self.sp)


if __name__ == '__main__':
    from datetime import datetime
    if len(sys.argv) != 2:
        print('Usage : python parsenames_optimized.py <name>')
        sys.exit()
    startt = datetime.now()
    p = closeMatches()
    print('Loading time is ', datetime.now() - startt)
    startt = datetime.now()
    a = p.find(sys.argv[1])
    print(a)
    print(datetime.now() - startt)
