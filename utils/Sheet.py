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
        # Initialize the DataFrame as a private member
        self._df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        self.extra_left_cols = extra_left_cols
        # Initialize internal state
        self.header = []
        self.col_names = []
        self.data = self.process_cells() 
        self.contexts = self.process_contexts()  
        self.n_header_lines = 0
        self.time_type = ""
        self.date = None
        # Begin processing
        self.parse_header()
        self.reshape_data()
        self.initialize_col_names()
        
        self.mark_first_numeric_row()
        self.process_contexts()
    
    @property
    def header(self):
        return self.header
    
    @property
    def data(self):
        return self.data
    
    @property
    def col_names(self):
        return self.col_names

    def parse_header(self):
        """ Header at the top of each sheet containing city, date, etc"""
        self.header = [print_nicely(clean(self._df.iloc[i, 0])) for i in range(3)]
        self.date = clean(self._df.iloc[3, 0])
        self.parse_date()
        # determine number of lines above the first taggable row
        self.n_header_lines = self._df[self._df.columns[-1]].first_valid_index()

    def initialize_col_names(self):
        """ Get unique column names in the sheet """
        col_names = [col for col in self.df["header"]]
        self.col_names = [print_nicely(col) for i, col in enumerate(col_names) if col not in col_names[:i]]

    def process_cells(self):
        """ Create a list of Cell objects to represent all """
        data = []
        for _, row in self._df.iterrows():
            if row["xbrl_element"] != "Choose from drop-down -->":
                date_id = self.time_type + self.date.strftime('%Y%m%d')
                xbrl_tag = str(row["xbrl_element"]).strip()
                cell = Cell(id = row["id"], 
                            xbrl_tag = xbrl_tag, 
                            row_name = row["nan"], 
                            col_name = row["header"],
                            value = format_value(row["value"]),
                            date_id = date_id)
                data.append(cell)
        return data

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
        context_names = set(ix.col_name() for ix in self.data)
        return [Context(self.time_type, self.date, col) for col in context_names]
    
    def reshape_data(self, sheet_name : str) -> None:
        """
        Process Excel sheet data to extract values and cell locations
        """   
        # Clean column names
        self._df.columns = self._df.iloc[self.n_header_lines].apply(clean)
        # Drop unneeded rows (above taggable portion)
        self._df.drop(index = self._df.index[:self.n_header_lines + 1], inplace=True)
        
        # Record original row number
        self._df.reset_index(drop=True, inplace=True)
        self._df["row"] = self.n_header_lines + 1 + self._df.index

        # Reshape using 'melt' to give one row per taggable item
        id_cols = self._df.columns[:self.extra_left_cols].tolist() + ["row"]
        val_cols = self._df.columns[self.extra_left_cols:].tolist()
        self._df = pd.melt(self._df, id_vars=id_cols, value_vars=val_cols, var_name="header")

        # Calculate original sheet column and cell in Excel document
        self._df['col'] = self._df.index // len(self._df) % len(val_cols) + self.extra_left_cols
        self._df['col'] = self._df['col'].apply(lambda x: ALPHABET[x])
        cells = [f'{c}{r}' for c, r in zip(self._df['col'], self._df["row"])]
        self._df["id"] = [f'{sheet_name.replace(" ", "")}_{cell}' for cell in cells]
        self._df = self._df.sort_values(by=['row', 'col'])
        

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
