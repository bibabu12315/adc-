import numpy as np

def draw_histogram(axes, raw_data=None, filtered_data=None, show_raw=False, show_filtered=True, title="ADC Histogram"):
    """绘制 ADC 直方图"""
    if show_raw and raw_data is not None and len(raw_data) > 0:
        num_unique = len(np.unique(raw_data))
        bins = min(num_unique if num_unique > 0 else 10, 100)
        axes.hist(raw_data, bins=bins, alpha=0.5, color='gray', edgecolor='black', label='Raw Data')

    if show_filtered and filtered_data is not None and len(filtered_data) > 0:
        num_unique = len(np.unique(filtered_data))
        bins = min(num_unique if num_unique > 0 else 10, 100)
        axes.hist(filtered_data, bins=bins, alpha=0.75, color='#1f77b4', edgecolor='black', label='Filtered Data')

    axes.set_title(title)
    axes.set_xlabel('ADC value')
    axes.set_ylabel('count')
    axes.grid(True)
    if show_raw or show_filtered:
        axes.legend()
