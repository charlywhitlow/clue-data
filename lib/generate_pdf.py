from fpdf import FPDF
from datetime import date


class PDF(FPDF):

    def header(self):
        # Title
        self.set_font('Arial', 'B', 24)
        self.cell(0, 10, 'Clue Period Tracker Report', 0, 1, 'C')

        # Subtitle
        self.set_font('Arial', '', 12)
        self.cell(0, 10, f'Generated {date.today().strftime("%d/%m/%Y")}', 0, 1, 'C')

        # Line break
        self.ln(5)

    def footer(self):
        # Page numbers       
        self.set_y(-15) # position 15mm from bottom of page
        self.set_font('Arial', '', 8)
        self.set_text_color(128) # gray
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C') # {nb} values replaced by alias_nb_pages()

    def add_charts(self):
        
        # section heading
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Cycle Detail', 0, 1, 'L')

        # charts
        self.set_font('Arial', '', 12)
        for i in range(1, 41):
            self.cell(0, 20, 'Cycle ' + str(i), 1, 1)
            # TODO


pdf = PDF()
pdf.alias_nb_pages() # replace {nb} value in page numbers
pdf.add_page()
pdf.set_font('Arial', '', 12)
pdf.add_charts()
pdf.output(f'reports/Clue_Report_{date.today().strftime("%d-%m-%Y")}.pdf', 'F')