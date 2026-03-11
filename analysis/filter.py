import numpy as np

def mean_multiple_filter(data, k):
    if len(data) == 0:
        return data
    mean_val = np.mean(data)
    return data[data <= (mean_val * k)]

def range_filter(data, min_val, max_val):
    if len(data) == 0:
        return data
    
    mask = np.ones(len(data), dtype=bool)
    if min_val is not None:
        mask &= (data >= min_val)
    if max_val is not None:
        mask &= (data <= max_val)
        
    return data[mask]

def probability_filter(data, threshold):
    if len(data) == 0:
        return data

    min_val = None
    max_val = None

    if isinstance(threshold, (list, tuple)) and len(threshold) == 2:
        min_val, max_val = threshold
    else:
        # 兼容旧调用：传入单值时不执行额外过滤
        return data

    mask = np.ones(len(data), dtype=bool)
    if min_val is not None:
        mask &= (data >= min_val)
    if max_val is not None:
        mask &= (data <= max_val)

    return data[mask]
