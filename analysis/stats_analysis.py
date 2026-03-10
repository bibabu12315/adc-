import numpy as np

def calculate_stats(data):
    """
    计算基本统计指标
    """
    if len(data) == 0:
        return None
        
    stats = {
        'mean': float(np.mean(data)),
        'std': float(np.std(data)),
        'max': float(np.max(data)),
        'min': float(np.min(data)),
        'peak_to_peak': float(np.max(data) - np.min(data))
    }
    return stats
