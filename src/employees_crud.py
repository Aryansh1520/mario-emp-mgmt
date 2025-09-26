# employees_crud.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QLabel, QLineEdit, QFormLayout, QDialogButtonBox, QSpinBox,
    QDoubleSpinBox, QComboBox, QHeaderView, QAbstractItemView, QFrame, QGridLayout,
    QScrollArea, QTextEdit, QDateEdit, QCheckBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette
from db import (
    get_conn,
    get_all_employees,
    get_active_employees,
    get_departments,
    compute_financials,
    insert_employee,
    update_employee,
    delete_employee
)

from ModernEmployeeFormDialog import ModernEmployeeFormDialog

from models import Employee
from ui_helpers import ModernCard, GlassButton, ModernInput, StatsCard, ModernLabel, ActionButton

class ModernEmployeesWidget(QWidget):
    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.init_ui()

    def load_stats(self):
        # Total employees (all)
        all_emps = get_all_employees(self.db_path)
        total_employees = len(all_emps)

        # Total payroll (sum of net pay for active employees)
        active_emps = get_active_employees(self.db_path)
        total_payroll = sum(compute_financials(emp)["net"] for emp in active_emps)

        # Total unique departments
        departments = get_departments(self.db_path)
        total_departments = len(departments)

        return total_employees, total_payroll, total_departments
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)

        # Stats cards row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        # We'll update these with real data
        self.total_employees_card = StatsCard("Total Employees", "0", "Active", "👥", "#3b82f6")
        self.total_salary_card = StatsCard("Total Payroll", "₹0", "Per Month", "💰", "#059669")
        self.departments_card = StatsCard("Departments", "0", "Active", "🏢", "#7c3aed")

        stats_layout.addWidget(self.total_employees_card)
        stats_layout.addWidget(self.total_salary_card)
        stats_layout.addWidget(self.departments_card)

        layout.addLayout(stats_layout)
        total_employees, total_payroll, total_departments = self.load_stats()
        self.total_employees_card.update_value(str(total_employees))
        self.total_salary_card.update_value(f"₹{total_payroll:,.2f}")
        self.departments_card.update_value(str(total_departments))
        # Main content card
        main_card = ModernCard("Employee Directory")
        main_layout = QVBoxLayout()

        # Search and filters
        search_layout = QHBoxLayout()
        search_layout.setSpacing(16)

        # Search input
        self.search_input = ModernInput("🔍 Search employees...")
        self.search_input.textChanged.connect(self.filter_employees)
        search_layout.addWidget(self.search_input, 2)

        # Department filter
        dept_label = QLabel("Department:")
        dept_label.setStyleSheet("font-weight: 500; color: #374151;")
        search_layout.addWidget(dept_label)

        self.dept_filter = QComboBox()
        self.dept_filter.setMinimumHeight(44)
        self.dept_filter.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 14px;
                color: #374151;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #3b82f6;
            }
        """)
        self.dept_filter.addItem("All Departments")
        self.dept_filter.currentTextChanged.connect(self.filter_employees)
        search_layout.addWidget(self.dept_filter)

        # Action buttons
        add_btn = GlassButton("➕ Add Employee", primary=True)
        add_btn.clicked.connect(self.on_add)
        search_layout.addWidget(add_btn)

        main_layout.addLayout(search_layout)

        # Employee table
        self.table = QTableWidget()
        self.setup_table()
        main_layout.addWidget(self.table)

        # Table action buttons
        table_actions = QHBoxLayout()

        edit_btn = GlassButton("✏️ Edit Selected")
        edit_btn.clicked.connect(self.on_edit)
        table_actions.addWidget(edit_btn)

        delete_btn = GlassButton("🗑️ Delete")
        delete_btn.clicked.connect(self.on_delete)
        table_actions.addWidget(delete_btn)

        table_actions.addStretch()

        refresh_btn = GlassButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        table_actions.addWidget(refresh_btn)

        main_layout.addLayout(table_actions)

        main_card.set_content_layout(main_layout)
        layout.addWidget(main_card)

        # Load initial data
        self.refresh_data()

    def setup_table(self):
        headers = ["ID", "Code", "Name", "Designation", "Department", "Gross Pay", "Net Pay", "Status"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        # Table styling
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                gridline-color: #f3f4f6;
                selection-background-color: rgba(59, 130, 246, 0.1);
                alternate-background-color: #f9fafb;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #374151;
                font-weight: 600;
                font-size: 13px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                padding: 12px 8px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f3f4f6;
            }
            QTableWidget::item:selected {
                background-color: rgba(59, 130, 246, 0.1);
                color: #1e293b;
            }
        """)

        # Table behavior
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        # **Make table read-only**
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Resize columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Code
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Designation
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Department
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Gross
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Net
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Status

    def get_all_employees(self):
        return get_all_employees(self.db_path)

    def refresh_data(self):
        employees = self.get_all_employees()
        self.update_stats(employees)
        self.update_table(employees)
        self.update_department_filter(employees)

    def update_stats(self, employees):
        # Total count (all employees in current filter)
        total_count = len(employees)

        # Total payroll (sum of net pay for active employees in current filter)
        active_employees = [emp for emp in employees if emp.get("status", "").lower() == "active"]
        total_payroll = sum(compute_financials(emp)["net"] for emp in active_employees)

        # Unique departments in current filter
        departments = set(emp.get('department', '') for emp in employees if emp.get('department'))

        # Update cards
        self.total_employees_card.update_value(str(total_count))
        self.total_salary_card.update_value(f"₹{total_payroll:,.2f}")
        self.departments_card.update_value(str(len(departments)))

        # Update card titles to reflect current filter
        dept_filter = self.dept_filter.currentText()
        if dept_filter != "All Departments":
            # Update the title labels to show filtered context
            if hasattr(self.total_employees_card, 'title_label'):
                self.total_employees_card.title_label.setText(f"Employees in {dept_filter}")
            if hasattr(self.total_salary_card, 'title_label'):
                self.total_salary_card.title_label.setText(f"Payroll - {dept_filter}")
        else:
            # Reset to original titles when showing all departments
            if hasattr(self.total_employees_card, 'title_label'):
                self.total_employees_card.title_label.setText("Total Employees")
            if hasattr(self.total_salary_card, 'title_label'):
                self.total_salary_card.title_label.setText("Total Payroll")

    def update_department_filter(self, employees):
        current_selection = self.dept_filter.currentText()
        self.dept_filter.clear()
        self.dept_filter.addItem("All Departments")

        departments = set(emp.get('department', '') for emp in employees if emp.get('department'))
        for dept in sorted(departments):
            self.dept_filter.addItem(dept)

        # Restore selection if possible
        index = self.dept_filter.findText(current_selection)
        if index >= 0:
            self.dept_filter.setCurrentIndex(index)

    def update_table(self, employees):
        """
        Populate the QTableWidget using compute_financials(emp) so Gross/Net are correct.
        """
        self.table.setRowCount(len(employees))

        for i, emp in enumerate(employees):
            # Ensure we use compute_financials to get gross/net
            financials = compute_financials(emp)
            gross_pay = financials.get("gross", 0.0)
            net_pay = financials.get("net", 0.0)

            # --- ID ---
            id_item = QTableWidgetItem(str(emp.get("id", "")))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, id_item)

            # --- Code ---
            code_item = QTableWidgetItem(emp.get("emp_code", ""))
            code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, code_item)

            # --- Name ---
            name_item = QTableWidgetItem(emp.get("name", ""))
            name_item.setFont(QFont("", 0, QFont.Weight.DemiBold))
            # keep default alignment (left) for name for better readability
            self.table.setItem(i, 2, name_item)

            # --- Designation ---
            des_item = QTableWidgetItem(emp.get("designation", ""))
            des_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 3, des_item)

            # --- Department ---
            dept_item = QTableWidgetItem(emp.get("department", ""))
            dept_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 4, dept_item)

            # --- Gross Pay (formatted display, numeric value for sorting) ---
            gross_text = f"₹{gross_pay:,.2f}"
            gross_item = QTableWidgetItem(gross_text)
            gross_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            gross_item.setForeground(QColor("#059669"))
            # set numeric value so sorting treats it as number
            gross_item.setData(Qt.ItemDataRole.UserRole, float(gross_pay))
            self.table.setItem(i, 5, gross_item)

            # --- Net Pay (formatted display, numeric value for sorting) ---
            net_text = f"₹{net_pay:,.2f}"
            net_item = QTableWidgetItem(net_text)
            net_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            net_item.setForeground(QColor("#3b82f6"))
            net_item.setFont(QFont("", 0, QFont.Weight.Bold))
            net_item.setData(Qt.ItemDataRole.UserRole, float(net_pay))
            self.table.setItem(i, 6, net_item)

            # --- Status ---
            status = emp.get("status", "Active")
            status_text = "🟢 Active" if str(status).lower() == "active" else "🔴 Inactive"
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 7, status_item)

        # If you want sorting by the numeric value to actually work, map the sort role:
        # set a proxy so Qt will consider UserRole when sorting. QTableWidget doesn't expose
        # a direct API for changing the sort role, so we use a small trick: reimplement
        # lessThan in a QSortFilterProxyModel if you migrate to QTableView + model.
        # For now, this keeps numeric values attached to items (useful later).



    def filter_employees(self):
        search_text = self.search_input.text().lower()
        dept_filter = self.dept_filter.currentText()

        employees = self.get_all_employees()

        # Apply filters
        filtered_employees = []
        for emp in employees:
            # Search filter
            if search_text:
                searchable = f"{emp.get('name', '')} {emp.get('emp_code', '')} {emp.get('designation', '')}".lower()
                if search_text not in searchable:
                    continue

            # Department filter
            if dept_filter != "All Departments":
                if emp.get('department', '') != dept_filter:
                    continue

            filtered_employees.append(emp)

        # Update table with filtered data
        self.update_table(filtered_employees)

        # Update stats cards with filtered data
        self.update_stats(filtered_employees)

    def selected_employee_id(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        id_item = self.table.item(row, 0)
        return int(id_item.text()) if id_item else None

    def on_add(self):
        dialog = ModernEmployeeFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            emp = dialog.get_employee()
            insert_employee(self.db_path, emp.to_dict())
            self.refresh_data()

    def on_edit(self):
        emp_id = self.selected_employee_id()
        if not emp_id:
            QMessageBox.warning(self, "No Selection", "Please select an employee to edit.")
            return

        # Find employee data
        employees = self.get_all_employees()
        emp_dict = next((e for e in employees if e["id"] == emp_id), None)
        if not emp_dict:
            QMessageBox.warning(self, "Not Found", "Selected employee not found.")
            return

        dialog = ModernEmployeeFormDialog(self, Employee.from_dict(emp_dict))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            emp = dialog.get_employee()
            update_employee(self.db_path, emp_id, emp.to_dict())
            self.refresh_data()

    def on_delete(self):
        emp_id = self.selected_employee_id()
        if not emp_id:
            QMessageBox.warning(self, "No Selection", "Please select an employee to delete.")
            return

        # Get employee name for confirmation
        employees = self.get_all_employees()
        emp_dict = next((e for e in employees if e["id"] == emp_id), None)
        emp_name = emp_dict.get("name", "Unknown") if emp_dict else "Unknown"

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete employee:\n\n{emp_name}\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            delete_employee(self.db_path, emp_id)
            self.refresh_data()
            QMessageBox.information(self, "Deleted", f"Employee '{emp_name}' has been deleted.")


