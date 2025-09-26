from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, inch
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image, KeepTogether, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import HRFlowable

from num2words import num2words
import os
import sys

# Add the parent directory to Python path to import db module
sys.path.append(str(Path(__file__).parent.parent))
from db import get_employee_by_id, compute_financials

# Try to register fonts that support currency symbols
def register_fonts():
    """Register fonts with currency symbol support"""
    font_registered = False

    # List of common font paths for different systems
    font_paths = [
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        # macOS
        "/System/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        # Linux/Ubuntu
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        # Local fonts (place fonts in assets folder)
        str(Path(__file__).parent.parent / "assets" / "DejaVuSans.ttf"),
        str(Path(__file__).parent.parent / "assets" / "Arial.ttf"),
    ]

    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                font_registered = True
                print(f"Font registered successfully: {font_path}")
                break
        except Exception as e:
            continue

    if not font_registered:
        print("Warning: No custom font found. Using default font. Currency symbols may not render properly.")
        return 'Helvetica'  # Fallback to default

    return 'CustomFont'

class ModernPayslipGenerator:
    """Generate modern, clean payslip PDFs for employees."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.font_name = register_fonts()

        # Modern color palette - define before setup_custom_styles()
        self.colors = {
            'primary': colors.HexColor('#3B82F6'),      # Blue
            'secondary': colors.HexColor('#64748B'),     # Slate
            'success': colors.HexColor('#10B981'),       # Green
            'background': colors.HexColor('#F8FAFC'),    # Light gray
            'card': colors.HexColor('#FFFFFF'),          # White
            'border': colors.HexColor('#E2E8F0'),        # Light border
            'text_primary': colors.HexColor('#1E293B'),  # Dark text
            'text_secondary': colors.HexColor('#64748B'), # Gray text
            'accent': colors.HexColor('#F59E0B'),        # Orange
        }

        self.setup_custom_styles()

    def setup_custom_styles(self):
        # Header styles
        self.company_title_style = ParagraphStyle(
            'CompanyTitle',
            parent=self.styles['Normal'],
            fontSize=24,
            fontName=self.font_name,
            textColor=self.colors['text_primary'],
            alignment=TA_LEFT,
            spaceAfter=2,
            leading=28,
            fontWeight='bold'
        )

        self.company_subtitle_style = ParagraphStyle(
            'CompanySubtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName=self.font_name,
            textColor=self.colors['text_secondary'],
            alignment=TA_LEFT,
            spaceAfter=0,
            leading=14
        )

        self.payslip_period_style = ParagraphStyle(
            'PayslipPeriod',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName=self.font_name,
            textColor=self.colors['text_primary'],
            alignment=TA_RIGHT,
            spaceAfter=0,
            leading=16
        )

        self.section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName=self.font_name,
            textColor=self.colors['text_primary'],
            alignment=TA_LEFT,
            spaceAfter=8,
            spaceBefore=0,
            leading=18,
            fontWeight='bold'
        )

        self.label_style = ParagraphStyle(
            'Label',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName=self.font_name,
            textColor=self.colors['text_secondary'],
            alignment=TA_LEFT,
            leading=12
        )

        self.value_style = ParagraphStyle(
            'Value',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName=self.font_name,
            textColor=self.colors['text_primary'],
            alignment=TA_LEFT,
            leading=14,
            fontWeight='bold'
        )

        self.amount_style = ParagraphStyle(
            'Amount',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName=self.font_name,
            textColor=self.colors['text_primary'],
            alignment=TA_RIGHT,
            leading=14
        )

        self.net_pay_amount_style = ParagraphStyle(
            'NetPayAmount',
            parent=self.styles['Normal'],
            fontSize=28,
            fontName=self.font_name,
            textColor=self.colors['success'],
            alignment=TA_CENTER,
            leading=32,
            fontWeight='bold'
        )

        self.net_pay_label_style = ParagraphStyle(
            'NetPayLabel',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName=self.font_name,
            textColor=self.colors['text_secondary'],
            alignment=TA_CENTER,
            leading=14
        )

        self.earnings_header_style = ParagraphStyle(
            'EarningsHeader',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName=self.font_name,
            textColor=self.colors['text_primary'],
            alignment=TA_LEFT,
            leading=14,
            fontWeight='bold'
        )

    def format_currency(self, amount):
        """Format currency with proper symbol"""
        if self.font_name == 'Helvetica':
            return f"₹{amount:,.2f}"
        else:
            return f"₹{amount:,.2f}"




    def create_header_section(self, pay_period):
        """Create the header section with company logo + name in a single row"""

        # --- LOGO ---
        logo_flowable = ""
    # --- LOGO ---
        if hasattr(sys, "_MEIPASS"):
            logo_path = Path(sys._MEIPASS) / "assets" / "logo.png"
        else:
            logo_path = Path(__file__).parent.parent / "assets" / "logo.png"

        if logo_path.exists():
            try:
                logo = Image(str(logo_path))
                logo.drawHeight = 25 * mm   # smaller logo
                logo.drawWidth = 25 * mm
                logo.hAlign = 'LEFT'
                logo_flowable = logo
            except Exception as e:
                print(f"Warning: Could not load logo: {e}")

        # --- COMPANY INFO ---
        company_info = [
            Paragraph("Mariomed Pharmaceuticals", self.company_title_style),
            Paragraph("S1, Ground Floor, Sonam Annapoorna CHS", self.company_subtitle_style),
Paragraph("New Golden nest, Phase-7,Bhayandar (East)", self.company_subtitle_style),
Paragraph("THANE - 401105", self.company_subtitle_style)
        ]

        # --- MAIN HEADER TABLE ---
        # Put logo and text side-by-side in the same row
        header_table = Table(
            [[logo_flowable, company_info]],
            colWidths=[30 * mm, 170 * mm]
        )

        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        return header_table
    

    def create_employee_summary_card(self, emp, fin , pay_period: str):
        """Create the employee summary card with net pay highlight aligned perfectly"""

        # Total width to match earnings + deductions table
        total_width = 530  # points

        # Split into two columns: left = employee details, right = net pay
        left_width = total_width * 0.55   # ~55% for details
        right_width = total_width - left_width  # remaining for Net Pay

        # Left column - Employee details
        emp_details_data = [
            [Paragraph("<b>EMPLOYEE SUMMARY</b>", self.section_header_style)],
            [Paragraph("Employee Name", self.label_style)],
            [Paragraph(f": {emp.get('name', 'N/A')}", self.value_style)],
            [Paragraph("Employee ID", self.label_style)],
            [Paragraph(f": {emp.get('emp_code', 'N/A')}", self.value_style)],
            [Paragraph("Pay Period", self.label_style)],
            [Paragraph(pay_period, self.value_style)],
            [Paragraph("Designation", self.label_style)],
            [Paragraph(f": {emp.get('designation', 'N/A')}", self.value_style)],
            [Paragraph("PAN No", self.label_style)],
            [Paragraph(f": {emp.get('pan', 'N/A')}", self.value_style)],
        ]

        emp_details_table = Table(emp_details_data, colWidths=[left_width])
        emp_details_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))

        # Right column - Net Pay (large highlight)
        net_pay_data = [
            [Paragraph(self.format_currency(fin['net']), self.net_pay_amount_style)],
            [Paragraph("Employee Net Pay", self.net_pay_label_style)]
        ]

        net_pay_table = Table(net_pay_data, colWidths=[right_width])
        net_pay_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), self.colors['background']),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),  # align to top so top edges match
            ('BOTTOMPADDING', (0,0), (-1,-1), 20),
            ('BOX', (0,0), (-1,-1), 1, self.colors['border']),
        ]))

        # Main container: just two columns
        main_table = Table([[emp_details_table, net_pay_table]],
                        colWidths=[left_width, right_width])
        main_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BACKGROUND', (0,0), (-1,-1), self.colors['card']),
            ('BOX', (0,0), (-1,-1), 1, self.colors['border']),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))

        return main_table

    def create_earnings_deductions_section(self, fin):
        """Create earnings and deductions section"""
        from reportlab.platypus import Paragraph, Table, TableStyle

        # Earnings data
        earnings_data = [
            [Paragraph("EARNINGS", self.earnings_header_style), Paragraph("AMOUNT", self.earnings_header_style)],
            [Paragraph("Basic", self.label_style), Paragraph(self.format_currency(fin["basic"]), self.amount_style)],
            [Paragraph("House Rent Allowance", self.label_style), Paragraph(self.format_currency(fin["hra"]), self.amount_style)],
            [Paragraph("LTA", self.label_style), Paragraph(self.format_currency(fin["LTA"]), self.amount_style)],
            [Paragraph("Special Allowance", self.label_style), Paragraph(self.format_currency(fin["special_allowance"]), self.amount_style)],
            [Paragraph("Gross Earnings", self.earnings_header_style), Paragraph(self.format_currency(fin["gross"]), self.earnings_header_style)],
        ]

        # Deductions data
        deductions_data = [
            [Paragraph("DEDUCTIONS", self.earnings_header_style), Paragraph("AMOUNT", self.earnings_header_style)],
            [Paragraph("Income Tax", self.label_style), Paragraph(self.format_currency(fin["income_tax"]), self.amount_style)],
            [Paragraph("", self.label_style), Paragraph("", self.amount_style)],
            [Paragraph("", self.label_style), Paragraph("", self.amount_style)],
            [Paragraph("", self.label_style), Paragraph("", self.amount_style)],
            [Paragraph("Total Deductions", self.earnings_header_style), Paragraph(self.format_currency(fin["income_tax"]), self.earnings_header_style)],
        ]

        # Ensure both tables have same number of rows
        max_rows = max(len(earnings_data), len(deductions_data))
        while len(earnings_data) < max_rows:
            earnings_data.insert(-1, [Paragraph("", self.label_style), Paragraph("", self.amount_style)])
        while len(deductions_data) < max_rows:
            deductions_data.insert(-1, [Paragraph("", self.label_style), Paragraph("", self.amount_style)])

        # Table style
        table_style = TableStyle([
            ('BACKGROUND', (0,0), (1,0), self.colors['background']),
            ('BACKGROUND', (0,-1), (1,-1), self.colors['background']),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 1, self.colors['border']),
            ('INNERGRID', (0,0), (-1,-1), 0.5, self.colors['border']),
        ])

        # Reduce widths by 20%
        earnings_table_widths = [60*0.85*mm, 50*0.85*mm]
        deductions_table_widths = [60*0.85*mm, 50*0.85*mm]

        # Create individual tables
        earnings_table = Table(earnings_data, colWidths=earnings_table_widths)
        deductions_table = Table(deductions_data, colWidths=deductions_table_widths)
        earnings_table.setStyle(table_style)
        deductions_table.setStyle(table_style)

        # Force both tables to same height dynamically
        total_height = max(earnings_table.wrap(0,0)[1], deductions_table.wrap(0,0)[1])
        row_height = total_height / max_rows
        earnings_table._argH = [row_height] * max_rows
        deductions_table._argH = [row_height] * max_rows

        # Combine tables side by side with no gap
        main_earnings_table = Table([[earnings_table, deductions_table]],
                                    colWidths=[sum(earnings_table_widths), sum(deductions_table_widths)])
        main_earnings_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))

        return main_earnings_table


    def create_total_net_payable_section(self, fin):
        """Create the total net payable section"""
        net_payable_data = [
            [
                Paragraph("TOTAL NET PAYABLE", self.section_header_style),
                Paragraph(self.format_currency(fin['net']), self.net_pay_amount_style)
            ],
            [
                Paragraph("Gross Earnings - Total Deductions", self.label_style),
                ""
            ]
        ]

        net_payable_table = Table(net_payable_data, colWidths=[140*mm, 60*mm])
        net_payable_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), self.colors['success']),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DCFCE7')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 20),
            ('RIGHTPADDING', (0,0), (-1,-1), 20),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
            ('BOX', (0,0), (-1,-1), 1, self.colors['success']),
        ]))

        return net_payable_table

    def create_amount_in_words_section(self, fin):
        """Create amount in words section"""
        try:
            amt_words = num2words(fin['net'], to='currency', lang='en_IN')
            amt_words = amt_words.replace("euro", "Rupees").replace("cents", "Paise")
            amt_words = amt_words.title() + " Only"

            words_data = [
                [Paragraph(f"Amount In Words : {amt_words}", self.label_style)]
            ]

            words_table = Table(words_data, colWidths=[200*mm])
            words_table.setStyle(TableStyle([
                ('LEFTPADDING', (0,0), (-1,-1), 20),
                ('RIGHTPADDING', (0,0), (-1,-1), 20),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ]))

            return words_table
        except Exception as e:
            print(f"Warning: Could not convert amount to words: {e}")
            return None

    def create_footer_section(self):
        """Create footer section"""
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName=self.font_name,
            textColor=self.colors['text_secondary'],
            alignment=TA_CENTER,
            leading=11
        )

        footer_data = [
            [Paragraph("-- This is a system generated payslip, hence the signature is not required --", footer_style)]
        ]

        footer_table = Table(footer_data, colWidths=[200*mm])
        footer_table.setStyle(TableStyle([
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))

        return footer_table

    def generate_pdf(self, db_path: str, employee_id: int, pay_period: str, output_dir: str) -> str:
        """Generate modern PDF for a specific employee and pay period."""
        # Setup output directory
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        # Get employee data
        emp = get_employee_by_id(db_path, employee_id)
        if not emp:
            raise ValueError(f"Employee ID {employee_id} not found")

        fin = compute_financials(emp)

        # Create filename
        safe_emp_code = str(emp.get('emp_code', employee_id)).replace('/', '_')
        safe_period = pay_period.replace(' ', '_').replace('/', '_')
        filename = out_dir / f"Payslip_{safe_emp_code}_{safe_period}.pdf"

        # Create document with tighter margins for better space utilization
        doc = SimpleDocTemplate(
            str(filename),
            pagesize=A4,
            rightMargin=10*mm,
            leftMargin=10*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )

        story = []

        # Build the document sections
        story.append(self.create_header_section(pay_period))
        story.append(Spacer(1, 12))

        story.append(self.create_employee_summary_card(emp, fin ,  pay_period))
        story.append(Spacer(1, 15))

        story.append(self.create_earnings_deductions_section(fin))
        story.append(Spacer(1, 10))

        story.append(self.create_total_net_payable_section(fin))
        story.append(Spacer(1, 8))

        # Amount in words (if conversion works)
        words_section = self.create_amount_in_words_section(fin)
        if words_section:
            story.append(words_section)
            story.append(Spacer(1, 8))

        story.append(self.create_footer_section())

        # Build PDF
        try:
            doc.build(story)
            print(f"Modern payslip generated successfully: {filename}")
            return str(filename)
        except Exception as e:
            raise Exception(f"Failed to generate PDF: {e}")
