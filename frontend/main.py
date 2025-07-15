import sys

from PyQt6.QtWidgets import QApplication, QLabel, QWidget

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("PyQt6 기본 테스트")
window.setGeometry(100, 100, 300, 200)

label = QLabel("Hello PyQt6!", parent=window)
label.move(100, 80)

window.show()
sys.exit(app.exec())
