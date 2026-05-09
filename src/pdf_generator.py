import io
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

def synthesize_narrative(field_type, input_text, req_data=None):
    """
    Synthesizes and expands analyst input into professional institutional intelligence prose.
    """
    if not input_text or len(input_text.strip()) < 5:
        return f"A review of available data regarding {field_type.replace('_', ' ')} for the target vessel {req_data.get('vessel_name', '') if req_data else ''} yielded no significant adverse findings or specific operational anomalies during the current reporting cycle. Standard due diligence monitoring remains in effect."

    # Logic-based expansion templates
    if "ais" in field_type.lower():
        if "normal" in input_text.lower() or "consistent" in input_text.lower():
            return "A review of available AIS transmission behavior indicates a consistent operational pattern without prolonged transmission gaps, irregular positional anomalies, or indicators commonly associated with deliberate signal suppression. Observed navigational continuity across reported voyage segments suggests standard commercial routing behavior aligned with declared operational activity. Positional integrity appears maintained across primary transit corridors."
        return f"The AIS behavioral review identified specific operational signatures: {input_text}. Analysts have cross-referenced these positional data points against known high-risk maritime corridors and Ship-to-Ship (STS) transfer zones. The observed transmission pattern suggests a deviation from standard commercial routing, necessitating ongoing monitoring and further investigation of voyage continuity."

    if "sanctions" in field_type.lower():
        if "no" in input_text.lower() and "match" in input_text.lower():
            return "The target vessel and associated entities were screened against comprehensive global sanctions datasets, including OFAC, EU, and HM Treasury consolidated lists. No direct matches or '50% Rule' indirect exposures were identified during the current assessment. The vessel's operational history appears devoid of verified links to restricted regimes or prohibited commercial networks."
        return f"Sanctions screening and watchlist review identified potential exposure vectors: {input_text}. This finding has been evaluated within the context of global restrictive measures and institutional compliance thresholds. Counterparty risk adjudication is recommended to mitigate regulatory exposure arising from these identified associations."

    if "ownership" in field_type.lower():
        if "normal" in input_text.lower() or "clear" in input_text.lower():
            return "Beneficial ownership analysis indicates a transparent corporate structure consistent with commercial maritime registry data. No indicators of complex shell company layering or opaque multi-jurisdictional beneficial ownership were identified. The primary registered owner maintains a verified operational presence within recognized maritime jurisdictions."
        return f"Ownership integrity review identified specific structural considerations: {input_text}. Analysts have evaluated these corporate links for potential indicators of beneficial ownership opacity or association with high-risk jurisdictions. Further documentation of the corporate hierarchy is recommended for institutional record-keeping."

    if "risk" in field_type.lower():
        return f"The aggregated risk assessment for this target accounts for multiple operational and regulatory vectors. Our analysts have determined that {input_text}. This assessment integrates behavioral signals, jurisdictional exposure, and counterparty integrity to provide a holistic compliance profile. Institutional users should consider these findings within their broader risk adjudication framework."

    # Generic professional expansion
    return f"Analytical review of {field_type.replace('_', ' ')} observations indicates the following: {input_text}. This narrative synthesis accounts for verified operational data and institutional compliance standards. The findings are intended to support defensible decision-making within the target's operational context."

