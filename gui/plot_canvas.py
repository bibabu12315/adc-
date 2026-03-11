from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas 
from matplotlib.figure import Figure
from PySide6.QtWidgets import QSizePolicy

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # 始化 Matplotlib Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        super(PlotCanvas, self).__init__(self.fig)
        self.setParent(parent)

        # 伸和自适用
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)        
        self.updateGeometry()

    def update_plot(self):
        self.fig.tight_layout()
        self.draw()