import sys
from PySide6.QtWidgets import QApplication

# 为了保证在打包或特定目录下能正确引用内部包，我们将当前路径加入 sys.path
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # 强制设置应用级别的样式或字体（可选）
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
