def draw_waveform(axes, data, title="ADC Waveform"):
    """绘制 ADC 波形图"""
    axes.clear()
    axes.plot(data, linewidth=0.8, color='#1f77b4')
    axes.set_title(title)
    axes.set_xlabel('sample index')
    axes.set_ylabel('ADC value')
    axes.grid(True)
