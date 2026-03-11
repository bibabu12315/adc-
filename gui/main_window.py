import sys
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QSplitter, QMessageBox, QTabWidget
from PySide6.QtCore import Qt

from gui.control_panel import ControlPanel
from gui.plot_canvas import PlotCanvas

from utils.excel_loader import load_excel, convert_to_valid_data
from analysis.stats_analysis import calculate_stats
from analysis.enob_analysis import calculate_enob
from analysis.bit_analysis import calculate_bit_stability
from analysis.fft_analysis import calculate_fft
from analysis.filter import mean_multiple_filter, probability_filter

import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADC 数据分析工具")
        self.resize(1100, 750)
        self.statusBar().showMessage("就绪")
        
        self.df = None
        self.raw_channel_data = None
        self.filtered_channel_data = None
        
        self.init_ui()
        self.bind_events()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QHBoxLayout(main_widget)
        splitter = QSplitter(Qt.Horizontal)
        
        self.control_panel = ControlPanel()
        self.control_panel.setFixedWidth(360)
        
        # Tabs for plots
        self.tab_widget = QTabWidget()
        
        self.canvas_wave = PlotCanvas()
        self.canvas_hist = PlotCanvas()
        self.canvas_fft = PlotCanvas()
        self.canvas_bit = PlotCanvas()
        
        self.tab_widget.addTab(self.canvas_wave, "波形图")
        self.tab_widget.addTab(self.canvas_hist, "直方图")
        self.tab_widget.addTab(self.canvas_fft, "FFT 频谱")
        self.tab_widget.addTab(self.canvas_bit, "Bit 噪声")
        
        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.tab_widget)
        
        splitter.setSizes([360, 740])
        splitter.setCollapsible(0, False)
        layout.addWidget(splitter)

    def bind_events(self):
        self.control_panel.file_loaded_signal.connect(self.on_file_loaded)
        self.control_panel.run_analysis_signal.connect(self.on_run_analysis)

    def on_file_loaded(self, file_path):
        try:
            self.df = load_excel(file_path)
            channels = list(self.df.columns)
            self.control_panel.update_channels(channels)
            QMessageBox.information(self, "成功", f"成功加载数据，共发现 {len(channels)} 个通道")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载失败:\n{str(e)}")

    def on_run_analysis(self):
        if self.df is None:
            return
            
        channel = self.control_panel.get_selected_channel()
        if not channel:
            return
            
        try:
            raw_series = self.df[channel]
            self.raw_channel_data = convert_to_valid_data(raw_series)
            
            if len(self.raw_channel_data) == 0:
                return

            config = self.control_panel.get_config()
            
            filtered_data = self.raw_channel_data
            if config['filter_mean_enabled']:
                filtered_data = mean_multiple_filter(filtered_data, config['filter_mean_k'])
            if config['filter_prob_enabled']:
                filtered_data = probability_filter(filtered_data, (config['filter_prob_min'], config['filter_prob_max']))
                
            self.filtered_channel_data = filtered_data

            stats_msg = self.control_panel.update_statistics(len(self.raw_channel_data), len(self.filtered_channel_data))
            self.statusBar().showMessage(stats_msg)
            
            # Replot and compute stats
            self.update_plots()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"分析出错:\n{str(e)}")

    def update_plots(self):
        if self.raw_channel_data is None or self.filtered_channel_data is None:
            return
            
        config = self.control_panel.get_config()
        channel = self.control_panel.get_selected_channel()
        
        plot_data = self.filtered_channel_data if config['plot_source'] == 'Filtered' else self.raw_channel_data
        
        if len(plot_data) == 0:
            self.control_panel.display_results("警告：选定的数据源在滤波后为空！")
            for canvas in [self.canvas_wave, self.canvas_hist, self.canvas_fft, self.canvas_bit]:
                canvas.axes.clear()
                canvas.update_plot()
            return
            
        # Stats based on selected data source (requirement 3)
        source_name = "滤波后数据" if config['plot_source'] == 'Filtered' else "原始数据"
        results_text = f"--- {channel} 分析报告 ---\n数据源: {source_name}\n"
        
        stats = calculate_stats(plot_data)
        results_text += f"\n[基本统计]\n平均值 (Mean): {stats['mean']:.2f}\n"
        results_text += f"标准差 (Std): {stats['std']:.2f}\n"
        results_text += f"峰峰值 (P2P): {stats['peak_to_peak']}\n"
        results_text += f"最大值 (Max): {stats['max']} / 最小值 (Min): {stats['min']}\n"
        
        enob = calculate_enob(stats['std'], config['adc_bits'])
        results_text += f"\n[有效位数]\nENOB: {enob:.2f} bits\n"
        
        # --- Waveform Plot ---
        ax_w = self.canvas_wave.axes
        ax_w.clear()
        ax_w.plot(plot_data, linewidth=0.8, color='#1f77b4')
        ax_w.set_title(f"{channel} | 波形图")
        ax_w.set_xlabel("采样点索引")
        ax_w.set_ylabel("ADC 采样值")
        ax_w.grid(True)
        
        # Y Scaling mode
        y_mode = config['y_mode']
        if y_mode == "Auto_Filt" and len(self.filtered_channel_data) > 0:
            ymin = np.min(self.filtered_channel_data)
            ymax = np.max(self.filtered_channel_data)
            margin = (ymax - ymin) * 0.05 if ymax > ymin else 10
            ax_w.set_ylim(ymin - margin, ymax + margin)
        elif y_mode == "Auto_Raw" and len(self.raw_channel_data) > 0:
            ymin = np.min(self.raw_channel_data)
            ymax = np.max(self.raw_channel_data)
            margin = (ymax - ymin) * 0.05 if ymax > ymin else 10
            ax_w.set_ylim(ymin - margin, ymax + margin)
        elif y_mode == "Manual":
            ax_w.set_ylim(config['y_min'], config['y_max'])
            
        self.canvas_wave.update_plot()
        
        # --- Histogram Plot ---
        ax_h = self.canvas_hist.axes
        ax_h.clear()
        counts, bins, patches = ax_h.hist(plot_data, bins=config['hist_bins'], alpha=0.75, color='#2ca02c', edgecolor='black')
        ax_h.set_title(f"{channel} | 直方图 ({config['hist_bins']} 柱)")
        ax_h.set_xlabel("ADC 采样值")
        ax_h.set_ylabel("频数")
        ax_h.grid(True)
        self.canvas_hist.update_plot()
        
        # --- FFT Plot ---
        ax_f = self.canvas_fft.axes
        ax_f.clear()
        freqs, mag = calculate_fft(plot_data, config['fs'])
        ax_f.plot(freqs, mag, color='#d62728')
        ax_f.set_title(f"{channel} | FFT 频谱")
        ax_f.set_xlabel("频率 (Hz)")
        ax_f.set_ylabel("幅度 (dB)")
        ax_f.grid(True)
        self.canvas_fft.update_plot()
        
        # --- Bit Noise Plot ---
        ax_b = self.canvas_bit.axes
        ax_b.clear()
        bit_stats = calculate_bit_stability(plot_data, config['adc_bits'])
        
        bits = []
        flips = []
        for stat in bit_stats:
             bits.append(stat['bit_index'])
             flips.append(stat['flip_ratio'] * 100.0)
             
        ax_b.bar(bits, flips, color='#9467bd')
        ax_b.set_title(f"{channel} | Bit 翻转率")
        ax_b.set_xlabel("Bit 索引")
        ax_b.set_ylabel("翻转率 (%)")
        ax_b.set_xticks(bits)
        ax_b.grid(True, axis='y')
        self.canvas_bit.update_plot()
        
        self.control_panel.display_results(results_text)
