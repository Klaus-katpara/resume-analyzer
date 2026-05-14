import PyPDF2
from django.shortcuts import render
from .models import Resume
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse

SKILLS_DB = [
    "python", "django", "sql", "pandas", "numpy",
    "machine learning", "data analysis", "excel",
    "power bi", "tableau", "html", "css", "javascript"
]

JOB_ROLES = {
    "data analyst": ["python", "sql", "pandas", "excel", "power bi", "tableau"],
    "web developer": ["html", "css", "javascript", "django"],
    "ml engineer": ["python", "machine learning", "numpy", "pandas"]
}

def landing_page(request):
    return render(request, 'landing_page.html')

def upload_resume(request):
    if request.method == 'POST':
        file = request.FILES['file']
        role = request.POST.get('role')

        obj = Resume.objects.create(file=file)

        # 📄 Extract text FIRST
        pdf = PyPDF2.PdfReader(obj.file.path)
        text = ""

        for page in pdf.pages:
            text += page.extract_text()

        # 🔤 Convert AFTER extraction
        text_lower = text.lower()

        # 🔍 Detect all skills
        found_skills = [skill for skill in SKILLS_DB if skill in text_lower]

        # 🎯 General score
        score = int((len(found_skills) / len(SKILLS_DB)) * 100)

        # 🎯 Role-based matching
        required_skills = JOB_ROLES.get(role, [])

        matched = [skill for skill in required_skills if skill in text_lower]
        missing = [skill for skill in required_skills if skill not in text_lower]

        role_score = int((len(matched) / len(required_skills)) * 100) if required_skills else 0

        # 💡 Recommendation
        if role_score > 80:
            message = "Strong match! You're ready to apply."
        elif role_score > 50:
            message = "Good, but you can improve."
        else:
            message = "Needs improvement. Focus on missing skills."

        return render(request, 'resume.html', {
            'text': text,
            'skills': found_skills,
            'score': score,
            'role': role,
            'role_score': role_score,
            'missing': missing,
            'message': message
        })

    return render(request, 'upload.html')

def download_report(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resume_report.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    # Get data from GET request
    role = request.GET.get('role')
    score = request.GET.get('score')
    role_score = request.GET.get('role_score')
    skills = request.GET.get('skills', '')
    missing = request.GET.get('missing', '')

    content = []

    content.append(Paragraph("Resume Analysis Report", styles['Title']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Role: {role}", styles['Normal']))
    content.append(Paragraph(f"Overall Score: {score}%", styles['Normal']))
    content.append(Paragraph(f"Role Match: {role_score}%", styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph("Skills Detected:", styles['Heading2']))
    content.append(Paragraph(skills, styles['Normal']))
    content.append(Spacer(1, 10))

    content.append(Paragraph("Missing Skills:", styles['Heading2']))
    content.append(Paragraph(missing, styles['Normal']))

    doc.build(content)

    return response