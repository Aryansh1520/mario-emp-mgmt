# ui_helpers.py
from PyQt6.QtWidgets import (
    QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QWidget, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QFont


class CenteredLabel(QLabel):
    """A QLabel that centers its text both horizontally and vertically."""
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class ModernCard(QFrame):
    """A modern card container with shadow and rounded corners."""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("modernCard")
        self.init_ui(title)
        self.setup_style()

    def init_ui(self, title):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(16)

        if title:
            self.title_label = QLabel(title)
            self.title_label.setStyleSheet("""
                font-size: 18px;
                font-weight: 600;
                color: #1f2937;
                margin-bottom: 8px;
            """)
            self.layout.addWidget(self.title_label)

    def setup_style(self):
        self.setStyleSheet("""
            QFrame#modernCard {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e5e7eb;
            }
        """)

        # Add subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

    def add_widget(self, widget):
        self.layout.addWidget(widget)

    def set_content_layout(self, layout):
        self.layout.addLayout(layout)


class GlassButton(QPushButton):
    """Modern glass-morphism style button."""

    def __init__(self, text, primary=False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setMinimumHeight(44)
        self.setup_style()

    def setup_style(self):
        if self.primary:
            style = """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #3b82f6, stop:1 #1d4ed8);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 12px 24px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #2563eb, stop:1 #1e40af);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1d4ed8, stop:1 #1e3a8a);
                }
            """
        else:
            style = """
                QPushButton {
                    background: rgba(255, 255, 255, 0.9);
                    color: #374151;
                    border: 2px solid #e5e7eb;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 12px 24px;
                }
                QPushButton:hover {
                    background: white;
                    border-color: #3b82f6;
                    color: #3b82f6;
                }
                QPushButton:pressed {
                    background: #f8fafc;
                }
            """

        self.setStyleSheet(style)


class ModernInput(QLineEdit):
    """Modern styled input field."""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setMinimumHeight(44)
        self.setup_style()

    def setup_style(self):
        self.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """)


class StatsCard(QFrame):
    """A card for displaying statistics."""

    def __init__(self, title, value, subtitle="", icon="", color="#3b82f6", parent=None):
        super().__init__(parent)
        self.setObjectName("statsCard")
        self.init_ui(title, value, subtitle, icon, color)
        self.setup_style(color)

    def init_ui(self, title, value, subtitle, icon, color):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        # Header with icon and title
        header = QHBoxLayout()

        if icon:
            self.icon_label = QLabel(icon)
            self.icon_label.setStyleSheet(f"""
                font-size: 24px;
                color: {color};
                min-width: 32px;
            """)
            header.addWidget(self.icon_label)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 500;
            color: #6b7280;
        """)
        header.addWidget(self.title_label)
        header.addStretch()
        layout.addLayout(header)

        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {color};
            margin: 4px 0;
        """)
        layout.addWidget(self.value_label)

        # Subtitle
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setStyleSheet("""
                font-size: 12px;
                color: #9ca3af;
            """)
            layout.addWidget(self.subtitle_label)

    def setup_style(self, color):
        self.setStyleSheet(f"""
            QFrame#statsCard {{
                background-color: white;
                border-radius: 12px;
                border-left: 4px solid {color};
                border-top: 1px solid #e5e7eb;
                border-right: 1px solid #e5e7eb;
                border-bottom: 1px solid #e5e7eb;
            }}
        """)

        # Add subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(shadow)

    def update_value(self, new_value: str):
        """Update the main value displayed on the card."""
        self.value_label.setText(new_value)

class ModernLabel(QLabel):
    """Enhanced label with modern styling."""

    def __init__(self, text="", style_type="normal", parent=None):
        super().__init__(text, parent)
        self.setup_style(style_type)

    def setup_style(self, style_type):
        styles = {
            "normal": "color: #374151; font-size: 14px;",
            "title": "color: #1f2937; font-size: 20px; font-weight: 600;",
            "subtitle": "color: #6b7280; font-size: 16px; font-weight: 500;",
            "caption": "color: #9ca3af; font-size: 12px;",
            "success": "color: #059669; font-size: 14px; font-weight: 500;",
            "error": "color: #dc2626; font-size: 14px; font-weight: 500;",
            "warning": "color: #d97706; font-size: 14px; font-weight: 500;",
        }

        self.setStyleSheet(styles.get(style_type, styles["normal"]))


class LoadingSpinner(QWidget):
    """Modern loading spinner widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.angle = 0

        # Animation
        self.animation = QPropertyAnimation(self, b"rotation")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.setLoopCount(-1)  # Infinite loop
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw spinner
        rect = self.rect().adjusted(5, 5, -5, -5)
        painter.setPen(QColor(59, 130, 246))  # Blue color
        painter.drawArc(rect, self.angle * 16, 120 * 16)

        self.angle = (self.angle + 10) % 360


class ActionButton(QPushButton):
    """Floating action button style."""

    def __init__(self, icon="", parent=None):
        super().__init__(icon, parent)
        self.setFixedSize(56, 56)
        self.setup_style()

    def setup_style(self):
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3b82f6, stop:1 #1d4ed8);
                color: white;
                border: none;
                border-radius: 28px;
                font-size: 18px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2563eb, stop:1 #1e40af);
            }
            QPushButton:pressed {
            }
        """)

        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(59, 130, 246, 100))
        self.setGraphicsEffect(shadow)
