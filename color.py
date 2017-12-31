def prRed(prt): return("\033[91m {}\033[00m" .format(prt))
def prGreen(prt): return("\033[92m {}\033[00m" .format(prt))
def prYellow(prt): return("\033[93m {}\033[00m" .format(prt))
def prLightPurple(prt): return("\033[94m {}\033[00m" .format(prt))
def prPurple(prt): return("\033[95m {}\033[00m" .format(prt))
def prCyan(prt): return("\033[96m {}\033[00m" .format(prt))
def prLightGray(prt): return("\033[97m {}\033[00m" .format(prt))
def prBlack(prt): return("\033[98m {}\033[00m" .format(prt))

def text_color(s,value):
    if value > 0.5:
        return prGreen(s)
    elif value >= 0.25:
        return prYellow(s)
    elif value > 0:
        return prRed(s)
    else:
        return prBlack(s)