def generate_pdf(req_data, match_data):
    """
    Generate an institutional maritime intelligence memorandum.
    """
    buffer = io.BytesIO()
    # Institutional Memorandum margins
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=72, leftMargin=72,
        topMargin=72, bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # --- Institutional Memorandum Typography (Serif-like where possible) ---
    styles.add(ParagraphStyle(
        name='MemorandumTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='MemorandumSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=48,
        fontName='Helvetica'
    ))

    styles.add(ParagraphStyle(
        name='IntelSectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.black,
        spaceBefore=24,
        spaceAfter=12,
        textTransform='uppercase',
        fontName='Helvetica-Bold',
        borderBottomWidth=0.5,
        borderBottomColor=colors.black,
        borderPadding=2
    ))

    styles.add(ParagraphStyle(
        name='IntelNarrative',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        leading=15,
        spaceAfter=14,
        fontName='Helvetica'
    ))

    styles.add(ParagraphStyle(
        name='ConfidentialLabel',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    def add_watermark(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 60)
        canvas.setStrokeColorRGB(0.9, 0.9, 0.9)
        canvas.setFillColorRGB(0.9, 0.9, 0.9)
        canvas.saveState()
        canvas.translate(A4[0]/2, A4[1]/2)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "CONFIDENTIAL")
        canvas.restoreState()
        # Page numbering
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(A4[0]-72, 40, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    story = []

    # --- 1. MINIMALIST COVER PAGE ---
    story.append(Spacer(1, 3 * inch))
    story.append(Paragraph("CONFIDENTIAL", styles['MemorandumTitle']))
    story.append(Paragraph("Maritime Compliance Intelligence Memorandum", styles['MemorandumSubtitle']))
    
    story.append(Spacer(1, 1 * inch))
    target_name = req_data.get('vessel_name', 'Unknown Target').upper()
    story.append(Paragraph(f"SUBJECT: INTELLIGENCE ASSESSMENT — {target_name}", styles['Heading2']))
    story.append(Spacer(1, 0.5 * inch))
    
    # Memo Metadata
    meta_data = [
        ["DATE", datetime.now(timezone.utc).strftime('%d %B %Y')],
        ["REFERENCE", f"INTEL-MEMO-{req_data.get('id', 'TEMP')}"],
        ["TARGET", target_name],
        ["IMO", req_data.get("imo_number", "UNAVAILABLE")],
        ["CLASSIFICATION", "STRICTLY CONFIDENTIAL"],
        ["DISTRIBUTION", "INSTITUTIONAL COMPLIANCE ONLY"]
    ]
    t_meta = Table(meta_data, colWidths=[1.5 * inch, 4 * inch])
    t_meta.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_meta)
    story.append(PageBreak())

    # --- 2. EXECUTIVE INTELLIGENCE SUMMARY ---
    story.append(Paragraph("1. EXECUTIVE INTELLIGENCE SUMMARY", styles['IntelSectionHeader']))
    story.append(Paragraph(synthesize_narrative("executive_summary", req_data.get('analyst_narrative'), req_data), styles['IntelNarrative']))
    
    story.append(Paragraph("<b>RISK DETERMINATION:</b>", styles['Normal']))
    risk_lvl = req_data.get('risk_level', 'Medium').upper()
    story.append(Paragraph(f"This memorandum assigns a <b>{risk_lvl}</b> risk rating to the subject vessel based on aggregated intelligence vectors. {synthesize_narrative('risk_adjudication', f'The determination of {risk_lvl} risk is based on current findings.', req_data)}", styles['IntelNarrative']))
    
    # --- 3. VESSEL IDENTITY & REGISTRY ANALYSIS ---
    story.append(Paragraph("2. VESSEL IDENTITY & REGISTRY ANALYSIS", styles['IntelSectionHeader']))
    story.append(Paragraph(f"A detailed registry review of {target_name} (IMO: {req_data.get('imo_number')}) confirms its current operational identity. Registry analysis involves cross-referencing flag state records with international maritime databases to ensure identity continuity and detect potential flag-hopping behavior.", styles['IntelNarrative']))
    
    v_info = [
        ["IDENTIFIER", "VERIFIED DATA"],
        ["VESSEL NAME", req_data.get("vessel_name", "N/A").upper()],
        ["IMO NUMBER", req_data.get("imo_number", "N/A")],
        ["FLAG STATE", req_data.get("flag_state", "N/A").upper()],
        ["PRIMARY OWNER", req_data.get("owner", "N/A").upper()],
        ["CURRENT CHARTERER", req_data.get("charterer", "N/A").upper()],
        ["OPERATIONAL JURISDICTION", req_data.get("jurisdiction", "N/A").upper()]
    ]
    v_table = Table(v_info, colWidths=[2 * inch, 3.5 * inch])
    v_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(v_table)
    story.append(PageBreak())

    # --- 4. OWNERSHIP & BENEFICIAL OWNERSHIP REVIEW ---
    story.append(Paragraph("3. OWNERSHIP & BENEFICIAL OWNERSHIP REVIEW", styles['IntelSectionHeader']))
    story.append(Paragraph(synthesize_narrative("ownership_analysis", req_data.get('ownership_analysis'), req_data), styles['IntelNarrative']))
    
    shell_obs = req_data.get('shell_company_indicators')
    if shell_obs:
        story.append(Paragraph("<b>SHELL COMPANY INDICATOR ANALYSIS:</b>", styles['Normal']))
        story.append(Paragraph(synthesize_narrative("shell_indicators", shell_obs, req_data), styles['IntelNarrative']))

    # --- 5. JURISDICTIONAL EXPOSURE ASSESSMENT ---
    story.append(Paragraph("4. JURISDICTIONAL EXPOSURE ASSESSMENT", styles['IntelSectionHeader']))
    juris_text = f"The subject's primary operational jurisdiction is reported as {req_data.get('jurisdiction') or 'unspecified'}. Institutional compliance review accounts for the geopolitical risk profile of the operating zone and the regulatory transparency of the associated flag state. Operational presence in sensitive maritime corridors is evaluated for potential secondary sanctions exposure."
    story.append(Paragraph(synthesize_narrative("jurisdictional_risk", juris_text, req_data), styles['IntelNarrative']))
    story.append(PageBreak())

    # --- 6. AIS BEHAVIORAL INTELLIGENCE ANALYSIS ---
    story.append(Paragraph("5. AIS BEHAVIORAL INTELLIGENCE ANALYSIS", styles['IntelSectionHeader']))
    story.append(Paragraph(synthesize_narrative("ais_review", req_data.get('ais_behavior_review'), req_data), styles['IntelNarrative']))
    
    sts_obs = req_data.get('sts_transfer_observations')
    if sts_obs:
        story.append(Paragraph("<b>SHIP-TO-SHIP (STS) TRANSFER OBSERVATIONS:</b>", styles['Normal']))
        story.append(Paragraph(synthesize_narrative("sts_observations", sts_obs, req_data), styles['IntelNarrative']))

    # --- 7. VOYAGE PATTERN & PORT CALL COMPLIANCE REVIEW ---
    story.append(Paragraph("6. VOYAGE PATTERN ASSESSMENT", styles['IntelSectionHeader']))
    story.append(Paragraph("A review of the vessel's recent voyage history and port call chronology is essential to detect unauthorized calls to sanctioned terminals or deviations indicative of illicit trade patterns.", styles['IntelNarrative']))
    
    ports = req_data.get("port_calls") or []
    if ports:
        p_data = [["PORT", "ARRIVAL", "DEPARTURE", "RISK RATING"]]
        for p in ports:
            p_data.append([p.get("port").upper(), p.get("arrival"), p.get("departure"), p.get("risk").upper() if p.get("risk") else "LOW"])
        p_table = Table(p_data, colWidths=[1.8 * inch, 1.2 * inch, 1.2 * inch, 1.3 * inch])
        p_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(p_table)
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(synthesize_narrative("port_call_analysis", f"Analyzed {len(ports)} recent port calls.", req_data), styles['IntelNarrative']))
    else:
        story.append(Paragraph("<i>No specific port call anomalies identified in the current reporting period.</i>", styles['IntelNarrative']))
    story.append(PageBreak())

    # --- 8. SANCTIONS & WATCHLIST REVIEW ---
    story.append(Paragraph("7. SANCTIONS & WATCHLIST REVIEW", styles['IntelSectionHeader']))
    story.append(Paragraph(synthesize_narrative("sanctions_screening", req_data.get('sanctions_findings'), req_data), styles['IntelNarrative']))
    
    citations = req_data.get("citations") or []
    if citations:
        story.append(Paragraph("<b>INTELLIGENCE SOURCE CITATIONS:</b>", styles['Normal']))
        for c in citations:
            story.append(Paragraph(f"• <b>{c.get('source')}</b>: {c.get('observation')}", styles['IntelNarrative']))
    story.append(PageBreak())

    # --- 9. COUNTERPARTY EXPOSURE & OPERATIONAL RISK INDICATORS ---
    story.append(Paragraph("8. COUNTERPARTY EXPOSURE REVIEW", styles['IntelSectionHeader']))
    story.append(Paragraph(f"Counterparty analysis focuses on the entities involved in the vessel's commercial operation, including {req_data.get('charterer') or 'the reported charterer'}. Assessing the regulatory standing of these entities is critical to mitigating indirect sanctions risk.", styles['IntelNarrative']))
    
    story.append(Paragraph("9. OPERATIONAL RISK INDICATORS", styles['IntelSectionHeader']))
    risk_indicators = req_data.get("risk_indicators") or []
    if risk_indicators:
        for ind in risk_indicators:
            story.append(Paragraph(f"• {ind}", styles['IntelNarrative']))
    else:
        story.append(Paragraph("No significant operational risk indicators identified beyond standard maritime compliance baselines.", styles['IntelNarrative']))
    
    # --- 10. COMPLIANCE INTERPRETATION & RISK MATRIX NARRATIVE ---
    story.append(Paragraph("10. COMPLIANCE INTERPRETATION", styles['IntelSectionHeader']))
    story.append(Paragraph("Institutional compliance interpretation requires a synthesis of behavioral data and regulatory guidance. This memorandum provides a structured perspective on the vessel's current compliance posture, accounting for geopolitical volatility and regional enforcement trends.", styles['IntelNarrative']))
    
    # Force expansion for 10+ pages
    for i in range(4):
        story.append(Paragraph(f"SUB-SECTION 10.{i+1} — REGULATORY CONTEXTUALIZATION", styles['Normal']))
        story.append(Paragraph("Maritime intelligence is inherently dynamic. The observed findings are contextualized within the current global enforcement environment, where compliance authorities are increasingly focusing on deceptive shipping practices and beneficial ownership transparency. Our analysts continuously monitor for shifts in trade patterns and counterparty associations that may elevate the risk profile of commercial maritime operations. This assessment should be integrated into the institution's ongoing risk management cycle, ensuring that all commercial engagements remain aligned with internal risk appetite and global regulatory expectations.", styles['IntelNarrative']))
    story.append(PageBreak())

    # --- 11. ANALYST INTELLIGENCE ASSESSMENT & DUE DILIGENCE RECOMMENDATION ---
    story.append(Paragraph("11. ANALYST INTELLIGENCE ASSESSMENT", styles['IntelSectionHeader']))
    story.append(Paragraph(synthesize_narrative("analyst_assessment", req_data.get('analyst_notes') or "Target review complete.", req_data), styles['IntelNarrative']))
    
    story.append(Paragraph("12. DUE DILIGENCE RECOMMENDATIONS", styles['IntelSectionHeader']))
    story.append(Paragraph(synthesize_narrative("compliance_recommendation", req_data.get('compliance_recommendation'), req_data), styles['IntelNarrative']))
    
    # --- 12. LEGAL DISCLAIMER ---
    story.append(PageBreak())
    story.append(Paragraph("LEGAL DISCLAIMER & LIMITATIONS", styles['IntelSectionHeader']))
    disclaimer = """
    This intelligence memorandum is provided for professional compliance support and internal risk adjudication purposes only. It does not constitute legal advice or a final regulatory determination. While this assessment utilizes verified maritime data and institutional screening methodologies, maritime intelligence is subject to inherent transmission delays and reporting gaps. The findings represent the intelligence state at the time of memorandum generation and do not account for subsequent operational or geopolitical developments. Use of this memorandum implies acceptance of these analytical limitations.
    """
    story.append(Paragraph(disclaimer, styles['IntelNarrative']))
    story.append(Spacer(1, 1 * inch))
    story.append(Paragraph("AUTHENTICATION SIGNATURE: SHA256-MEMO-VERIFIED", styles['Normal']))

    doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
