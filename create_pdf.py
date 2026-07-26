import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('ArialUnicode', './arial.ttf'))

from PIL import Image as PILImage  # Add this import at the top

import matplotlib
matplotlib.use('Agg')  # Non-GUI backend for server/script environments
import matplotlib.pyplot as plt

def clean_body_text(text):
    """
    Cleans non-math paragraph text of characters that default 
    ReportLab fonts (like Helvetica) cannot render.
    """
    if not text:
        return ""
        
    # Replace Unicode En dash (U+2013) with a standard ASCII hyphen
    text = text.replace('\u2013', '-')
    
    # Replace Unicode Non-breaking hyphen (U+2011) with a standard ASCII hyphen
    text = text.replace('\u2011', '-')
    # Optional: Replace EM dash (U+2014) with a double hyphen or safe alternative
    text = text.replace('\u2014', ' -- ')
    text = text.replace('∼', '~')

    return text

def preprocess_latex(formula):
    """
    Translates advanced LaTeX macros (like bra-ket) and normalizes 
    multiplication symbols to formats that Matplotlib's mathtext can parse.
    """
    formula = clean_body_text(formula)

    # 1. Convert \ket{x} -> \left| x \right\rangle
    formula = re.sub(r'\\ket\{([^{}]+)\}', r'\\left| \1 \\right\\rangle', formula)    
    # 2. Convert \bra{x} -> \left\langle x \right|
    formula = re.sub(r'\\bra\{([^{}]+)\}', r'\\left\\langle \1 \\right|', formula)
    
    formula = formula.replace('sqrt2', 'sqrt{2}')

    formula = formula.replace('×', '\\times')

    return formula

def latex_to_png(formula, filename, dpi=300):
    """
    Renders a processed LaTeX string cleanly to an inline-friendly image.
    """
    # Reset and configure Matplotlib's math font set
    plt.rcParams['mathtext.fontset'] = 'cm' # Computer Modern (standard LaTeX styling)
    
    fig = plt.figure(figsize=(0.01, 0.01))
    try:
        clean_formula = preprocess_latex(formula)
        
        # Render
        fig.text(0, 0, f"${clean_formula}$", fontsize=11, usetex=False)
        
        plt.savefig(filename, dpi=dpi, transparent=True, bbox_inches='tight', pad_inches=0.01)
        plt.close(fig)
        return True
    except Exception as e:
        plt.close(fig)
        print(f"Warning: Failed to render standard math formatting for '${formula}$'. Exception: {e}")
        return False


def process_inline_math(text, temp_dir="math_images", target_height = 11.5):
    """
    Parses arbitrary body text, identifies math blocks delimited by single $, 
    processes them, and returns ReportLab-friendly HTML paragraphs.
    """
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    text = clean_body_text(text)  # Clean the text of unsupported characters 
    # Identifies anything sandwiched by '$'
    pattern = r'\$([^$]+?)\$'
    matches = re.findall(pattern, text)
    
    processed_text = text
    for match in matches:
        # Exclusion filter: bypass direct monetary values like $200 or $99.90
        # if re.match(r'^\d+(\.\d+)?$', match):
        #     continue
            
        img_filename = os.path.join(temp_dir, f"math_{hash(match)}.png")
        
        success = True
        if not os.path.exists(img_filename):
            success = latex_to_png(match, img_filename)
            
        if success and os.path.exists(img_filename):
            try:
                with PILImage.open(img_filename) as img:
                    orig_width, orig_height = img.size
                
                # Math rendering layout scaling
                aspect_ratio = orig_width / orig_height
                target_width = round(target_height * aspect_ratio, 2)
                
                img_tag = f'<img src="{img_filename}" width="{target_width}" height="{target_height}" valign="middle"/>'
                processed_text = processed_text.replace(f"${match}$", img_tag, 1)
            except Exception as e:
                print(f"Error drawing image tag for ${match}$: {e}")
                continue
                
    return processed_text


def draw_page_format(canvas, doc):
    """Defines the structural format applied to every single page."""
    canvas.saveState()
    
    # Header Format
    canvas.setFont('Helvetica-Bold', 12)
    canvas.setFillColor(colors.HexColor("#1A365D")) # Dark Blue
    canvas.drawString(54, 750, "Conference 2026")
    
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.gray)
    canvas.drawRightString(letter[0] - 54, 750, "Poster Abstract")
    
    # Header Line
    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.setLineWidth(1)
    canvas.line(54, 742, letter[0] - 54, 742)
    
    # Footer Format
    canvas.line(54, 60, letter[0] - 54, 60)
    canvas.drawString(54, 45, "Footer: Conference 2026 | Poster Abstracts")
    
    # Dynamic Page Numbering
    page_num = canvas.getPageNumber()
    canvas.drawRightString(letter[0] - 54, 45, f"Page {page_num}")
    
    canvas.restoreState()


def create_formatted_pdf(filename, dataList):
    # Setup document geometry (54 points = 0.75 inch margins)
    # topMargin and bottomMargin ensure the main content doesn't overlap header/footer
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=80,
        bottomMargin=80
    )
    
    styles = getSampleStyleSheet()
    story = []

    heading_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading1'],
        fontName='Times-Roman',
        fontSize=18,
        textColor= "black",
        spaceAfter=12
    )

    normalArial_style = ParagraphStyle(
        'NormalArial',
        parent=styles['Normal'],
        fontName='ArialUnicode'  # <--- Change this from Helvetica to loaded font
    )

    normalGray_style = ParagraphStyle(
        'NormalArial',
        parent=styles['Normal'],
        textColor= "gray",
    )

    # Generate multi-page content
    for page_idx, paper in enumerate(dataList):
        print(f"Processing paper {page_idx+1}/{len(dataList)}: {paper.title}")
        # Section Heading
        # heading_text = f"Abstract {page_idx+1}: {paper.title}"
    
        story.append(Paragraph(process_inline_math(paper.title, target_height = 18), heading_style)) 

        # Body Content
        author_text = ""
        for author in paper.authors:
            author_text += f"{author.given_name} {author.family_name}, "
        author_text = author_text.rstrip(", ")  # Remove trailing comma
        story.append(Paragraph(process_inline_math(author_text), normalArial_style))
    
        text = f'''<br/><b>Abstract</b> <br/>'''
        story.append(Paragraph(text, styles['Normal']))
        body_text = f'''{paper.abstract}'''
        story.append(Paragraph(process_inline_math(body_text), normalArial_style))

        if paper.topics != "":
            text = f'''<br/><br/><b>Topics:</b> {paper.topics}'''
            story.append(Paragraph(text, styles['Normal']))

        text = f'''<br/><br/>poster ID {paper.pid} | session {paper.snum}'''
        story.append(Paragraph(text, normalGray_style))

        # story.append(Paragraph("<br/><br/><b>Contacts</b>:"))
        # for contact in paper.contacts:
        #     story.append(Paragraph(
        #         f"{contact.given_name} {contact.family_name}: {contact.email}, {contact.affiliation}", 
        #         styles['Normal']))

        # Force a page break
        from reportlab.platypus import PageBreak
        story.append(PageBreak())
            
    # Build document and bind the exact same formatting function to all pages
    doc.build(
        story, 
        onFirstPage=draw_page_format, 
        onLaterPages=draw_page_format
    )
