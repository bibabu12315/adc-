import sys
import os
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QSplitter, QMessageBox
from PySide6.QtCore import Qt

# 导入自定义组件
from gui.control_panel import ControlPanel
from gui.plot_canvas import PlotCanvas

# 导入业务逻辑
from utils.excel_loader import load_excel, convert_to_valid_data
from analysis.stats_analysis import calculate_stats
from analysis.enob_analysis import calculate_enob
from analysis.bit_analysis import calculate_bit_stability
from analysis.fft_analysis import calculate_fft

# 导入绘图逻辑
from plot.waveform_plot import draw_waveform
from plot.histogram_plot import draw_histogram
from plot.fft_plot import draw_fft
from plot.bit_noise_plot import draw_bit_noise

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADC Analysis Tool (上位机版)")
        self.resize(1000, 700)
        
        # 核心数据状态
        self.df = None
        self.current_channel_data = None
        self.analysis_results = {}
        
        self.init_ui()
        self.bind_events()

    def init_ui(self):
        # 主挂载点
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QHBoxLayout(main_widget)
        
        # 使用 QSplitter 按照 30% / 70% 比例切分
        splitter = QSplitter(Qt.Horizontal)
        
        self.control_panel = ControlPanel()
        self.plot_canvas = PlotCanvas()
        
        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.plot_canvas)
        
        # 设置初始比例 (这里采用大约 3:7 的比例)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)

    def bind_events(self):
        self.control_panel.file_loaded_signal.connect(self.on_file_loaded)
        self.control_panel.run_analysis_signal.connect(self.on_run_analysis)
        self.control_panel.plot_changed_signal.connect(self.on_plot_changed)
        # 当通道改变时，如果有数据，可以直接重新分析该通道
        self.control_panel.cmb_channel.currentIndexChanged.connect(self.on_channel_switched)

    def on_file_loaded(self, file_path):
        try:
            self.df = load_excel(file_path)
            # 刷新通道选择下拉框
            channels = list(self.df.columns)
            self.control_panel.update_channels(channels)
            QMessageBox.information(self, "成功", f"成功加载数据，共发现 {len(channels)} 个通道")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载文件失败:\n{str(e)}")

    def on_channel_switched(self):
        # 只要切换了通道，若用户已有运行记录，最好提示点"开始分析"或自动开始，这里选择静默，等用户点击更新。
        pass

    def on_run_analysis(self):
        if self.df is None:
            QMessageBox.warning(self, "警告", "请先选择并加载一个 Excel 文件。")
            return
            
        channel = self.control_panel.get_selected_channel()
        if not channel:
            return
            
        try:
            # 清洗数据
            raw_series = self.df[channel]
            self.current_channel_data = convert_to_valid_data(raw_series)
            
            if len(self.current_channel_data) == 0:
                QMessageBox.warning(self, "警告", f"通道 '{channel}' 没有有效数值数据。")
                return

            config = self.control_panel.get_config()
            results_text = f"--- {channel} 分析报告 ---\n"
            
            # --- 1) 统计分析 ---
            if config['do_stats']:
                stats = calculate_stats(self.current_channel_data)
                self.analysis_results['stats'] = stats
                results_text += f"\n[基本统计]\n平均值 (Mean): {stats['mean']:.2f}\n"
                results_text += f"标准差 (Std): {stats['std']:.2f}\n"
                results_text += f"峰峰值 (P2P): {stats['peak_to_peak']}\n"
                results_text += f"最大值: {stats['max']} / 最小值: {stats['min']}\n"
            
            # --- 2) ENOB 分析 ---
            if config['do_enob'] and 'stats' in self.analysis_results:
                enob = calculate_enob(self.analysis_results['stats']['std'], config['adc_bits'])
                self.analysis_results['enob'] = enob
                results_text += f"\n[有效位数]\nENOB: {enob:.2f} bits\n"
                
            # --- 3) Bit 稳定性 ---
            if config['do_bit']:
                bit_stats = calculate_bit_stability(self.current_channel_data, config['adc_bits'])
                self.analysis_results['bit_stats'] = bit_stats
                # (可选将详情全列在 GUI 里，防止太长这里省略具体每一位)
                
            # --- 4) FFT 分析 ---
            if config['do_fft']:
                freqs, mag = calculate_fft(self.current_channel_data, config['fs'])
                self.analysis_results['fft'] = (freqs, mag)
            
            # 显示结果到文本框
            self.control_panel.display_results(results_text)
            
            # 更新正在被选中的图表
            current_plot = self.control_panel.get_selected_plot()
            self.update_canvas(current_plot, channel)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"分析过程中发生异常:\n{str(e)}")

    def on_plot_changed(self, plot_type):
        if self.current_channel_data is None:
            return
        channel = self.control_panel.get_selected_channel()
        self.update_canvas(plot_type, channel)
        
    def update_canvas(self, plot_type, channel):
        if self.current_channel_data is None:
            return
            
        axes = self.plot_canvas.axes
        data = self.current_channel_data
        
        axes.clear()
        
        try:
            if plot_type == "波形图":
                draw_waveform(axes, data, title=f"{channel} - Waveform")
            elif plot_type == "直方图":
                draw_histogram(axes, data, title=f"{channel} - Histogram")
            elif plot_type == "FFT图":
                if 'fft' in self.analysis_results:
                    freqs, mag = self.analysis_results['fft']
                    draw_fft(axes, freqs, mag, title=f"{channel} - FFT Spectrum")
                else:
                    axes.text(0.5, 0.5, "FFT Analysis Not Enabled\nor Not Calculated Yet", ha='center', va='center')
            elif plot_type == "Bit噪声":
                if 'bit_stats' in self.analysis_results:
                    bit_stats = self.analysis_results['bit_stats']
                    draw_bit_noise(axes, bit_stats, title=f"{channel} - Bit Flip Ratio")
                else:
                    axes.text(0.5, 0.5, "Bit Analysis Not Enabled\nor Not Calculated Yet", ha='center', va='center')
                    
        except Exception as e:
            axes.clear()
            axes.text(0.1, 0.5, f"Plot Error:\n{str(e)}", color='red')
            
        self.plot_canvas.update_plot()
