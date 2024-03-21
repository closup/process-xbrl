from utils.Context import Context
from utils.Cell import Cell
from utils.helper_functions import *
import pandas as pd
from utils.constants import *
from typing import * # to specify funtion inputs and outputs
from datetime import datetime # for date parsing


class Sheet:
    """ Object to represent an Excel sheet tab (one table) """
    def __init__(self, excel_file: str, sheet_name: str, extra_left_cols: int = 2):
        """ 
        Initialize Sheet object 
        Inputs:
            excel_file : file location for file to convert to XBRL 
            sheet_name : name of relevant tab on Excel sheet 
            extra_left_cols : number of untaggable columns to the left of data """
        self.df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        self.extra_left_cols = extra_left_cols
        self.parse_header()
        self.reshape_data()
        self.initialize_col_names()
        self.process_cells()
        self.mark_first_numeric_row()
        self.process_contexts()

    def parse_header(self) -> str:
        """Generate header text for the HTML rendering"""
        self.header = []
        for i in range(3):
            line = print_nicely(clean(self.df.iloc[i,0]))
            if line != "":
                self.header.append(line)

    @property
    def header(self):
        return self.header

    def initialize_col_names(self):
        col_names = [col for col in self.df["header"]]
        self.col_names = [print_nicely(col) for i, col in enumerate(col_names) if col not in col_names[:i]]

    def process_cells(self):
        self.data = []
        for _, row in self.df.iterrows():
            if row["xbrl_element"] != "Choose from drop-down -->":
                self.data.append(Cell(row, self.time_type + self.date.strftime('%Y%m%d')))

    def mark_first_numeric_row(self):
        """ Finds the first row of taggable data """
        i = 0
        while self.data[i].value == "":
            i += 1
        row = self.data[i].row
        while self.data[i].row == row:
            self.data[i].set_first_row()
            i += 1

    def process_contexts(self):
        """ Grabs all unique contexts in """
        context_names = set(ix.col_name for ix in self.data)
        self.contexts = [Context(self.time_type, self.date, col) for col in context_names]
    
    def reshape_data(self, sheet_name : str) -> None:
        """
        Process Excel sheet data to extract values and cell locations
        Turns data into a df with one row per taggable item
        """   
        # clean column names
        self.df.columns = self.df.iloc[self.n_header_lines].apply(clean)
        self.df = self.df.drop(list(range(self.n_header_lines + 1)))
        
        # Record original row number (from Excel sheet)
        self.df["row"] = self.n_header_lines + self.df.index - 3
        n_rows_orig = len(self.df) # num of rows before reshaping

        # Reshape the DataFrame        
        id_cols = self.df.columns[:self.extra_left_cols].tolist() + ["row"]
        val_cols = self.df.columns[self.extra_left_cols:].tolist()
        self.df = pd.melt(self.df, id_vars=id_cols, value_vars=val_cols, var_name="header")
        print(self.df)

        # Calculate original sheet column and cell in Excel document
        self.df['col'] = [ALPHABET[i] for i in (self.extra_left_cols + (self.df.index // n_rows_orig))]
        cells = [f'{c}{r}' for c, r in zip(self.df['col'], self.df["row"])]
        self.df["id"] = [f'{sheet_name.replace(" ", "")}_{cell}' for cell in cells]
        self.df = self.df.sort_values(by=['row', 'col'])
        

    def parse_date(self):
        """ Use data in spreadsheet to define period or instance + parse date """
        if "for_the_year_ended_" in self.date:
            self.time_type = "D"
            self.date = str.replace(self.date, "for_the_year_ended_", "")
        else:
            self.time_type = "I"
        try:
        # First try parsing with the numerical year-month-day format (default if "date" in Excel)
            self.date = datetime.strptime(self.date, "%Y-%m-%d_%H:%M:%S")
        except ValueError:
            try:
                # If the above format fails, try the month-name_day,_year format.
                self.date = datetime.strptime(self.date, '%B_%d,_%Y')
            except ValueError:
                pass
        self.date_display = self.date.strftime("%B %d, %Y")
