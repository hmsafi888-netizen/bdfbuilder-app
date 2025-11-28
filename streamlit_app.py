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


# Generate PDF button
if st.button("🎨 Generate PDF", type="primary", use_container_width=True):
    if not arabic_text.strip():
        st.error("⚠️ Please enter some body text first!")
    else:
        with st.spinner("Creating your PDF..."):
            try:
                # Create PDF directly here
                buffer = BytesIO()
                
                # Create PDF canvas
                page_width, page_height = A4
                c = canvas.Canvas(buffer, pagesize=A4)
                
                # Register Arabic font
                try:
                    if arabic_font_path and os.path.exists(arabic_font_path):
                        pdfmetrics.registerFont(TTFont('Arabic', arabic_font_path))
                        font_name = 'Arabic'
                    else:
                        font_name = 'Helvetica'
                        st.warning("⚠️ Arabic font not available, using fallback.")
                except Exception as e:
                    font_name = 'Helvetica'
                    st.warning(f"⚠️ Could not load Arabic font: {e}")
                
                # Convert margins to points
                margin_top_pt = mm_to_points(margin_top)
                margin_bottom_pt = mm_to_points(margin_bottom)
                margin_left_pt = mm_to_points(margin_left)
                margin_right_pt = mm_to_points(margin_right)
                
                # Calculate text area
                text_width = page_width - margin_left_pt - margin_right_pt
                text_height = page_height - margin_top_pt - margin_bottom_pt
                
                # Process title if provided
                title_lines = []
                title_height = 0
                if title_text and title_text.strip():
                    reshaped_title = arabic_reshaper.reshape(title_text)
                    bidi_title = get_display(reshaped_title)
                    
                    # Split title into lines if too long
                    title_lines = simpleSplit(bidi_title, font_name, title_font_size, text_width)
                    title_line_height = title_font_size * 1.5
                    title_height = len(title_lines) * title_line_height + 20  # Add spacing after title
                
                # Adjust text area for title on first page
                first_page_text_height = text_height - title_height
                
                # Process body text
                reshaped_text = arabic_reshaper.reshape(arabic_text)
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
                
                # Paginate - first page has less space due to title
                lines_on_first_page = int(first_page_text_height / line_height) if first_page_text_height > 0 else 0
                lines_per_page = int(text_height / line_height)
                
                page_number = 1
                line_index = 0
                
                while line_index < len(lines):
                    if page_number > 1:
                        c.showPage()
                    
                    # Draw decorative borders
                    draw_decorative_border(c, page_width, page_height)
                    
                    # Draw title on first page only
                    y_position = page_height - margin_top_pt
                    if page_number == 1 and title_lines:
                        # Set title font
                        c.setFont(font_name, title_font_size)
                        
                        # Draw title lines
                        for title_line in title_lines:
                            # Center align title
                            x_position = page_width / 2
                            c.drawCentredString(x_position, y_position, title_line)
                            y_position -= title_font_size * 1.5
                        
                        # Add spacing after title
                        y_position -= 20
                    
                    # Set body font
                    c.setFont(font_name, font_size)
                    
                    # Determine how many lines for this page
                    if page_number == 1:
                        lines_this_page = min(lines_on_first_page, len(lines) - line_index)
                    else:
                        lines_this_page = min(lines_per_page, len(lines) - line_index)
                    
                    # Get lines for this page
                    page_lines = lines[line_index:line_index + lines_this_page]
                    
                    # Draw body text
                    for line in page_lines:
                        if line.strip():
                            # Calculate x position based on alignment
                            if text_align == "Right (Arabic)":
                                x_position = page_width - margin_right_pt
                                c.drawRightString(x_position, y_position, line)
                            elif text_align == "Center":
                                x_position = page_width / 2
                                c.drawCentredString(x_position, y_position, line)
                            else:  # Justify
                                x_position = page_width - margin_right_pt
                                c.drawRightString(x_position, y_position, line)
                        
                        y_position -= line_height
                    
                    # Add page number
                    c.setFont(font_name, 10)
                    
                    # Calculate total pages
                    remaining_lines = len(lines) - lines_on_first_page
                    if remaining_lines > 0:
                        total_pages = 1 + ((remaining_lines + lines_per_page - 1) // lines_per_page)
                    else:
                        total_pages = 1
                    
                    page_text = f"Page {page_number} of {total_pages}"
                    c.drawCentredString(page_width / 2, 15, page_text)
                    
                    line_index += lines_this_page
                    page_number += 1
                
                # Save PDF
                c.save()
                buffer.seek(0)
                
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
                    data=buffer,
                    file_name="arabic_document.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Error creating PDF: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

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
