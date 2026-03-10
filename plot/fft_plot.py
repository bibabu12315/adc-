def draw_fft(axes, freqs, magnitude, title="FFT Spectrum"):
    """绘制 FFT 幅度谱"""
    axes.clear()
    axes.plot(freqs, magnitude, color='#d62728')
    axes.set_title(title)
    axes.set_xlabel('frequency (Hz)')
    axes.set_ylabel('magnitude')
    axes.grid(True)
    
    # Optional: Log scale on Y for better noise floor visibility
    # axes.set_yscale('log')
