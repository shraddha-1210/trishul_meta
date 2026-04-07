from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from backend.risk_scorer import RiskScorer
from datetime import datetime

def generate_report(output_path="trishul_report.pdf"):
    scorer = RiskScorer()
    edges = scorer.get_riskiest_edges()
    paths = scorer.get_attack_paths()

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("TRISHUL — Attack Path Intelligence Report", styles['Title']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Top Attack Paths", styles['Heading2']))
    for i, p in enumerate(paths[:5]):
        story.append(Paragraph(
            f"{i+1}. {' → '.join(p.path)} | Risk: {p.total_risk} | "
            f"Reach Probability: {p.reach_probability*100:.0f}% | Target: {p.crown_jewel}",
            styles['Normal']
        ))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Riskiest Trust Edges (CVSS-style Scoring)", styles['Heading2']))
    table_data = [["Source", "Target", "Risk Score", "Blast Radius", "Recommendation"]]
    for e in edges[:8]:
        table_data.append([
            e.src_name, e.dst_name,
            str(e.combined_risk), str(e.blast_radius),
            e.recommendation[:60] + "..." if len(e.recommendation) > 60 else e.recommendation
        ])

    t = Table(table_data, colWidths=[100, 100, 60, 70, 180])
    t.setStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C2C2A')),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTSIZE',   (0,0), (-1,-1), 8),
        ('GRID',       (0,0), (-1,-1), 0.25, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F1EFE8')])
    ])
    story.append(t)

    doc.build(story)
    print(f"✅ Report saved to {output_path}")

if __name__ == "__main__":
    generate_report()