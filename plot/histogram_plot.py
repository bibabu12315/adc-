import numpy as np

def draw_histogram(axes, data, title="ADC Histogram"):
    """绘制 ADC 直方图"""
    axes.clear()
    if len(data) == 0:
        return
        
    num_unique = len(np.unique(data))
    bins = min(num_unique if num_unique > 0 else 10, 100)
    
    axes.hist(data, bins=bins, alpha=0.75, color='#2ca02c', edgecolor='black')
    axes.set_title(title)
    axes.set_xlabel('ADC value')
    axes.set_ylabel('count')
    axes.grid(True)
