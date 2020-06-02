def is_numb_arr(arr):
    try:
        [int(i) for i in arr]
        return True
    except:
        return False

def recurs_splitter(spl):
    returndata = []
    data = spl.split("@")
    if len(data) > 1:
        for d in data:
            returndata.extend(recurs_splitter(d))
    else:
        data = spl.split(":")
        if len(data) > 1:
            for d in data:
                returndata.extend(recurs_splitter(d))
        else:
            returndata = data
    return returndata

def processproxyrow(row):
    parts = recurs_splitter(row)
    proxystructure = {"ip":None, "port":None, "usr":None, "pswd":None}
    if len(parts) not in [2, 4]: return None
    for p in parts:
        if len(p.split(".")) == 4 and is_numb_arr(p.split(".")):
            if proxystructure["ip"]:
                return None
            proxystructure["ip"] = p
        elif is_numb_arr([p]):
            if proxystructure["port"]:
                return None
            proxystructure["port"] = p
        else:
            if proxystructure["usr"]:
                if proxystructure["pswd"]:
                    return None
                else:
                    proxystructure["pswd"] = p
            else:
                proxystructure["usr"] = p
    if not (proxystructure["ip"] and proxystructure["port"]): return None
    usrpswdstruct = proxystructure["usr"] + ":" + proxystructure["pswd"] if proxystructure["usr"] and proxystructure["pswd"] else None
    return usrpswdstruct + "@" + proxystructure["ip"] + ":" + proxystructure["port"] if usrpswdstruct else proxystructure["ip"] + ":" + proxystructure["port"]
