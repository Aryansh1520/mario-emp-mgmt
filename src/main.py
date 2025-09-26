# main.py
import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QStackedWidget, QFileDialog, QMessageBox, QComboBox,
    QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QIcon, QPixmap, QFont, QPainter, QPainterPath , QGuiApplication
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal

# local modules
from db import ensure_db
from employees_crud import ModernEmployeesWidget, Employee
from payslip_generator import ModernPayslipGenerator
from ui_helpers import ModernCard, GlassButton, ModernInput
from PayslipPage import PayslipPage
from sidemenu import ModernSidebar, SidebarButton

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
STYLES_DIR = BASE_DIR / "styles"
DB_PATH = BASE_DIR / "data" / "employees.db"




class ModernHeader(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        self.setObjectName("header")
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 0, 30, 0)

        # Page title
        self.title_label = QLabel("Employee Management")
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #1e293b;
        """)
        layout.addWidget(self.title_label)

        layout.addStretch()

        # Action buttons
        self.action_layout = QHBoxLayout()
        layout.addLayout(self.action_layout)

        # Header styling
        self.setStyleSheet("""
            QFrame#header {
                background: white;
                border-bottom: 1px solid #e2e8f0;
            }
        """)

    def set_title(self, title):
        self.title_label.setText(title)

    def clear_actions(self):
        while self.action_layout.count():
            child = self.action_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def add_action_button(self, text, callback, primary=False):
        btn = GlassButton(text, primary=primary)
        btn.clicked.connect(callback)
        self.action_layout.addWidget(btn)
        return btn



class ModernMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mariomed Payslip Generator")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(self.get_main_stylesheet())

        # Ensure database
        ensure_db(DB_PATH)

        self.init_ui()

    def get_main_stylesheet(self):
        return """
            QWidget {
                background-color: #f8fafc;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                color: #1e293b;
            }

            QScrollArea {
                border: none;
                background: transparent;
            }

            QMessageBox {
                background-color: white;
                color: #1e293b;
            }
        """

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = ModernSidebar()
        self.sidebar.page_changed.connect(self.on_page_changed)
        layout.addWidget(self.sidebar)

        # Main content area
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header
        self.header = ModernHeader()
        content_layout.addWidget(self.header)

        # Page stack
        self.page_stack = QStackedWidget()

        # Create pages
        self.employees_page = ModernEmployeesWidget(DB_PATH)
        self.payslip_page = PayslipPage(DB_PATH)

        self.page_stack.addWidget(self.employees_page)
        self.page_stack.addWidget(self.payslip_page)

        content_layout.addWidget(self.page_stack)
        layout.addWidget(content_frame)

        # Set initial page
        self.on_page_changed(0)

    def on_page_changed(self, index):
        self.page_stack.setCurrentIndex(index)

        if index == 0:
            self.header.set_title("👥 Employee Management")
        elif index == 1:
            self.header.set_title("📄 Payslip Generation")
            # Refresh employee list when switching to payslip page
            self.payslip_page.refresh_employee_list()
def main():
    app = QApplication(sys.argv)

    # --- App-level properties ---
    app.setApplicationName("Mariomed Payslip Generator")
    app.setApplicationVersion("1.0")

    # --- Icon path ---
    icon_path = ASSETS_DIR / "logo.png"
    if not icon_path.exists():
        print("Warning: Icon not found:", icon_path)

    # Set icon globally for app (taskbar)
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
        QGuiApplication.setWindowIcon(QIcon(str(icon_path)))  # ensures taskbar/dock icon

    # --- Main Window ---
    window = ModernMainWindow()
    window.setWindowTitle("Mariomed Payslip Generator")

    # Also set window-level icon (title bar)
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
