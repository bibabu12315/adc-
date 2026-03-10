import numpy as np

def calculate_enob(std, adc_bits):
    """
    计算 ENOB (Effective Number Of Bits)
    公式：ENOB = log2(FullScale / (sqrt(12) * std))
    """
    if std <= 0:
        return float('inf') # 避免除零异常
        
    full_scale = 2 ** adc_bits
    enob = np.log2(full_scale / (np.sqrt(12) * std))
    return float(enob)
