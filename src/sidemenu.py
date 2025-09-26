# modern_sidebar.py
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton , QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from pathlib import Path
from os import sys
HERE = Path(__file__).parent

if hasattr(sys, "_MEIPASS"):
    LOGO_PATH = Path(sys._MEIPASS) / "assets" / "logo.png"
else:
    LOGO_PATH = HERE.parent / "assets" / "logo.png"
    
class SidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCheckable(True)
        self.setObjectName("sidebarButton")
        self.setMinimumHeight(50)

        # Styling
        self.setStyleSheet("""
            QPushButton#sidebarButton {
                background: transparent;
                border: none;
                color: #64748b;
                font-size: 15px;
                font-weight: 500;
                text-align: left;
                padding: 12px 24px;
                border-radius: 12px;
            }
            QPushButton#sidebarButton:hover {
                background: rgba(59, 130, 246, 0.1);
                color: #3b82f6;
            }
            QPushButton#sidebarButton:checked {
                background: rgba(59, 130, 246, 0.15);
                color: #1e3a8a;
                font-weight: 600;
            }
        """)


class ModernSidebar(QFrame):
    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(280)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(8)

        # ===== Brand / Logo =====
        brand_frame = QFrame()
        brand_layout = QHBoxLayout(brand_frame)
        brand_layout.setContentsMargins(20, 0, 20, 30)
        brand_layout.setSpacing(12)
        brand_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Logo
        logo_label = QLabel()
        logo_pix = QPixmap(str(LOGO_PATH))
        if not LOGO_PATH.exists():
            pass
            #QMessageBox.warning(None, "Debug", f"Logo path does NOT exist:\n{LOGO_PATH}")
        else:
            pass
            #QMessageBox.information(None, "Debug", f"Logo path exists:\n{LOGO_PATH}")

        if logo_pix.isNull():
            #QMessageBox.warning(None, "Debug", f"Failed to load QPixmap from:\n{LOGO_PATH}")
            logo_label.setText("🏥")  # fallback
            logo_label.setStyleSheet("font-size: 24px;")
        else:
            logo_pix = logo_pix.scaled(
                40, 40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(logo_pix)
            #QMessageBox.information(None, "Debug", f"Successfully loaded QPixmap:\n{LOGO_PATH}")


        brand_layout.addWidget(logo_label)

        # Company Name
        company_label = QLabel("Mariomed\nPharmaceuticals")
        company_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #1e293b;
            line-height: 1.2;
        """)
        brand_layout.addWidget(company_label)
        brand_layout.addStretch()

        layout.addWidget(brand_frame)

        # ===== Navigation Buttons =====
        self.nav_buttons = []

        employees_btn = SidebarButton("Employees")
        payslips_btn = SidebarButton("Payslips")

        self.nav_buttons.extend([employees_btn, payslips_btn])

        for i, btn in enumerate(self.nav_buttons):
            btn.clicked.connect(lambda checked, idx=i: self.on_button_clicked(idx))
            layout.addWidget(btn)

        # Select first button by default
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)

        layout.addStretch()

        # ===== Footer =====
        footer = QLabel("v1.0 • Modern UI")
        footer.setStyleSheet("""
            color: #94a3b8;
            font-size: 11px;
            padding: 12px 20px;
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

        # Sidebar styling
        self.setStyleSheet("""
            QFrame#sidebar {
                background: #ffffff;
                border-right: 1px solid #e2e8f0;
            }
        """)

    def on_button_clicked(self, index):
        # Uncheck all other buttons
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.page_changed.emit(index)
