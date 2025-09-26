from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class Employee:
    """Employee static info + earnings/deductions."""
    id: Optional[int] = None
    emp_code: str = ""
    name: str = ""
    designation: str = ""
    department: str = ""
    bank_account: str = ""
    ifsc: str = ""
    pan: str = ""
    joining_date: str = ""
    notes: str = ""
    status: str = "Active"  # <-- New field

    # Static earnings & deductions
    basic: float = 0.0
    hra: float = 0.0
    LTA: float = 0.0
    special_allowance: float = 0.0
    income_tax: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Employee":
        return Employee(
            id=d.get("id"),
            emp_code=d.get("emp_code", ""),
            name=d.get("name", ""),
            designation=d.get("designation", ""),
            department=d.get("department", ""),
            bank_account=d.get("bank_account", ""),
            ifsc=d.get("ifsc", ""),
            pan=d.get("pan", ""),
            joining_date=d.get("joining_date", ""),
            notes=d.get("notes", ""),
            status=d.get("status", "Active"),  # <-- handle status
            basic=float(d.get("basic", 0.0) or 0.0),
            hra=float(d.get("hra", 0.0) or 0.0),
            LTA=float(d.get("LTA", 0.0) or 0.0),
            special_allowance=float(d.get("special_allowance", 0.0) or 0.0),
            income_tax=float(d.get("income_tax", 0.0) or 0.0)
        )


@dataclass
class Payslip:
    """Generated payslip for a given pay period."""
    id: Optional[int] = None
    employee_id: Optional[int] = None
    pay_period: str = ""
    notes: str = ""

    # Computed fields (from Employee)
    basic: float = 0.0
    hra: float = 0.0
    LTA: float = 0.0
    special_allowance: float = 0.0
    income_tax: float = 0.0
    gross: float = 0.0
    net: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Payslip":
        basic = float(d.get("basic", 0.0) or 0.0)
        hra = float(d.get("hra", 0.0) or 0.0)
        LTA = float(d.get("LTA", 0.0) or 0.0)
        special = float(d.get("special_allowance", 0.0) or 0.0)
        income_tax = float(d.get("income_tax", 0.0) or 0.0)
        gross = basic + hra + LTA + special
        net = gross - income_tax

        return Payslip(
            id=d.get("id"),
            employee_id=d.get("employee_id"),
            pay_period=d.get("pay_period", ""),
            notes=d.get("notes", ""),
            basic=basic,
            hra=hra,
            LTA=LTA,
            special_allowance=special,
            income_tax=income_tax,
            gross=round(gross, 2),
            net=round(net, 2)
        )
