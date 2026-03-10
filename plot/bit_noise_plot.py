def draw_bit_noise(axes, bit_stats, title="Bit Noise (Flip Ratio)"):
    """绘制每个 bit 的翻转概率图"""
    axes.clear()
    if not bit_stats:
        return
        
    bits = [stat['bit_index'] for stat in bit_stats]
    probs = [stat['flip_ratio'] for stat in bit_stats]
    
    axes.bar(bits, probs, color='#ff7f0e', alpha=0.8)
    axes.set_title(title)
    axes.set_xlabel('bit index')
    axes.set_ylabel('flip ratio')
    axes.set_xticks(bits)
    axes.grid(True, axis='y')
    axes.set_ylim([0, 0.6]) # Max ratio is 0.5 usually
