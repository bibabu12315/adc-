from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, 
                               QLabel, QComboBox, QLineEdit, QCheckBox, 
                               QRadioButton, QButtonGroup, QGroupBox, QTextEdit, 
                               QFileDialog, QMessageBox)
from PySide6.QtCore import Signal

class ControlPanel(QWidget):
    # 定义自定义信号以供 MainWindow 挂载执行操作
    file_loaded_signal = Signal(str)
    run_analysis_signal = Signal()
    plot_changed_signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # --- 1) 数据文件选择 ---
        file_group = QGroupBox("1. 数据文件选择")
        file_layout = QVBoxLayout()
        self.btn_load_file = QPushButton("选择 Excel 文件")
        self.btn_load_file.clicked.connect(self.select_file)
        self.lbl_file_path = QLabel("当前未选择文件")
        self.lbl_file_path.setWordWrap(True)
        
        # 多通道选择
        ch_layout = QHBoxLayout()
        ch_layout.addWidget(QLabel("选择通道:"))
        self.cmb_channel = QComboBox()
        self.cmb_channel.currentIndexChanged.connect(self.on_channel_changed)
        ch_layout.addWidget(self.cmb_channel)

        file_layout.addWidget(self.btn_load_file)
        file_layout.addWidget(self.lbl_file_path)
        file_layout.addLayout(ch_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # --- 2) ADC 配合 ---
        config_group = QGroupBox("2. ADC 配置")
        config_layout = QVBoxLayout()
        
        bits_layout = QHBoxLayout()
        bits_layout.addWidget(QLabel("ADC 位数:"))
        self.cmb_bits = QComboBox()
        self.cmb_bits.addItems(["8", "10", "12", "16"])
        self.cmb_bits.setCurrentText("12")
        bits_layout.addWidget(self.cmb_bits)
        
        fs_layout = QHBoxLayout()
        fs_layout.addWidget(QLabel("采样率 (Hz):"))
        self.le_fs = QLineEdit("20000")
        fs_layout.addWidget(self.le_fs)
        
        config_layout.addLayout(bits_layout)
        config_layout.addLayout(fs_layout)
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # --- 3) 分析与图形选择 ---
        combo_group = QGroupBox("3. 分析与图形选择")
        combo_layout = QGridLayout()
        
        self.chk_stats = QCheckBox("基本统计")
        self.chk_enob = QCheckBox("ENOB")
        self.chk_fft = QCheckBox("FFT分析")
        self.chk_bit = QCheckBox("Bit稳定")
        
        for chk in [self.chk_stats, self.chk_enob, self.chk_fft, self.chk_bit]:
            chk.setChecked(True)
            
        self.rb_waveform = QRadioButton("波形图")
        self.rb_histogram = QRadioButton("直方图")
        self.rb_fft = QRadioButton("FFT图")
        self.rb_bit = QRadioButton("Bit噪声")
        self.rb_waveform.setChecked(True)
        
        self.plot_btn_group = QButtonGroup()
        for i, rb in enumerate([self.rb_waveform, self.rb_histogram, self.rb_fft, self.rb_bit]):
            self.plot_btn_group.addButton(rb, i)
            rb.toggled.connect(self.on_plot_radio_toggled)

        # 排版 (4列 x 2排)
        combo_layout.addWidget(self.chk_stats, 0, 0)
        combo_layout.addWidget(self.chk_enob, 0, 1)
        combo_layout.addWidget(self.chk_fft, 0, 2)
        combo_layout.addWidget(self.chk_bit, 0, 3)

        combo_layout.addWidget(self.rb_waveform, 1, 0)
        combo_layout.addWidget(self.rb_histogram, 1, 1)
        combo_layout.addWidget(self.rb_fft, 1, 2)
        combo_layout.addWidget(self.rb_bit, 1, 3)
        
        combo_group.setLayout(combo_layout)
        layout.addWidget(combo_group)

        # --- 4) 运行控制 ---
        self.btn_run = QPushButton("开始分析")
        self.btn_run.setMinimumHeight(40)
        self.btn_run.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.btn_run.clicked.connect(self.run_analysis)
        layout.addWidget(self.btn_run)

        # --- 5) 结果显示 ---
        result_group = QGroupBox("5. 结果展示")
        result_layout = QVBoxLayout()
        self.txt_results = QTextEdit()
        self.txt_results.setReadOnly(True)
        self.txt_results.setMinimumHeight(300) # 显著增加显示区域高度
        # 增大显示字体
        font = self.txt_results.font()
        font.setPointSize(11)
        self.txt_results.setFont(font)
        result_layout.addWidget(self.txt_results)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        self.setLayout(layout)
        
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 Excel 文件", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.lbl_file_path.setText(file_path)
            self.file_loaded_signal.emit(file_path)

    def on_channel_changed(self):
        pass # Optional hook

    def on_plot_radio_toggled(self):
        sender = self.sender()
        if sender.isChecked():
            self.plot_changed_signal.emit(sender.text())
            
    def run_analysis(self):
        self.run_analysis_signal.emit()

    def update_channels(self, channels):
        self.cmb_channel.clear()
        self.cmb_channel.addItems(channels)
        
    def get_selected_channel(self):
        return self.cmb_channel.currentText()

    def get_config(self):
        return {
            'adc_bits': int(self.cmb_bits.currentText()),
            'fs': float(self.le_fs.text()),
            'do_stats': self.chk_stats.isChecked(),
            'do_enob': self.chk_enob.isChecked(),
            'do_bit': self.chk_bit.isChecked(),
            'do_fft': self.chk_fft.isChecked()
        }

    def get_selected_plot(self):
        for rb in [self.rb_waveform, self.rb_histogram, self.rb_fft, self.rb_bit]:
            if rb.isChecked():
                return rb.text()
        return "波形图"

    def display_results(self, text):
        self.txt_results.setText(text)
