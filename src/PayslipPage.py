# payslip_page.py
import sys, os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QFileDialog, QMessageBox, QInputDialog, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor
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
        self.setup_styles()

    def setup_styles(self):
        """Apply modern styling to the widget."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)

        # Page Header
        # header_layout = QHBoxLayout()
        # title = QLabel("📄 Payslip Management")
        # title.setStyleSheet("""
        #     font-size: 24px;
        #     font-weight: 700;
        #     color: #1f2937;
        #     margin-bottom: 8px;
        #     padding: 0;
        # """)
        # header_layout.addWidget(title)
        # header_layout.addStretch()
        # layout.addLayout(header_layout)

        # Main content in horizontal layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(24)

        # Left column - Controls
        left_column = QVBoxLayout()
        left_column.setSpacing(20)

        # ===== Employee Selection =====
        selection_card = ModernCard("👤 Employee Selection")
        sel_layout = QVBoxLayout()
        sel_layout.setSpacing(16)

        # Employee dropdown with label
        employee_label = QLabel("Select Employee:")
        employee_label.setStyleSheet("""
            font-weight: 600;
            color: #374151;
            font-size: 14px;
            margin-bottom: 4px;
        """)
        sel_layout.addWidget(employee_label)

        dropdown_layout = QHBoxLayout()
        dropdown_layout.setSpacing(12)

        self.employee_combo = QComboBox()
        self.employee_combo.setMinimumHeight(48)
        self.employee_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 14px;
                color: #374151;
                font-weight: 500;
            }
            QComboBox:hover {
                border-color: #3b82f6;
                background: #f8fafc;
            }
            QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 32px;
                subcontrol-origin: padding;
                subcontrol-position: center right;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #6b7280;
                margin: 4px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #3b82f6;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                selection-background-color: rgba(59, 130, 246, 0.1);
                padding: 4px;
            }
        """)
        dropdown_layout.addWidget(self.employee_combo, 1)

        refresh_btn = GlassButton("🔄 Refresh")
        refresh_btn.setMinimumHeight(48)
        refresh_btn.clicked.connect(self.refresh_employee_list)
        dropdown_layout.addWidget(refresh_btn)

        sel_layout.addLayout(dropdown_layout)

        # Quick stats
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #bae6fd;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(12, 12, 12, 12)

        self.employee_count_label = QLabel("Total Employees: Loading...")
        self.employee_count_label.setStyleSheet("""
            color: #0369a1;
            font-size: 13px;
            font-weight: 500;
        """)
        stats_layout.addWidget(self.employee_count_label)

        sel_layout.addWidget(stats_frame)
        selection_card.set_content_layout(sel_layout)
        left_column.addWidget(selection_card)

        # ===== Actions =====
        actions_card = ModernCard("⚡ Quick Actions")
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(12)

        self.generate_btn = GlassButton("📄 Generate PDF Payslip", primary=True)
        self.generate_btn.setMinimumHeight(52)
        self.generate_btn.clicked.connect(self.generate_payslip)
        actions_layout.addWidget(self.generate_btn)



        # Add some help text
        help_text = QLabel("💡 Select an employee above to preview their payslip details")
        help_text.setStyleSheet("""
            color: #6b7280;
            font-size: 12px;
            padding: 8px 12px;
            background: #f9fafb;
            border-radius: 6px;
            border-left: 3px solid #3b82f6;
        """)
        help_text.setWordWrap(True)
        actions_layout.addWidget(help_text)

        actions_card.set_content_layout(actions_layout)
        left_column.addWidget(actions_card)

        left_column.addStretch()

        # Left column wrapper
        left_widget = QWidget()
        left_widget.setLayout(left_column)
        left_widget.setMaximumWidth(400)
        left_widget.setMinimumWidth(350)

        main_layout.addWidget(left_widget)

        # Right column - Preview (with scroll)
        self.setup_preview_area()
        main_layout.addWidget(self.preview_widget, 1)  # Give it more space

        layout.addLayout(main_layout)

        # Connect signals
        self.employee_combo.currentIndexChanged.connect(self.update_preview)

        # Initial load
        self.refresh_employee_list()

    def setup_preview_area(self):
        """Create the scrollable preview area with modern styling."""
        self.preview_widget = ModernCard("📋 Payslip Preview")

        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Modern scrollbar styling
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0, 0, 0, 0.05);
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(59, 130, 246, 0.6);
                min-height: 20px;
                border-radius: 4px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(59, 130, 246, 0.8);
            }
            QScrollBar::handle:vertical:pressed {
                background: rgba(59, 130, 246, 1.0);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # Preview content widget
        self.preview_content = QLabel()
        self.preview_content.setWordWrap(True)
        self.preview_content.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.preview_content.setMinimumHeight(400)

        # Set initial empty state
        self.set_empty_preview()

        self.scroll_area.setWidget(self.preview_content)
        self.preview_widget.add_widget(self.scroll_area)

    def set_empty_preview(self):
        """Set the preview to show empty state."""
        empty_html = """
        <div style="
            text-align: center;
            padding: 60px 40px;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 16px;
            border: 2px dashed #cbd5e1;
            margin: 20px;
        ">
            <div style="
                font-size: 48px;
                margin-bottom: 16px;
                color: #94a3b8;
            ">📄</div>
            <h3 style="
                color: #475569;
                margin: 0 0 8px 0;
                font-size: 18px;
                font-weight: 600;
            ">No Employee Selected</h3>
            <p style="
                color: #64748b;
                margin: 0;
                font-size: 14px;
                line-height: 1.5;
            ">Choose an employee from the dropdown to preview their payslip details</p>
        </div>
        """
        self.preview_content.setText(empty_html)

    # =========================
    # Employee Dropdown
    # =========================
    def refresh_employee_list(self):
        employees = get_all_employees(self.db_path)
        self.employee_combo.clear()
        self.employee_combo.addItem("-- Select Employee --", userData=None)

        for emp in employees:
            status_indicator = "🟢" if emp.get('status', '').lower() == 'active' else "🔴"
            display = f"{status_indicator} {emp.get('emp_code', emp.get('id', ''))} - {emp.get('name', '')}"
            self.employee_combo.addItem(display, userData=emp)

        # Update employee count
        active_count = len([e for e in employees if e.get('status', '').lower() == 'active'])
        total_count = len(employees)
        self.employee_count_label.setText(f"Total Employees: {total_count} ({active_count} active)")

        self.update_preview()

    def current_employee(self):
        idx = self.employee_combo.currentIndex()
        if idx <= 0:  # 0 is "Select Employee"
            return None
        return self.employee_combo.itemData(idx)

    # =========================
    # Preview Updates
    # =========================
    def update_preview(self):
        emp = self.current_employee()
        if not emp:
            self.set_empty_preview()
            return

        # Compute financials using updated function
        fin = compute_financials(emp)

        # Create detailed preview
        status_color = "#059669" if emp.get('status', '').lower() == 'active' else "#dc2626"
        status_text = "Active" if emp.get('status', '').lower() == 'active' else "Inactive"
        status_icon = "🟢" if emp.get('status', '').lower() == 'active' else "🔴"

        preview_html = f"""
        <div style="padding: 24px; background: white; margin: 20px; border-radius: 16px; border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <!-- Header -->
            <div style="border-bottom: 2px solid #f1f5f9; padding-bottom: 20px; margin-bottom: 24px;">
                <h2 style="color: #1f2937; margin: 0 0 8px 0; font-size: 22px; font-weight: 700;">
                    📋 Payslip Preview
                </h2>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: {status_color}; font-weight: 600; font-size: 14px;">
                        {status_icon} {status_text}
                    </span>
                </div>
            </div>

            <!-- Employee Details -->
            <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 20px; border-radius: 12px; margin-bottom: 24px;">
                <h3 style="color: #374151; margin: 0 0 16px 0; font-size: 16px; font-weight: 600;">👤 Employee Information</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 14px;">
                    <div><span style="color: #6b7280; font-weight: 500;">Name:</span> <span style="color: #1f2937; font-weight: 600;">{emp.get('name', 'N/A')}</span></div>
                    <div><span style="color: #6b7280; font-weight: 500;">Employee Code:</span> <span style="color: #1f2937; font-weight: 600;">{emp.get('emp_code', emp.get('id', 'N/A'))}</span></div>
                    <div><span style="color: #6b7280; font-weight: 500;">Designation:</span> <span style="color: #1f2937;">{emp.get('designation', 'N/A')}</span></div>
                    <div><span style="color: #6b7280; font-weight: 500;">Department:</span> <span style="color: #1f2937;">{emp.get('department', 'N/A')}</span></div>
                    <div><span style="color: #6b7280; font-weight: 500;">Joining Date:</span> <span style="color: #1f2937;">{emp.get('joining_date', 'N/A')}</span></div>
                    <div><span style="color: #6b7280; font-weight: 500;">Pay Period:</span> <span style="color: #7c3aed; font-weight: 600; font-style: italic;">To be entered during generation</span></div>
                </div>
            </div>

            <!-- Earnings Breakdown -->
            <div style="background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%); padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #059669;">
                <h3 style="color: #065f46; margin: 0 0 16px 0; font-size: 16px; font-weight: 600;">💰 Earnings Breakdown</h3>
                <div style="font-size: 14px; line-height: 1.8;">
                    <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                        <span style="color: #374151;">Basic Salary:</span>
                        <span style="color: #059669; font-weight: 600;">₹{fin['basic']:,.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                        <span style="color: #374151;">HRA:</span>
                        <span style="color: #059669; font-weight: 600;">₹{fin['hra']:,.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                        <span style="color: #374151;">LTA:</span>
                        <span style="color: #059669; font-weight: 600;">₹{fin['LTA']:,.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                        <span style="color: #374151;">Special Allowance:</span>
                        <span style="color: #059669; font-weight: 600;">₹{fin['special_allowance']:,.2f}</span>
                    </div>
                </div>
            </div>

            <!-- Deductions -->
            <div style="background: linear-gradient(135deg, #fef2f2 0%, #fef7f7 100%); padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #dc2626;">
                <h3 style="color: #991b1b; margin: 0 0 16px 0; font-size: 16px; font-weight: 600;">💳 Deductions</h3>
                <div style="font-size: 14px; line-height: 1.8;">
                    <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                        <span style="color: #374151;">Income Tax:</span>
                        <span style="color: #dc2626; font-weight: 600;">₹{fin['income_tax']:,.2f}</span>
                    </div>
                </div>
            </div>

            <!-- Summary -->
            <div style="background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%); padding: 24px; border-radius: 12px; border: 2px solid #3b82f6;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="color: #1e40af; font-size: 16px; font-weight: 600;">💵 Gross Pay:</span>
                    <span style="color: #1e40af; font-size: 18px; font-weight: 700;">₹{fin['gross']:,.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid #bfdbfe;">
                    <span style="color: #1e40af; font-size: 18px; font-weight: 700;">💸 Net Pay:</span>
                    <span style="color: #1e40af; font-size: 24px; font-weight: 900;">₹{fin['net']:,.2f}</span>
                </div>
            </div>

            <!-- Bank Details (if available) -->
            {f'''
            <div style="background: #f8fafc; padding: 16px; border-radius: 8px; margin-top: 20px; border: 1px solid #e2e8f0;">
                <h4 style="color: #475569; margin: 0 0 12px 0; font-size: 14px; font-weight: 600;">🏦 Bank Details</h4>
                <div style="font-size: 13px; line-height: 1.6; color: #64748b;">
                    <div>Account: {emp.get('bank_account', 'N/A')}</div>
                    <div>IFSC: {emp.get('ifsc', 'N/A')}</div>
                    <div>PAN: {emp.get('pan', 'N/A')}</div>
                </div>
            </div>
            ''' if emp.get('bank_account') or emp.get('ifsc') or emp.get('pan') else ''}

            <!-- Notes (if available) -->
            {f'''
            <div style="background: #fffbeb; padding: 16px; border-radius: 8px; margin-top: 16px; border-left: 3px solid #f59e0b;">
                <h4 style="color: #92400e; margin: 0 0 8px 0; font-size: 14px; font-weight: 600;">📝 Notes</h4>
                <p style="color: #78350f; font-size: 13px; margin: 0; line-height: 1.5;">{emp.get('notes', '')}</p>
            </div>
            ''' if emp.get('notes', '').strip() else ''}
        </div>
        """

        self.preview_content.setText(preview_html)

    # =========================
    # PDF Generation
    # =========================

    def generate_payslip(self):
        desktop_dir = str(Path.home() / "Desktop")

        emp = self.current_employee()
        if not emp:
            QMessageBox.warning(self, "No Selection", "Please select an employee first.")
            return

        pay_period, ok = QInputDialog.getText(
            self, "Pay Period",
            "Enter Pay Period (e.g., December 2025):",
            text="December 2025"
        )
        if not ok or not pay_period.strip():
            return
        pay_period = pay_period.strip()

        out_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            desktop_dir  # open at Desktop
        )
        if not out_dir:
            return

        try:
            generator = ModernPayslipGenerator()
            filename = generator.generate_pdf(self.db_path, emp['id'], pay_period, output_dir=out_dir)
            QMessageBox.information(
                self, "Success",
                f"✅ Payslip generated successfully!\n\nSaved to:\n{filename}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"❌ Failed to generate payslip:\n\n{str(e)}"
            )

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
