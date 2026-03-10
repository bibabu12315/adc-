import numpy as np

def calculate_fft(data, fs):
    """
    对信号去直流分量并进行 FFT 分析
    返回：freq频段数组, magnitude幅度数组
    """
    if len(data) == 0:
        return np.array([]), np.array([])
        
    # 1) 去直流
    data_ac = data - np.mean(data)
    
    n = len(data_ac)
    
    # 2) 计算 FFT
    fft_result = np.fft.fft(data_ac)
    
    # 3) 计算幅度
    magnitude = np.abs(fft_result) / n
    magnitude = magnitude[:n//2]  # 只保留正频率部分
    
    # 4) 生成频率轴
    freqs = np.fft.fftfreq(n, d=1/fs)[:n//2]
    
    return freqs, magnitude
