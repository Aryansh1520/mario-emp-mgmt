from PyQt6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QScrollArea,
    QTextEdit,
    QComboBox,
    QDoubleSpinBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Assuming these are your custom widgets
from ui_helpers import (
    ModernCard,
    ModernInput,
    ModernLabel,
    GlassButton
)

# Your Employee model
from models import Employee


class ModernEmployeeFormDialog(QDialog):
    """Modern dialog for adding/editing employees (static info + earnings/deductions + status)."""

    def __init__(self, parent=None, employee: "Employee" = None):
        super().__init__(parent)
        self.setWindowTitle("Employee Details" if employee else "New Employee")
        self.setMinimumSize(600, 750)
        self.employee = employee or Employee()
        self.init_ui()
        self.setup_style()

    def setup_style(self):
        self.setStyleSheet("""
            QDialog { background-color: #f8fafc; }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #3b82f6;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
            QScrollBar::add-page, QScrollBar::sub-page { background: none; }
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # --- Header ---
        header_layout = QHBoxLayout()
        title = QLabel("👤 Employee Information")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #1f2937; margin-bottom: 8px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # --- Scroll Area ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(24)

        # --- Basic Info Card ---
        basic_card = ModernCard("Basic Information")
        basic_layout = QGridLayout()
        basic_layout.setSpacing(16)

        # Employee Code
        basic_layout.addWidget(ModernLabel("Employee Code:", "subtitle"), 0, 0)
        self.code_edit = ModernInput()
        self.code_edit.setText(self.employee.emp_code or "")
        basic_layout.addWidget(self.code_edit, 0, 1)

        # Full Name
        basic_layout.addWidget(ModernLabel("Full Name:", "subtitle"), 0, 2)
        self.name_edit = ModernInput()
        self.name_edit.setText(self.employee.name or "")
        basic_layout.addWidget(self.name_edit, 0, 3)

        # Designation
        basic_layout.addWidget(ModernLabel("Designation:", "subtitle"), 1, 0)
        self.designation_edit = ModernInput()
        self.designation_edit.setText(self.employee.designation or "")
        basic_layout.addWidget(self.designation_edit, 1, 1)

        # Department
        basic_layout.addWidget(ModernLabel("Department:", "subtitle"), 1, 2)
        self.department_edit = ModernInput()
        self.department_edit.setText(self.employee.department or "")
        basic_layout.addWidget(self.department_edit, 1, 3)

        # Joining Date
        basic_layout.addWidget(ModernLabel("Joining Date:", "subtitle"), 2, 0)
        self.joining_edit = ModernInput()
        self.joining_edit.setText(self.employee.joining_date or "")
        self.joining_edit.setPlaceholderText("DD/MM/YYYY")
        basic_layout.addWidget(self.joining_edit, 2, 1)

        # Status
        basic_layout.addWidget(ModernLabel("Status:", "subtitle"), 2, 2)
        from PyQt6.QtWidgets import QComboBox
        self.status_combo = QComboBox()
        if self.employee.id:  # Edit mode
            self.status_combo.addItems(["Active", "Inactive"])
            self.status_combo.setCurrentText(getattr(self.employee, "status", "Active"))
            self.status_combo.setEnabled(True)
        else:  # Add mode
            self.status_combo.addItem("Active")
            self.status_combo.setCurrentText("Active")
            self.status_combo.setEnabled(False)
        basic_layout.addWidget(self.status_combo, 2, 3)

        basic_card.set_content_layout(basic_layout)
        form_layout.addWidget(basic_card)

        # --- Bank Card ---
        bank_card = ModernCard("🏦 Bank Details")
        bank_layout = QGridLayout()
        bank_layout.setSpacing(16)

        self.bank_edit = ModernInput()
        self.bank_edit.setText(self.employee.bank_account or "")
        bank_layout.addWidget(ModernLabel("Bank Account:", "subtitle"), 0, 0)
        bank_layout.addWidget(self.bank_edit, 0, 1)

        self.ifsc_edit = ModernInput()
        self.ifsc_edit.setText(self.employee.ifsc or "")
        bank_layout.addWidget(ModernLabel("IFSC Code:", "subtitle"), 0, 2)
        bank_layout.addWidget(self.ifsc_edit, 0, 3)

        self.pan_edit = ModernInput()
        self.pan_edit.setText(self.employee.pan or "")
        bank_layout.addWidget(ModernLabel("PAN Number:", "subtitle"), 1, 0)
        bank_layout.addWidget(self.pan_edit, 1, 1)

        bank_card.set_content_layout(bank_layout)
        form_layout.addWidget(bank_card)

        # --- Earnings & Deductions Card ---
        finance_card = ModernCard("💰 Earnings & Deductions (Static)")
        finance_layout = QGridLayout()
        finance_layout.setSpacing(16)

        # Basic
        finance_layout.addWidget(ModernLabel("Basic:", "subtitle"), 0, 0)
        self.basic_edit = QDoubleSpinBox()
        self.basic_edit.setMaximum(10000000)
        self.basic_edit.setValue(getattr(self.employee, "basic", 0.0))
        finance_layout.addWidget(self.basic_edit, 0, 1)

        # HRA
        finance_layout.addWidget(ModernLabel("HRA:", "subtitle"), 0, 2)
        self.hra_edit = QDoubleSpinBox()
        self.hra_edit.setMaximum(10000000)
        self.hra_edit.setValue(getattr(self.employee, "hra", 0.0))
        finance_layout.addWidget(self.hra_edit, 0, 3)

        # LTA
        finance_layout.addWidget(ModernLabel("LTA:", "subtitle"), 1, 0)
        self.LTA_edit = QDoubleSpinBox()
        self.LTA_edit.setMaximum(10000000)
        self.LTA_edit.setValue(getattr(self.employee, "LTA", 0.0))
        finance_layout.addWidget(self.LTA_edit, 1, 1)

        # Special Allowance
        finance_layout.addWidget(ModernLabel("Special Allowance:", "subtitle"), 1, 2)
        self.special_edit = QDoubleSpinBox()
        self.special_edit.setMaximum(10000000)
        self.special_edit.setValue(getattr(self.employee, "special_allowance", 0.0))
        finance_layout.addWidget(self.special_edit, 1, 3)

        # Income Tax
        finance_layout.addWidget(ModernLabel("Income Tax:", "subtitle"), 2, 0)
        self.tax_edit = QDoubleSpinBox()
        self.tax_edit.setMaximum(10000000)
        self.tax_edit.setValue(getattr(self.employee, "income_tax", 0.0))
        finance_layout.addWidget(self.tax_edit, 2, 1)

        finance_card.set_content_layout(finance_layout)
        form_layout.addWidget(finance_card)

        # --- Notes Card ---
        notes_card = ModernCard("📝 Additional Notes")
        self.notes_edit = QTextEdit(getattr(self.employee, "notes", "") or "")
        self.notes_edit.setMaximumHeight(100)
        self.notes_edit.setStyleSheet("""
            QTextEdit { background-color: white; border: 2px solid #e5e7eb; border-radius: 12px; padding: 12px 16px; font-size: 14px; color: #374151; }
            QTextEdit:focus { border-color: #3b82f6; }
        """)
        notes_card.add_widget(self.notes_edit)
        form_layout.addWidget(notes_card)

        scroll.setWidget(form_widget)
        layout.addWidget(scroll)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_btn = GlassButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        save_btn = GlassButton("💾 Save Employee", primary=True)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def get_employee(self) -> "Employee":
        """Return employee object including static earnings & deductions and status."""
        e = Employee(
            id=getattr(self.employee, "id", None),
            emp_code=self.code_edit.text().strip(),
            name=self.name_edit.text().strip(),
            designation=self.designation_edit.text().strip(),
            department=self.department_edit.text().strip(),
            bank_account=self.bank_edit.text().strip(),
            ifsc=self.ifsc_edit.text().strip(),
            pan=self.pan_edit.text().strip(),
            joining_date=self.joining_edit.text().strip(),
            notes=self.notes_edit.toPlainText().strip(),
            basic=self.basic_edit.value(),
            hra=self.hra_edit.value(),
            LTA=self.LTA_edit.value(),
            special_allowance=self.special_edit.value(),
            income_tax=self.tax_edit.value(),
            status=self.status_combo.currentText()
        )
        return e
