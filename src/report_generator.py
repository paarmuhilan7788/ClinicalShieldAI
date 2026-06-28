from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import json

def generate_pdf_report(records, output_path="outputs/clinicalshield_report.pdf"):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle("title", parent=styles["Title"],
                                  fontSize=24, textColor=colors.HexColor("#ff4b4b"),
                                  alignment=TA_CENTER)
    story.append(Paragraph("ClinicalShield AI", title_style))
    story.append(Paragraph("FHIR Threat Detection Report", title_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                            ParagraphStyle("sub", parent=styles["Normal"], alignment=TA_CENTER, textColor=colors.grey)))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#ff4b4b")))
    story.append(Spacer(1, 0.3 * inch))

    # Summary metrics
    total = len(records)
    attacks = [r for r in records if r.get("prediction", {}).get("is_attack", False)]
    critical = [r for r in attacks if r.get("prediction", {}).get("severity") == "critical"]
    detection_rate = round(len(attacks) / total * 100, 1) if total > 0 else 0

    story.append(Paragraph("Executive Summary", styles["Heading1"]))
    summary_data = [
        ["Metric", "Value"],
        ["Total Records Analysed", str(total)],
        ["Attacks Detected", str(len(attacks))],
        ["Detection Rate", f"{detection_rate}%"],
        ["Critical Severity", str(len(critical))],
    ]
    summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ff4b4b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#1e2130"), colors.HexColor("#0e1117")]),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.white),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3 * inch))

    # Top attack vectors
    story.append(Paragraph("Top Attack Vectors", styles["Heading1"]))
    vector_counts = {}
    for r in attacks:
        v = r.get("prediction", {}).get("vector_type", "Unknown")
        vector_counts[v] = vector_counts.get(v, 0) + 1
    sorted_vectors = sorted(vector_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    vector_data = [["Attack Vector", "Count"]] + [[v, str(c)] for v, c in sorted_vectors]
    vector_table = Table(vector_data, colWidths=[4 * inch, 1.5 * inch])
    vector_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ff4b4b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#1e2130"), colors.HexColor("#0e1117")]),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.white),
    ]))
    story.append(vector_table)
    story.append(Spacer(1, 0.3 * inch))

    # MITRE TTPs
    story.append(Paragraph("MITRE ATT&CK Coverage", styles["Heading1"]))
    ttp_counts = {}
    for r in attacks:
        ttp = r.get("prediction", {}).get("mitre_ttp", "Unknown")
        ttp_counts[ttp] = ttp_counts.get(ttp, 0) + 1
    sorted_ttps = sorted(ttp_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    ttp_data = [["TTP ID", "Count"]] + [[t, str(c)] for t, c in sorted_ttps]
    ttp_table = Table(ttp_data, colWidths=[4 * inch, 1.5 * inch])
    ttp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ff4b4b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#1e2130"), colors.HexColor("#0e1117")]),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.white),
    ]))
    story.append(ttp_table)

    doc.build(story)
    print(f"PDF saved → {output_path}")
    return output_path