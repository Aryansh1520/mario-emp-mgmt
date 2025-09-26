# payslip_page.py
import sys, os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QFileDialog, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from db import get_all_employees, compute_financials
from payslip_generator import ModernPayslipGenerator
from ui_helpers import ModernCard, GlassButton  # your existing UI components

BASE_DIR = Path(__file__).parent


class PayslipPage(QWidget):
    """Payslip management page: select employee, preview, and generate PDF."""

    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)

        # ===== Employee Selection =====
        selection_card = ModernCard("Select Employee")
        sel_layout = QVBoxLayout()
        dropdown_layout = QHBoxLayout()
        dropdown_layout.setSpacing(16)

        employee_label = QLabel("Employee:")
        employee_label.setStyleSheet("font-weight: 500; color: #374151;")
        dropdown_layout.addWidget(employee_label)

        self.employee_combo = QComboBox()
        self.employee_combo.setMinimumHeight(44)
        self.employee_combo.setStyleSheet("""
            QComboBox { background: white; border: 2px solid #e5e7eb; border-radius: 12px; padding: 8px 16px; font-size: 14px; color: #374151; }
            QComboBox:hover { border-color: #3b82f6; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox::down-arrow { image: none; }
        """)
        dropdown_layout.addWidget(self.employee_combo, 1)

        refresh_btn = GlassButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_employee_list)
        dropdown_layout.addWidget(refresh_btn)

        sel_layout.addLayout(dropdown_layout)
        selection_card.set_content_layout(sel_layout)
        layout.addWidget(selection_card)

        # ===== Payslip Preview =====
        preview_card = ModernCard("Payslip Preview")
        self.preview_content = QLabel("Select an employee to preview payslip")
        self.preview_content.setStyleSheet("""
            color: #6b7280;
            font-size: 15px;
            padding: 20px;
            background: #f9fafb;
            border-radius: 8px;
            border: 2px dashed #d1d5db;
        """)
        self.preview_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_content.setMinimumHeight(200)
        preview_card.add_widget(self.preview_content)
        layout.addWidget(preview_card)

        # ===== Actions =====
        actions_card = ModernCard("Actions")
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(16)

        self.generate_btn = GlassButton("📄 Generate PDF", primary=True)
        self.generate_btn.clicked.connect(self.generate_payslip)
        actions_layout.addWidget(self.generate_btn)

        self.open_folder_btn = GlassButton("📁 Open Output Folder")
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        actions_layout.addWidget(self.open_folder_btn)

        actions_layout.addStretch()
        actions_card.set_content_layout(actions_layout)
        layout.addWidget(actions_card)

        layout.addStretch()

        # Connect signals
        self.employee_combo.currentIndexChanged.connect(self.update_preview)

        # Initial load
        self.refresh_employee_list()

    # =========================
    # Employee Dropdown
    # =========================
    def refresh_employee_list(self):
        employees = get_all_employees(self.db_path)
        self.employee_combo.clear()
        for emp in employees:
            display = f"{emp.get('emp_code', emp.get('id', ''))} - {emp.get('name', '')}"
            self.employee_combo.addItem(display, userData=emp)
        self.update_preview()

    def current_employee(self):
        idx = self.employee_combo.currentIndex()
        if idx < 0:
            return None
        return self.employee_combo.itemData(idx)

    # =========================
    # Preview
    # =========================

    # =========================
    # PDF Generation
    # =========================
    def generate_payslip(self):
        emp = self.current_employee()
        if not emp:
            QMessageBox.warning(self, "No Selection", "Please select an employee first.")
            return

        pay_period, ok = QInputDialog.getText(self, "Pay Period", "Enter Pay Period (e.g., December 2025):")
        if not ok or not pay_period.strip():
            return
        pay_period = pay_period.strip()

        out_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory", str(BASE_DIR / "output"))
        if not out_dir:
            return

        try:
            generator = ModernPayslipGenerator()
            filename = generator.generate_pdf(self.db_path, emp['id'], pay_period, output_dir=out_dir)
            QMessageBox.information(self, "Success", f"✅ Payslip generated!\n\nSaved to: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Failed to generate payslip:\n\n{str(e)}")

    # =========================
    # Open Folder
    # =========================
    def open_output_folder(self):
        output_dir = BASE_DIR / "output"
        output_dir.mkdir(exist_ok=True)
        if sys.platform.startswith("win"):
            os.startfile(str(output_dir))
        elif sys.platform.startswith("darwin"):
            os.system(f'open "{output_dir}"')
        else:
            os.system(f'xdg-open "{output_dir}"')

    def update_preview(self):
      emp = self.current_employee()
      if not emp:
          self.preview_content.setText("Select an employee to preview payslip")
          self.preview_content.setStyleSheet("""
              color: #6b7280;
              font-size: 15px;
              padding: 20px;
              background: #f9fafb;
              border-radius: 8px;
              border: 2px dashed #d1d5db;
          """)
          return

      # Compute financials using updated function
      fin = compute_financials(emp)

      preview_html = f"""
      <div style="background: white; padding: 20px; border-radius: 12px; border: 1px solid #e5e7eb;">
          <h3 style="color: #1f2937; margin: 0 0 16px 0; font-size: 18px;">📋 Payslip Preview</h3>
          <table style="width: 100%; font-size: 14px; line-height: 1.6;">
              <tr><td style="color: #6b7280; width: 120px;"><b>Employee:</b></td><td style="color: #1f2937;">{emp.get('name', '')}</td></tr>
              <tr><td style="color: #6b7280;"><b>ID/Code:</b></td><td style="color: #1f2937;">{emp.get('emp_code', emp.get('id', ''))}</td></tr>
              <tr><td style="color: #6b7280;"><b>Designation:</b></td><td style="color: #1f2937;">{emp.get('designation', '')}</td></tr>
              <tr><td style="color: #6b7280;"><b>Department:</b></td><td style="color: #1f2937;">{emp.get('department', '')}</td></tr>
              <tr><td style="color: #6b7280;"><b>Pay Period:</b></td><td style="color: #1f2937;">Enter Pay Period</td></tr>
              <tr><td colspan="2" style="height: 12px;"></td></tr>
              <tr><td style="color: #059669;"><b>💰 Gross Pay:</b></td><td style="color: #059669; font-weight: 600;">₹{fin['gross']:,.2f}</td></tr>
              <tr><td style="color: #dc2626;"><b>💳 Deductions (Income Tax):</b></td><td style="color: #dc2626;">₹{fin['income_tax']:,.2f}</td></tr>
              <tr><td style="color: #3b82f6;"><b>💵 Net Pay:</b></td><td style="color: #3b82f6; font-weight: 700; font-size: 16px;">₹{fin['net']:,.2f}</td></tr>
          </table>
      </div>
      """
      self.preview_content.setText(preview_html)
      self.preview_content.setStyleSheet("background: transparent; border: none; padding: 0;")
