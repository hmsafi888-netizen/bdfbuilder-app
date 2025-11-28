import streamlit as st
from io import BytesIO
import os

# Page setup
st.set_page_config(page_title="Arabic PDF Builder", layout="centered")

st.title("📄 Arabic PDF Builder")
st.markdown("Create beautiful PDFs with Arabic text and decorative borders")

# Check for required packages
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import simpleSplit
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase import pdfmetrics
    import arabic_reshaper
    from bidi.algorithm import get_display
    import requests
    DEPENDENCIES_INSTALLED = True
except ImportError as e:
    DEPENDENCIES_INSTALLED = False
    st.error("⚠️ Required packages are not installed!")
    st.markdown("""
    ### 📦 Missing Dependencies Detected
    
    Please create a `requirements.txt` file in your project root with:
    
    ```
    streamlit
    reportlab
    arabic-reshaper
    python-bidi
    requests
    ```
    
    ### For Streamlit Cloud:
    1. Create `requirements.txt` in your GitHub repository
    2. Add the packages listed above
    3. Commit and push
    4. Click "Reboot app" in the Manage App menu
    
    ### For Local Development:
    ```bash
    pip install reportlab arabic-reshaper python-bidi requests
    ```
    
    Then restart your Streamlit app.
    """)
    st.stop()

# Download Arabic font if not exists
@st.cache_resource
def download_arabic_font():
    """Download Arabic font for PDF generation"""
    font_path = "NotoNaskhArabic-Regular.ttf"
    
    if not os.path.exists(font_path):
        try:
            # Download Noto Naskh Arabic font from Google Fonts
            url = "https://github.com/google/fonts/raw/main/ofl/notonaskharabic/NotoNaskhArabic%5Bwght%5D.ttf"
            response = requests.get(url)
            with open(font_path, 'wb') as f:
                f.write(response.content)
            return font_path
        except:
            return None
    return font_path

# Load the font
arabic_font_path = download_arabic_font()

# Sidebar for options
st.sidebar.header("⚙️ PDF Settings")

# Title Section
st.subheader("📌 Title (First Page Header)")
title_text = st.text_input(
    "Enter Title:",
    placeholder="عنوان المستند",
    help="This will appear at the top of the first page"
)

col1, col2 = st.columns(2)
with col1:
    title_font_size = st.number_input(
        "Title Font Size:",
        min_value=16,
        max_value=48,
        value=24,
        step=2,
        help="Font size for the title"
    )
with col2:
    title_bold = st.checkbox("Bold Title", value=True)

st.markdown("---")

# Body text Section
st.subheader("📄 Body Content")
arabic_text = st.text_area(
    "Enter Body Text:",
    height=200,
    placeholder="اكتب النص العربي هنا...",
    help="Enter your main content here"
)

# Font size selection for body
font_size = st.sidebar.slider(
    "Body Font Size:",
    min_value=10,
    max_value=24,
    value=14,
    step=1,
    help="Select the font size for body text"
)

# Line spacing
line_spacing = st.sidebar.slider(
    "Line Spacing:",
    min_value=1.0,
    max_value=2.5,
    value=1.5,
    step=0.1,
    help="Adjust spacing between lines"
)

# Margin settings
margin_top = st.sidebar.number_input("Top Margin (mm):", min_value=20, max_value=50, value=35)
margin_bottom = st.sidebar.number_input("Bottom Margin (mm):", min_value=20, max_value=50, value=35)
margin_left = st.sidebar.number_input("Left Margin (mm):", min_value=15, max_value=40, value=25)
margin_right = st.sidebar.number_input("Right Margin (mm):", min_value=15, max_value=40, value=25)

# Text alignment
text_align = st.sidebar.selectbox(
    "Text Alignment:",
    ["Right (Arabic)", "Center", "Justify"],
    help="Choose text alignment"
)


def mm_to_points(mm):
    """Convert millimeters to points"""
    return mm * 2.83465


def draw_decorative_border(c, width, height):
    """Draw decorative corner borders on the page"""
    c.setStrokeColorRGB(0.72, 0.53, 0.04)  # Golden color
    c.setLineWidth(2)
    
    # Top right corner decoration
    corner_size = 60
    
    # Top right ornamental corner
    c.circle(width - 30, height - 30, 8, stroke=1, fill=0)
    c.circle(width - 45, height - 20, 5, stroke=1, fill=0)
    c.circle(width - 20, height - 45, 5, stroke=1, fill=0)
    c.line(width - 30, height - 30, width - 30, height - corner_size)
    c.line(width - 30, height - 30, width - corner_size, height - 30)
    
    # Bottom left corner decoration
    c.setStrokeColorRGB(0.0, 0.6, 0.8)  # Blue color
    c.circle(30, 30, 8, stroke=1, fill=0)
    c.circle(45, 40, 5, stroke=1, fill=0)
    c.circle(40, 45, 5, stroke=1, fill=0)
    c.line(30, 30, 30, corner_size + 30)
    c.line(30, 30, corner_size + 30, 30)
    c.circle(25, 50, 3, stroke=1, fill=0)
    c.circle(50, 25, 3, stroke=1, fill=0)
    
    # Horizontal line at bottom
    c.line(corner_size + 40, 30, width - 30, 30)


