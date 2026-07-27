from flask import Blueprint, send_file
from services.certificate_service import CertificateService

cert_bp = Blueprint('certificate', __name__)

@cert_bp.route('/certificates/download/<int:course_id>')
def download_certificate(course_id):
    # Mock data for demonstration
    student_name = "Alex Johnson"
    course_title = "Flask & Python Backend Mastery"

    pdf_buffer = CertificateService.generate_pdf(
        student_name=student_name,
        course_title=course_title
    )

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"SkillPro_Certificate_{course_id}.pdf",
        mimetype='application/pdf'
    )