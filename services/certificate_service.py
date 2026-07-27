import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class CertificateService:
    @staticmethod
    def generate_pdf(student_name: str, course_title: str) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=60
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CertTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=32,
            textColor=colors.HexColor('#4F46E5'),
            alignment=1,
            spaceAfter=20
        )
        sub_style = ParagraphStyle(
            'CertSub',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=16,
            textColor=colors.HexColor('#334155'),
            alignment=1,
            spaceAfter=15
        )
        name_style = ParagraphStyle(
            'CertName',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=26,
            textColor=colors.HexColor('#0F172A'),
            alignment=1,
            spaceAfter=20
        )

        elements = [
            Paragraph("CERTIFICATE OF COMPLETION", title_style),
            Spacer(1, 20),
            Paragraph("This is proudly awarded to", sub_style),
            Paragraph(student_name, name_style),
            Paragraph(f"for successfully completing the course <b>{course_title}</b> on SkillPro.", sub_style)
        ]

        doc.build(elements)
        buffer.seek(0)
        return buffer