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

    def add_summary_section(self, data):
        # heading
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Summary', 0, 1, 'L')
        self.ln(2)

        # summary stats
        self.set_font('Arial', '', 12)
        self.cell(0, 9, f'Number of cycles: {data["num_cycles"]}', 0, 1, 'L')
        self.cell(0, 9, f'Average cycle length: {data["average_cycle_length"]}', 0, 1, 'L')
        self.cell(0, 9, f'Average period length: {data["average_period_length"]}', 0, 1, 'L')
        self.ln(4)

    def add_charts_section(self, data):
        
        # section heading
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Detail', 0, 1, 'L')
        self.ln(2)

        # charts
        self.set_font('Arial', '', 12)
        for i in range(1, data['num_cycles']+1):
            cycle = data["cycles"][i-1]
            self.cell(0, 10, f'Cycle {i}: {cycle["start_date"].strftime("%d/%m/%Y")}  (period {cycle["period_length"]} days - cycle {cycle["cycle_length"]} days)', 1, 1)
            self.cell(0, 20, f'[CHART]', 1, 1)
            self.ln(3)
            

def create_report(data):
    pdf = PDF()
    pdf.alias_nb_pages() # replace {nb} value in page numbers
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.add_summary_section(data)
    pdf.add_charts_section(data)
    pdf.output(f'reports/Clue_Report_{date.today().strftime("%d-%m-%Y")}.pdf', 'F')