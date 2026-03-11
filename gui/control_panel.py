from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QComboBox, QLineEdit, QCheckBox, 
                               QRadioButton, QButtonGroup, QGroupBox, QTextEdit, 
                               QFileDialog, QMessageBox, QScrollArea)
from PySide6.QtCore import Signal
import sys

class ControlPanel(QWidget):
    file_loaded_signal = Signal(str)
    run_analysis_signal = Signal()
    plot_settings_changed_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Container for scroll area
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # --- 数据文件加载 ---
        file_group = QGroupBox("数据文件加载")
        file_layout = QVBoxLayout()
        self.btn_load_file = QPushButton("加载 Excel 文件")
        self.btn_load_file.clicked.connect(self.select_file)
        self.btn_run = QPushButton("开始分析")
        self.btn_run.clicked.connect(self.run_analysis)
        self.lbl_file_path = QLabel("未选择文件")
        self.lbl_file_path.setWordWrap(True)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_load_file)
        btn_layout.addWidget(self.btn_run)
        
        ch_layout = QHBoxLayout()
        ch_layout.addWidget(QLabel("选择通道:"))
        self.cmb_channel = QComboBox()
        self.cmb_channel.currentIndexChanged.connect(self.on_channel_changed)
        ch_layout.addWidget(self.cmb_channel)

        bits_layout = QHBoxLayout()
        bits_layout.addWidget(QLabel("ADC 位数:"))
        self.cmb_bits = QComboBox()
        self.cmb_bits.addItems(["8", "10", "12", "16"])
        self.cmb_bits.setCurrentText("12")
        bits_layout.addWidget(self.cmb_bits)

        file_layout.addLayout(btn_layout)
        file_layout.addWidget(self.lbl_file_path)
        file_layout.addLayout(ch_layout)
        file_layout.addLayout(bits_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # --- 数据滤波 ---
        filter_group = QGroupBox("数据滤波")
        filter_layout = QVBoxLayout()
        
        # Mean Multiple
        self.chk_mean_filter = QCheckBox("启用均值倍数滤波")
        mean_layout = QHBoxLayout()
        mean_layout.addWidget(QLabel("倍数 K:"))
        self.le_mean_k = QLineEdit("10")
        mean_layout.addWidget(self.le_mean_k)
        
        # Probability (switched to limit range filtering)
        self.chk_prob_filter = QCheckBox("启用上下限滤波")
        prob_layout = QHBoxLayout()
        prob_layout.addWidget(QLabel("下限:"))
        self.le_prob_min = QLineEdit()
        prob_layout.addWidget(self.le_prob_min)
        prob_layout.addWidget(QLabel("上限:"))
        self.le_prob_max = QLineEdit()
        prob_layout.addWidget(self.le_prob_max)
        
        filter_layout.addWidget(self.chk_mean_filter)
        filter_layout.addLayout(mean_layout)
        filter_layout.addWidget(self.chk_prob_filter)
        filter_layout.addLayout(prob_layout)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # --- 绘图数据源 ---
        source_group = QGroupBox("绘图数据源")
        source_layout = QHBoxLayout()
        self.rb_src_raw = QRadioButton("原始数据")
        self.rb_src_filtered = QRadioButton("滤波后数据 (默认)")
        self.rb_src_filtered.setChecked(True)
        
        self.src_btn_group = QButtonGroup()
        self.src_btn_group.addButton(self.rb_src_raw, 0)
        self.src_btn_group.addButton(self.rb_src_filtered, 1)
        
        source_layout.addWidget(self.rb_src_raw)
        source_layout.addWidget(self.rb_src_filtered)
        source_layout.addStretch()
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # --- 波形图 Y 轴模式 ---
        y_group = QGroupBox("波形图 Y 轴模式")
        y_layout = QVBoxLayout()
        self.rb_y_auto_filt = QRadioButton("自动 (基于滤波后范围)")
        self.rb_y_auto_raw = QRadioButton("自动 (基于原始范围)")
        self.rb_y_manual = QRadioButton("手动设置")
        self.rb_y_auto_filt.setChecked(True)
        
        self.y_btn_group = QButtonGroup()
        self.y_btn_group.addButton(self.rb_y_auto_filt, 0)
        self.y_btn_group.addButton(self.rb_y_auto_raw, 1)
        self.y_btn_group.addButton(self.rb_y_manual, 2)

        y_auto_layout = QHBoxLayout()
        y_auto_layout.addWidget(self.rb_y_auto_filt)
        y_auto_layout.addWidget(self.rb_y_auto_raw)
        y_auto_layout.addStretch()
        
        self.man_y_layout = QHBoxLayout()
        self.man_y_layout.addWidget(QLabel("Y 最小值:"))
        self.le_y_min = QLineEdit("0")
        self.man_y_layout.addWidget(QLabel("Y 最大值:"))
        self.le_y_max = QLineEdit("4095")
        
        y_layout.addLayout(y_auto_layout)
        y_layout.addWidget(self.rb_y_manual)
        y_layout.addLayout(self.man_y_layout)
        y_group.setLayout(y_layout)
        layout.addWidget(y_group)
        
        # --- 直方图设置 ---
        hist_group = QGroupBox("直方图设置")
        hist_layout = QHBoxLayout()
        hist_layout.addWidget(QLabel("柱数 (Bins):"))
        self.le_hist_bins = QLineEdit("100")
        hist_layout.addWidget(self.le_hist_bins)
        hist_group.setLayout(hist_layout)
        layout.addWidget(hist_group)
        
        # --- FFT 设置 ---
        fft_group = QGroupBox("FFT 设置")
        fft_layout = QHBoxLayout()
        fft_layout.addWidget(QLabel("采样率 (Hz):"))
        self.le_fs = QLineEdit("20000")
        fft_layout.addWidget(self.le_fs)
        fft_group.setLayout(fft_layout)
        layout.addWidget(fft_group)
        
        self.btn_run.setStyleSheet("font-weight: bold; font-size: 12px; background-color: #28a745; color: white;")

        # Analysis Results Display
        self.txt_results = QTextEdit()
        self.txt_results.setReadOnly(True)
        self.txt_results.setMinimumHeight(150)
        layout.addWidget(self.txt_results)
        
        # Finish scroll area
        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 Excel 文件", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.lbl_file_path.setText(file_path)
            self.file_loaded_signal.emit(file_path)

    def on_channel_changed(self):
        pass

    def on_settings_changed(self, *args):
        pass
            
    def run_analysis(self):
        self.run_analysis_signal.emit()

    def update_channels(self, channels):
        self.cmb_channel.clear()
        self.cmb_channel.addItems(channels)
        
    def get_selected_channel(self):
        return self.cmb_channel.currentText()

    def get_config(self):
        try:
            mean_k = float(self.le_mean_k.text())
        except ValueError:
            mean_k = 10.0
            
        try:
            prob_min = float(self.le_prob_min.text()) if self.le_prob_min.text() else None
        except ValueError:
            prob_min = None

        try:
            prob_max = float(self.le_prob_max.text()) if self.le_prob_max.text() else None
        except ValueError:
            prob_max = None
            
        plot_source = "Filtered" if self.rb_src_filtered.isChecked() else "Raw"
        
        if self.rb_y_auto_filt.isChecked():
            y_mode = "Auto_Filt"
        elif self.rb_y_auto_raw.isChecked():
            y_mode = "Auto_Raw"
        else:
            y_mode = "Manual"
            
        try:
            y_min = float(self.le_y_min.text())
        except:
            y_min = 0.0
            
        try:
            y_max = float(self.le_y_max.text())
        except:
            y_max = 4095.0
            
        try:
            hist_bins = int(self.le_hist_bins.text())
        except:
            hist_bins = 100
            
        try:
            fs = float(self.le_fs.text())
        except:
            fs = 20000.0

        return {
            'adc_bits': int(self.cmb_bits.currentText()),
            'fs': fs,
            'filter_mean_enabled': self.chk_mean_filter.isChecked(),
            'filter_mean_k': mean_k,
            'filter_prob_enabled': self.chk_prob_filter.isChecked(),
            'filter_prob_min': prob_min,
            'filter_prob_max': prob_max,
            'plot_source': plot_source,
            'y_mode': y_mode,
            'y_min': y_min,
            'y_max': y_max,
            'hist_bins': hist_bins
        }

    def update_statistics(self, raw_count, filt_count):
        removed = raw_count - filt_count
        ratio = (removed / raw_count * 100.0) if raw_count > 0 else 0.0
        return f"原始样本数: {raw_count} | 滤波后样本数: {filt_count} | 剔除样本数: {removed} | 剔除比例: {ratio:.2f}%"

    def display_results(self, text):
        self.txt_results.setText(text)
