import numpy as np

def calculate_bit_stability(data, adc_bits):
    """
    逐 bit 统计翻转概率
    公式: flip_ratio = min(count0, count1) / total
    """
    num_samples = len(data)
    bit_stats = []
    
    if num_samples == 0:
        return bit_stats
        
    int_data = np.array(data, dtype=int)
    
    for bit in range(adc_bits):
        # 提取各个采样的指定 bit
        bit_values = (int_data >> bit) & 1
        
        count1 = np.sum(bit_values)
        count0 = num_samples - count1
        
        # 按照用户给定的要求公式
        flip_ratio = min(count0, count1) / num_samples
        
        bit_stats.append({
            'bit_index': bit,
            'count0': int(count0),
            'count1': int(count1),
            'flip_ratio': float(flip_ratio)
        })
        
    return bit_stats
