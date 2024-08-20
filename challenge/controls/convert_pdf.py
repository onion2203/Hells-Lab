from io import BytesIO
from flask import render_template
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet

def text_to_pdf(text_file_path):
    """Convert text file to PDF"""
    try:
        stream_file = BytesIO()
        styles = getSampleStyleSheet()
        content = []
        with open(text_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                content.append(Paragraph(line, styles['Normal']))
        SimpleDocTemplate(stream_file).build(content)
        stream_file.seek(0)
        return stream_file
    except Exception as e:
        return render_template("error.html", title="Error", error="Are you Hacking me?", redirect_url="/convert"), 400

def image_to_pdf(image_file_path):
    """Convert image file to PDF"""
    try:
        stream_file = BytesIO()
        doc = SimpleDocTemplate(stream_file)
        content = []
        img = Image(image_file_path)
        img.drawHeight = 500
        img.drawWidth = 500
        content.append(img)
        doc.build(content)
        return stream_file
    except Exception as e:
        return render_template("error.html", title="Error", error="Are you Hacking me?", redirect_url="/convert"), 400

def html_to_pdf(html_file):
    """Convert HTML file to PDF""" 
    try:
        stream_file = BytesIO()
        html_content = open(html_file).read()
        data = []
        data.append(Paragraph(html_content, getSampleStyleSheet()["BodyText"]))
        SimpleDocTemplate(stream_file).build(data)
        stream_file.seek(0)
        return stream_file
    except Exception as e:
        return render_template("error.html", title="Error", error="Are you Hacking me?", redirect_url="/convert"), 400