from fpdf import FPDF
from datetime import date
from matplotlib import pyplot as plt
import tempfile
from matplotlib.ticker import (MultipleLocator)

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

        # add charts
        self.set_font('Arial', '', 12)
        x_axis_labels = [x+1 for x in range(data['max_cycle_length']+1)]
        y_axis_labels = [1,2,3,4]
        for i in range(1, data['num_cycles']+1):
            cycle = data["cycles"][i-1]

            # create pdf cell for current cycle
            self.cell(0, 50, '', 1, 0)
            self.set_x(12)
            self.cell(0, 10, f'Cycle {i}: {cycle["start_date"].strftime("%d/%m/%Y")}  |  period {cycle["period_length"]} days  |  cycle {cycle["cycle_length"]} days', 0, 1)

            # create figure
            fig, ax = plt.subplots(figsize=(9,2), tight_layout=True)
            ax.set_xticks(x_axis_labels)
            ax.xaxis.set_minor_locator(MultipleLocator(.5)) # add minor ticks between items
            ax.tick_params(which='minor', length=8)
            ax.tick_params(axis='x', which='major',length=0) # hide major ticks
            ax.set_xlim(x_axis_labels[0]-.5, x_axis_labels[-1]+.5)
            ax.set_yticks(y_axis_labels)

            # build cycle data and plot on bar graph
            cycle_days = [0 for x in range(cycle['cycle_length'])]
            start_date = cycle['start_date']
            for entry in cycle['period']:
                day_num = (entry['day'] - start_date).days
                cycle_days[day_num] = entry['period_numeric']
            ax.bar(range(1, len(cycle_days)+1), cycle_days, 1)

            # add cycle length line on second x axis
            ax_line = ax.twiny()
            ax_line.set_xticks(x_axis_labels)
            ax_line.plot([0.05 for x in range(cycle['cycle_length']+1)], lw=4, color='green')
            ax_line.set_xlim(x_axis_labels[0]-1, x_axis_labels[-1])
            ax_line.tick_params(axis='x', which='both',length=0) # hide all ticks
            ax_line.set_xticklabels([])
            ax_line.text(cycle['cycle_length']+0.7, 0.5, f'{cycle["cycle_length"]} days', horizontalalignment='right', color='green')
            ax_line.plot([cycle['cycle_length']], 0.1, "o", color='green')

            # create temp image file
            temp = tempfile.NamedTemporaryFile(suffix='.png')
            plt.savefig(temp)

            # add image to pdf at current y, x=12
            self.image(temp.name, 11, None, 185, 35) # name, x, y, w, h
            temp.close() # delete temp file
            self.ln(5) # 5 to pad gap


def create_report(data):
    pdf = PDF()
    pdf.alias_nb_pages() # replace {nb} value in page numbers
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.add_summary_section(data)
    pdf.add_charts_section(data)
    pdf.output(f'reports/Clue_Report_{date.today().strftime("%d-%m-%Y")}.pdf', 'F')