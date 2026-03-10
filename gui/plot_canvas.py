from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QSizePolicy

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # 初始化 Matplotlib Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        super(PlotCanvas, self).__init__(self.fig)
        self.setParent(parent)
        
        # 允许控件拉伸和自适应
        QSizePolicy.Policy.Expanding
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

    def update_plot(self):
        """刷新并紧凑布局绘图区域"""
        self.fig.tight_layout()
        self.draw()
