from fpdf import FPDF
from datetime import date
from matplotlib import pyplot as plt
import tempfile
from matplotlib.ticker import (MultipleLocator)
from datetime import timedelta

class PDF(FPDF):

    def header(self):
        # Title
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'Clue Period Tracker Report', 0, 1, 'C')

        # Subtitle
        self.set_font('Arial', '', 11)
        self.cell(0, 10, f'Generated {date.today().strftime("%d/%m/%Y")}', 0, 1, 'C')

        # Line break
        self.ln(10)

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
        self.ln(4)

        # summary charts
        self.cell(92, 72, '', 1, 0)
        self.set_x(108) # gap
        self.cell(92, 72, '', 1, 0)
        self.set_x(12) # return cursor to start of row

        # headers
        self.set_font('Arial', 'B', 14)
        self.cell(88, 10, 'Cycle Length', 0, 0, 'C')
        self.set_x(110) # gap
        self.cell(88, 10, 'Period Length', 0, 1, 'C')

        # average
        self.set_font('Arial', '', 11)
        self.cell(88, 10, f'Average: {data["average_cycle_length"]:.1f} days', 0, 0, 'C')
        self.set_x(110) # move to start of second chart
        self.cell(88, 10, f'Average: {data["average_period_length"]:.1f} days', 0, 1, 'C')

        # add charts
        image_height = 50
        cycle_nums = range(data["num_cycles"])
        cycle_lengths = [cycle['cycle_length'] for cycle in data['cycles']]
        period_lengths = [cycle['period_length'] for cycle in data['cycles']]
        self.add_summary_chart(
            x_label='Time', x_values=cycle_nums, 
            y_label='Days in cycle', y_values=cycle_lengths, 
            x=11, image_width=88, image_height=image_height)
        self.set_y(self.get_y() - image_height) # return cursor to image x
        self.add_summary_chart(
            x_label='Time', x_values=cycle_nums, 
            y_label='Days on', y_values=period_lengths, 
            x=110, image_width=88, image_height=image_height)
        self.ln(10) # gap

    def add_summary_chart(self, x_values, y_values, y_label, x_label, image_height, image_width, x):
        fig, ax = plt.subplots(figsize=(3.5, 2), tight_layout=True) 
        ax.scatter(x_values, y_values, marker="x")
        ax.set_ylim(max(0, min(y_values)-2), max(y_values)+1)
        ax.set_ylabel(y_label)
        ax.tick_params(axis='x', which='major',length=0) # hide major ticks
        ax.get_xaxis().set_ticks([])
        ax.set_xlabel(x_label)

        # create temp image file and add to pdf
        temp = tempfile.NamedTemporaryFile(suffix='.png')
        plt.savefig(temp)
        self.image(temp.name, x, None, image_width, image_height)
        temp.close() # delete temp file

    def add_cycle_detail_section(self, data):

        # section heading
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Cycle Detail', 0, 1, 'L')
        self.ln(2)

        # add charts
        c1 = 'C0'
        x_axis_labels = [x+1 for x in range(data['max_cycle_length']+1)]
        y_axis_labels = [1,2,3]
        for i in range(1, data['num_cycles']+1):
            cycle = data["cycles"][i-1]

            # create pdf cell for current cycle
            self.cell(0, 45, '', 1, 0)
            self.set_x(12)
            self.set_font('Arial', 'B', 12)
            str1 = f'Cycle {i}:  '
            self.cell(self.get_string_width(str1), 10, str1, 0, 0)
            self.set_font('Arial', 'I', 11)
            self.cell(0, 10, f'{cycle["start_date"].strftime("%d-%b-%Y")} - {(cycle["start_date"] + timedelta(days=cycle["cycle_length"]-1)).strftime("%d-%b-%Y")}', 0, 1)

            # build cycle data and plot on bar graph
            start_date = cycle['start_date']
            period_days = [0 for x in range(cycle['cycle_length'])]
            spotting_days = [-1 for x in range(cycle['cycle_length'])]
            for entry in cycle['period']:
                day_num = (entry['day'] - start_date).days
                if entry['period_numeric'] == 1:
                    spotting_days[day_num] = 0.4
                else:
                    period_days[day_num] = entry['period_numeric']-1

            fig, ax = plt.subplots(figsize=(10, 1.5), tight_layout=True)
            ax.bar(range(1, len(period_days)+1), period_days, 1, color=c1) # period bars
            ax.scatter(range(1, len(spotting_days)+1), spotting_days, s=70, color=c1) # spotting markers
            ax.xaxis.set_minor_locator(MultipleLocator(.5)) # add minor ticks between items
            ax.set_xlim(x_axis_labels[0]-0.5, x_axis_labels[-1]+0.5)
            ax.tick_params(which='minor', length=8)
            ax.tick_params(axis='x', which='major',length=0) # hide major ticks
            ax.set_xticks(x_axis_labels)
            ax.set_yticks(y_axis_labels)
            ax.set_ylim(0, 3.2)
            ax.text(cycle['period_length']+0.9, 1, f'{cycle["period_length"]} days on ({cycle["cycle_length"]-cycle["period_length"]} days off)', horizontalalignment='left', color=c1, style='italic')

            # add cycle length line on second x axis
            ax_line = ax.twiny()
            ax_line.set_xticks(x_axis_labels)
            ax_line.plot([0.05 for x in range(cycle['cycle_length']+1)], linewidth=4, color=c1) # cycle length line
            ax_line.set_xlim(x_axis_labels[0]-1, x_axis_labels[-1])
            ax_line.tick_params(axis='x', which='both',length=0) # hide all ticks
            ax_line.set_xticklabels([])
            ax_line.text(cycle['cycle_length']+0.85, 0.75, f'{cycle["cycle_length"]} days', horizontalalignment='right', color=c1)
            ax_line.scatter([cycle['cycle_length']], 0.2, s=200, marker="|", color=c1, linewidth=4)

            # create temp image file
            temp = tempfile.NamedTemporaryFile(suffix='.png')
            plt.savefig(temp)

            # add image to pdf at current y, x=12
            self.image(temp.name, 11, None, 185, 30) # name, x, y, w, h
            temp.close() # delete temp file
            self.ln(5) # 5 to pad gap


def create_report(data):
    pdf = PDF()
    pdf.alias_nb_pages() # replace {nb} value in page numbers
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.add_summary_section(data)
    pdf.add_cycle_detail_section(data)
    pdf.output(f'reports/Clue_Report_{date.today().strftime("%d-%m-%Y")}.pdf', 'F')