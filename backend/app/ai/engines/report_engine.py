import os
from pathlib import Path
from typing import Dict, Any, List
import xml.sax.saxutils as saxutils

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from app.core.logger import logger

def safe_escape(text: Any) -> str:
    """Escapes string inputs for XML paragraph rendering inside ReportLab."""
    if text is None:
        return "N/A"
    return saxutils.escape(str(text))

def generate_pdf_report(
    output_path: Path,
    candidate_name: str,
    ats_score: int,
    breakdown: Dict[str, int],
    health: Dict[str, str],
    summary: str,
    matched_skills: List[str],
    missing_skills: List[Dict[str, Any]],
    suggestions: List[str],
    roadmap: List[Dict[str, Any]]
) -> Path:
    """
    Builds a multi-page, formatted PDF report using ReportLab.
    Saves the PDF to output_path.
    """
    logger.info(f"Generating PDF ReportLab document at: {output_path}")
    
    # Setup document template
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles definitions
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SubSectionHeader',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2563EB'),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'ReportBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=5
    )
    
    score_banner_style = ParagraphStyle(
        'ScoreBanner',
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=36,
        alignment=1, # Center
        textColor=colors.HexColor('#2563EB')
    )
    
    story = []
    
    # --- PAGE 1: HEADER & CORE RESULTS ---
    # Header Banner
    story.append(Paragraph(f"AI RESUME ANALYTICS REPORT", title_style))
    story.append(Paragraph(f"<b>Candidate Profile:</b> {safe_escape(candidate_name)}", body_style))
    story.append(Spacer(1, 15))
    
    # ATS Score callout table
    score_html = f"ATS SCORE: {ats_score}/100"
    score_p = Paragraph(score_html, score_banner_style)
    
    score_table_data = [[score_p]]
    score_table = Table(score_table_data, colWidths=[doc.width])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 20),
        ('BOTTOMPADDING', (0,0), (-1,-1), 20),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 20))
    
    # 1. Executive Summary
    story.append(Paragraph("Executive Profile Summary", h1_style))
    story.append(Paragraph(safe_escape(summary), body_style))
    story.append(Spacer(1, 15))
    
    # 2. Section Health Analysis
    story.append(Paragraph("Resume Section Health Evaluation", h1_style))
    health_data = [["Section Category", "Status Status"]]
    for sec, stat in health.items():
        health_data.append([sec.replace("_", " ").title(), stat])
        
    health_table = Table(health_data, colWidths=[200, 200])
    health_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,1), (-1,-1), 5),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
    ]))
    story.append(health_table)
    story.append(PageBreak()) # Clean separation
    
    # --- PAGE 2: SKILL GAP & ROADMAP ---
    story.append(Paragraph("Skill Gap & Alignment Matrix", h1_style))
    
    # Matched Skills
    story.append(Paragraph("Successfully Matched Skills", h2_style))
    matched_p = ", ".join(matched_skills) if matched_skills else "No matching keywords detected against job requirements."
    story.append(Paragraph(safe_escape(matched_p), body_style))
    story.append(Spacer(1, 10))
    
    # Missing Skills Table
    story.append(Paragraph("Crucial Missing Skills & Priority", h2_style))
    if missing_skills:
        missing_data = [["Missing Skill", "Priority Rating"]]
        for item in missing_skills[:10]: # Cap at 10 items for print layout
            stars = "★" * item["priority"]
            missing_data.append([item["skill"].title(), f"{stars} (Level {item['priority']})"])
            
        missing_table = Table(missing_data, colWidths=[200, 200])
        missing_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0,1), (-1,-1), 4),
            ('BOTTOMPADDING', (0,1), (-1,-1), 4),
        ]))
        story.append(missing_table)
    else:
        story.append(Paragraph("Perfect skill alignment! No gaps detected.", body_style))
    story.append(Spacer(1, 15))
    
    # Roadmap Section
    story.append(Paragraph("Skill Acceleration & Learning Roadmap", h1_style))
    if roadmap:
        for idx, step in enumerate(roadmap[:4]): # Max 4 roadmap items in print report
            story.append(Paragraph(f"<b>Step {idx+1}: Learn {safe_escape(step.get('skill', ''))}</b>", h2_style))
            story.append(Paragraph(f"• <b>Recommended Course/Resource:</b> {safe_escape(step.get('resource', ''))}", bullet_style))
            story.append(Paragraph(f"• <b>Estimated Duration:</b> {safe_escape(step.get('time', ''))}", bullet_style))
            story.append(Paragraph(f"• <b>Hands-on Project Idea:</b> {safe_escape(step.get('project', ''))}", bullet_style))
            if step.get('certification'):
                story.append(Paragraph(f"• <b>Target Certification:</b> {safe_escape(step.get('certification'))}", bullet_style))
            story.append(Spacer(1, 5))
    else:
        story.append(Paragraph("No roadmap suggestions required.", body_style))
        
    story.append(PageBreak())
    
    # --- PAGE 3: RECOMMENDATIONS & AUDITING ---
    story.append(Paragraph("AI Recommendations & Rewrite Auditing", h1_style))
    
    story.append(Paragraph("Optimization Bullet Points", h2_style))
    if suggestions:
        for sug in suggestions[:8]: # Max 8 suggestions
            story.append(Paragraph(f"• {safe_escape(sug)}", bullet_style))
    else:
        story.append(Paragraph("Formatting structure is fully optimized.", body_style))
    story.append(Spacer(1, 15))
    
    # Footer notice
    story.append(Spacer(1, 40))
    notice_text = (
        "<i>Disclaimer: This report was dynamically generated by the AI Resume Analyzer using a "
        "hybrid deterministic NLP parser and generative scoring templates. Utilize these insights to optimize "
        "your profile layouts and target recruitment parameters.</i>"
    )
    story.append(Paragraph(notice_text, body_style))
    
    # Build document
    try:
        doc.build(story)
        logger.info(f"PDF successfully compiled and written to: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to compile PDF document layout: {e}")
        raise e
