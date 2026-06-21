import numpy as np

def safe_percent(part, whole):
    if whole == 0:
        return 0.0
    return np.round((part / whole) * 100, 2)