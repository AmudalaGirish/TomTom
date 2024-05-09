import os
from pyhtml2pdf import converter

path = os.path.abspath('C:/Girish/Django practice projects/TomTom/tomtom/maps/templates/maps/sample_invoice.html')

# Convert the HTML file to PDF
pdf_filename = 'sample.pdf'
converter.convert(f"file:///{path}", pdf_filename)

print(f'PDF file "{pdf_filename}" has been created.')