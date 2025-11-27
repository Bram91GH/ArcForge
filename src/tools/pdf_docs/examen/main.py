from weasyprint import HTML, CSS
import sys
import os

def html_to_pdf(input_html, output_pdf):
    if not os.path.exists(f"templates/{input_html}"):
        print(f"Error: '{input_html}' not found.")
        return

    css = CSS(f"static/src/css/test_file.css")
    HTML(f"templates/{input_html}").write_pdf(f"outputs/{output_pdf}", stylesheets=[css])
    print(f"PDF created successfully: {output_pdf}")



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python html_to_pdf.py input.html output.pdf")
        sys.exit(1)

    html_file = sys.argv[1]
    pdf_file = sys.argv[2]

    html_to_pdf(html_file, pdf_file)
