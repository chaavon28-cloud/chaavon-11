from fpdf import FPDF
from datetime import datetime

def generate_pdf(vessel_name, match, score, risk):
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "VESSEL SANCTIONS COMPLIANCE REPORT", ln=True, align="C")

    pdf.ln(5)

    # Metadata
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ln=True)
    pdf.cell(0, 6, "Prepared by: Compliance Intelligence System", ln=True)

    pdf.ln(5)

    # Vessel Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "VESSEL DETAILS", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Vessel Name: {vessel_name}", ln=True)

    pdf.ln(5)

    # Screening Result
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "SCREENING RESULT", ln=True)

    pdf.set_font("Arial", "", 10)

    if match:
        pdf.cell(0, 6, f"Sanctions Match: YES", ln=True)
        pdf.cell(0, 6, f"Matched Entity: {match}", ln=True)
        pdf.cell(0, 6, f"Confidence Score: {score}", ln=True)
    else:
        pdf.cell(0, 6, "Sanctions Match: NO", ln=True)

    pdf.ln(5)

    # Risk
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "RISK ASSESSMENT", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Risk Score: {risk}/100", ln=True)

    pdf.ln(5)

    # Disclaimer
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 5,
        "This report is generated based on publicly available sanctions data, including the OFAC SDN list. "
        "It is provided for informational purposes only and does not constitute legal advice. "
        "Users are responsible for independent compliance verification."
    )

    return pdf.output(dest="S").encode("latin-1") 
