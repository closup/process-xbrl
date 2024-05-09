from app.models import Context, Cell
from app.utils import *
import pandas as pd
from typing import * # to specify funtion inputs and outputs
from datetime import datetime # for date parsing

class Table:
    """ Object to represent an Excel sheet tab (one table) """
    def __init__(self, excel_file: str, sheet_name: str, extra_left_cols: int = 2):
        """ 
        Initialize Table object (a table in the excel sheet)
        Inputs:
            excel_file : file location for file to convert to XBRL 
            sheet_name : name of relevant tab on Excel sheet 
            extra_left_cols : number of untaggable columns to the left of data """
        # Initialize the DataFrame as a private member
        self._df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        # Initialize the rest of the slots
        self.extra_left_cols = extra_left_cols 
        self.time_type = self.get_time_type()
        self.date = self.parse_date()
        self._header = self.get_header()
        self.sheet_name = sheet_name
        # Process underlying sheet
        self.reshape_data()
        self._col_names = self.get_col_names()

    def data(self) -> List[Cell]:
        return self._data
    
    def col_names(self) -> List[str]:
        return self._col_names

    def city(self) -> str:
        return clean(self._df.iloc[0, 1])
    
    def scope(self) -> str:
        return clean(self._df.iloc[1, 1])
    
    def statement(self) -> str:
        return clean(self._df.iloc[2, 1])
    
    def raw_date(self) -> str:
        return clean(str(self._df.iloc[3, 1]))
    
    def formatted_date(self) -> str:
        if self.get_time_type() == 'D':
            return self.raw_date()
        return self.date.strftime('%B %d, %Y')

    def contexts(self) -> List[Context]:
        return self._contexts
    
    def header(self) -> List[str]:
        return self._header
    
    def get_time_type(self) -> str:
        """ Use data in spreadsheet to define period or instance + parse date """
        if "for_the_year_ended_" in self.raw_date():
            return "D"
        return "I" 

    def get_header(self) -> List[str]:
        """ Header at the top of each sheet containing city, date, etc"""
        return [print_nicely(line) for line in [self.city(), self.scope(), self.statement(), self.formatted_date()]]

    def n_header_lines(self) -> int:
        # determine number of lines above the first taggable row
        return self._df[self._df.columns[-1]].first_valid_index()
    
    def parse_date(self) -> datetime :
        """ Get date from spreadsheet and interpret """
        # clean date of extra words
        date = str.replace(self.raw_date(), "for_the_year_ended_", "")
        try:
        # First try parsing with the numerical year-month-day format (default if "date" in Excel)
            date = datetime.strptime(date, "%Y-%m-%d_%H:%M:%S")
        except ValueError:
            try:
                # If the above format fails, try the month-name_day,_year format.
                date = datetime.strptime(date, '%B_%d,_%Y')
            except ValueError:
                try: 
                    date = datetime.strptime(date, "%Y-%m-%d_%H%M%S")
                except ValueError:
                    pass
        finally:
            return date

    def get_col_names(self) -> List[str]:
        """ Get unique column names in the sheet """
        col_names = [col for col in self._df["header"]]
        return [print_nicely(col) for i, col in enumerate(col_names) if col not in col_names[:i]]

    def mark_first_numeric_row(self) -> None:
        """ Finds the first row of taggable data """
        i = 0
        while self._data[i].show_value() == "":
            # PRINT
            print(self._data[i].show_value())
            i += 1
        # tag all cells in that row
        row_name = self._data[i].row_name()
        while self._data[i].row_name() == row_name:
            self._data[i].set_first_row()
            i += 1
 
    def reshape_data(self) -> None:
        """
        Process Excel sheet data to extract values and cell locations
        """   
        # Clean column names
        self._df.columns = self._df.iloc[self.n_header_lines()].apply(clean)
        # Drop unneeded rows (above taggable portion)
        self._df.drop(index = self._df.index[:self.n_header_lines() + 1], inplace=True)
        
        # Record original row number
        self._df.reset_index(drop=True, inplace=True)
        self._df["row"] = 1 + self.n_header_lines() + len(self.header()) + self._df.index  
        n_rows_orig = len(self._df) # num of rows before reshaping

        # Reshape using 'melt' to give one row per taggable item
        id_cols = self._df.columns[:self.extra_left_cols].tolist() + ["row"]
        val_cols = self._df.columns[self.extra_left_cols:].tolist()
        self._df = pd.melt(self._df, id_vars=id_cols, value_vars=val_cols, var_name="header")

        # Calculate original sheet column and cell in Excel document
        self._df['col'] = [ALPHABET[i] for i in (self.extra_left_cols + (self._df.index // n_rows_orig))]
        cells = [f'{c}{r}' for c, r in zip(self._df['col'], self._df["row"])]
        self._df["id"] = [f'{self.sheet_name.replace(" ", "")}_{cell}' for cell in cells]
        self._df = self._df.sort_values(by=['row', 'col'])  

