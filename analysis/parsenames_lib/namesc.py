import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path)

from parsenames_optimized import closeMatches


c = closeMatches()


def names(username, full_name):
    u = c.find(username)
    f = c.find(full_name)

    if u[0] is None and f[0] is None:
        return [None]
    elif u[0] is None:
        return f
    elif f[0] is None:
        return u
    else:
        if u[1] > f[1]:
            return u
        elif u[1] < f[1]:
            return f
        else:
            if u[0] == f[0]:
                return u
            else:
                return [None]