def create_pdf(text, font_size, line_spacing, margins, alignment):
    """Create PDF with Arabic text and decorative borders"""
    buffer = BytesIO()
    
    # Create PDF canvas
    page_width, page_height = A4
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Register Arabic font (using downloaded Noto Naskh Arabic)
    try:
        if arabic_font_path and os.path.exists(arabic_font_path):
            pdfmetrics.registerFont(TTFont('Arabic', arabic_font_path))
            font_name = 'Arabic'
        else:
            # Fallback to Helvetica if Arabic font not available
            font_name = 'Helvetica'
            st.warning("⚠️ Arabic font not available, using fallback. Text may not display correctly.")
    except Exception as e:
        font_name = 'Helvetica'
        st.warning(f"⚠️ Could not load Arabic font: {e}")
    
    # Convert margins to points
    margin_top_pt = mm_to_points(margins['top'])
    margin_bottom_pt = mm_to_points(margins['bottom'])
    margin_left_pt = mm_to_points(margins['left'])
    margin_right_pt = mm_to_points(margins['right'])
    
    # Calculate text area
    text_width = page_width - margin_left_pt - margin_right_pt
    text_height = page_height - margin_top_pt - margin_bottom_pt
    
    # Set font
    c.setFont(font_name, font_size)
    
    # Process Arabic text
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    
    # Split text into lines that fit the width
    lines = []
    paragraphs = bidi_text.split('\n')
    
    for paragraph in paragraphs:
        if paragraph.strip():
            wrapped_lines = simpleSplit(paragraph, font_name, font_size, text_width)
            lines.extend(wrapped_lines)
        else:
            lines.append('')  # Empty line for paragraph breaks
    
    # Calculate line height
    line_height = font_size * line_spacing
    
    # Paginate
    lines_per_page = int(text_height / line_height)
    total_pages = (len(lines) + lines_per_page - 1) // lines_per_page
    
    page_number = 1
    
    for page_start in range(0, len(lines), lines_per_page):
        if page_start > 0:
            c.showPage()  # New page
            c.setFont(font_name, font_size)
        
        # Draw decorative borders
        draw_decorative_border(c, page_width, page_height)
        
        # Get lines for this page
        page_lines = lines[page_start:page_start + lines_per_page]
        
        # Draw text
        y_position = page_height - margin_top_pt
        
        for line in page_lines:
            if line.strip():
                # Calculate x position based on alignment
                if alignment == "Right (Arabic)":
                    x_position = page_width - margin_right_pt
                    c.drawRightString(x_position, y_position, line)
                elif alignment == "Center":
                    x_position = page_width / 2
                    c.drawCentredString(x_position, y_position, line)
                else:  # Justify
                    x_position = page_width - margin_right_pt
                    c.drawRightString(x_position, y_position, line)
            
            y_position -= line_height
        
        # Add page number
        c.setFont("Helvetica", 10)
        page_text = f"Page {page_number} of {total_pages}"
        c.drawCentredString(page_width / 2, 15, page_text)
        
        page_number += 1
    
    # Save PDF
    c.save()
    buffer.seek(0)
    return buffer


# Generate PDF button
if st.button("🎨 Generate PDF", type="primary", use_container_width=True):
    if not arabic_text.strip():
        st.error("⚠️ Please enter some body text first!")
    else:
        with st.spinner("Creating your PDF..."):
            try:
                margins = {
                    'top': margin_top,
                    'bottom': margin_bottom,
                    'left': margin_left,
                    'right': margin_right
                }
                
                pdf_buffer = create_pdf(
                    title_text,
                    title_font_size,
                    title_bold,
                    arabic_text,
                    font_size,
                    line_spacing,
                    margins,
                    text_align
                )
                
                st.success("✅ PDF created successfully!")
                
                # Preview info
                info_text = f"""
                **PDF Details:**
                - Title: {'Yes' if title_text else 'No title'}
                - Title Font Size: {title_font_size}pt
                - Body Font Size: {font_size}pt
                - Line Spacing: {line_spacing}
                - Alignment: {text_align}
                - Margins: T:{margin_top}mm, B:{margin_bottom}mm, L:{margin_left}mm, R:{margin_right}mm
                """
                st.info(info_text)
                
                # Download button
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_buffer,
                    file_name="arabic_document.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Error creating PDF: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
### 📝 Instructions:
1. **Enter a title** (optional) - This will appear at the top of the first page
2. **Adjust title settings** - Font size and bold options
3. **Enter your body text** in the text area
4. **Adjust body settings** in the sidebar (font size, spacing, margins)
5. **Click Generate PDF** to create your document
6. **Download** your beautifully formatted PDF

**Note:** The title appears centered on the first page only. Body text starts below the title.
""")
