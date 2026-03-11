def draw_waveform(axes, raw_data=None, filtered_data=None, show_raw=False, show_filtered=True, title="ADC Waveform"):
    """绘制 ADC 波形图"""
    axes.set_title(title)
    axes.set_xlabel('sample index')
    axes.set_ylabel('ADC value')

    if show_raw and raw_data is not None:
        axes.plot(raw_data, linewidth=0.8, color='gray', alpha=0.5, label='Raw Data')
    if show_filtered and filtered_data is not None:
        axes.plot(filtered_data, linewidth=0.8, color='#1f77b4', label='Filtered Data')

    axes.grid(True)
    if show_raw or show_filtered:
        axes.legend()
