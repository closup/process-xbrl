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
        print(f"Debug: Reading Excel file: {excel_file}, sheet: {sheet_name}")
        # Initialize the DataFrame as a private member
        self._df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        print(f"Debug: Initial DataFrame shape: {self._df.shape}")
        print(f"Debug: Initial DataFrame columns: {self._df.columns}")
        
        # Initialize the rest of the slots
        self.extra_left_cols = extra_left_cols 
        self.time_type = self.get_time_type()
        self.date = self.parse_date()
        self._header = self.get_header()
        self.sheet_name = sheet_name
        
        # Process underlying sheet
        try:
            print("Debug: Starting reshape_data")
            self.reshape_data()
            print("Debug: reshape_data completed")
            self._col_names = self.get_col_names()
        except Exception as e:
            print(f'Failed to parse {self.sheet_name}: {str(e)}')
            print(f"Debug: DataFrame state when error occurred:")
            print(f"Shape: {self._df.shape}")
            print(f"Columns: {self._df.columns}")
            print(f"First few rows:\n{self._df.head()}")
            raise e

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
        first_column = self._df[self._df.columns[0]]
        # Determine the index of the row which contains "XBRL Element" in the first column
        idx = first_column[first_column == "XBRL Element"].index

        # If "XBRL Element" is not found, return the number of rows in the DataFrame
        if idx.empty:
            return len(first_column)
        
        # Return the row number before "XBRL Element"
        return idx[0]
    
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
        print("Debug: Starting reshape_data")
        print(f"Debug: DataFrame shape before reshape: {self._df.shape}")
        
        # Clean column names and handle duplicates
        raw_columns = self._df.iloc[self.n_header_lines()].apply(clean)
        
        # First, identify which columns to keep
        columns_to_keep = []
        for i, col in enumerate(raw_columns):
            column_data = self._df.iloc[:, i]
            if not column_data.isna().all():
                columns_to_keep.append(i)
        
        # Keep only non-hidden columns
        self._df = self._df.iloc[:, columns_to_keep]
        raw_columns = raw_columns.iloc[columns_to_keep]
        
        # Now handle duplicate names
        unique_columns = []
        seen = set()
        for i, col in enumerate(raw_columns):
            if col in seen:
                unique_columns.append(f"{col}_{i}")
            else:
                unique_columns.append(col)
                seen.add(col)
        
        # Assign the new column names
        self._df.columns = unique_columns
        print(f"Debug: Columns after cleaning: {self._df.columns}")
        
        # Drop unneeded rows (above taggable portion)
        self._df.drop(index = self._df.index[:self.n_header_lines() + 1], inplace=True)
        self._df.reset_index(drop=True, inplace=True)
        print(f"Debug: DataFrame shape after dropping rows: {self._df.shape}")
        
        # Record original row number
        self._df["row"] = 1 + self.n_header_lines() + len(self.header()) + self._df.index  
        n_rows_orig = len(self._df) # num of rows before reshaping

        # Reshape using 'melt' to give one row per taggable item
        id_cols = self._df.columns[:self.extra_left_cols].tolist() + ["row"]
        val_cols = [col for col in self._df.columns[self.extra_left_cols:] 
                    if col != "row" and not col.startswith("nan_")]  # Exclude 'row' and duplicate 'nan' columns
        print(f"Debug: id_cols: {id_cols}")
        print(f"Debug: val_cols: {val_cols}")
        
        self._df = pd.melt(self._df, id_vars=id_cols, value_vars=val_cols, var_name="header")
        print(f"Debug: DataFrame shape after melt: {self._df.shape}")

        # Calculate original sheet column and cell in Excel document
        self._df['col'] = [ALPHABET[min(i, len(ALPHABET)-1)] for i in (self.extra_left_cols + (self._df.index // n_rows_orig))]
        cells = [f'{c}{r}' for c, r in zip(self._df['col'], self._df["row"])]
        self._df["id"] = [f'{self.sheet_name.replace(" ", "")}_{cell}' for cell in cells]
        
        print(f"Debug: Final DataFrame columns: {self._df.columns}")
        print(f"Debug: First few rows of final DataFrame:\n{self._df.head()}")

