from app.models import Table, Cell
from app.utils import *
import pandas as pd

class Reconciliation(Table):
    """ Extends net position class to add an extra header row """

    def __init__(self, excel_file: str, sheet_name: str, extra_left_cols: int = 1):
        super().__init__(excel_file, sheet_name, extra_left_cols)
        self._data = []
        self._contexts = []
        self.process_cells()
        print(self._data)
        self.mark_first_numeric_row()

    def process_cells(self):
        """Create a list of Cell objects to represent Excel data"""
        print(f"df : {self._df}")
        for col_name in self._df['header'].unique():
            # get the rows
            rows = self._df[self._df['header'] == col_name]

            # Iterate through filtered rows and create Cell objects with the specified context
            for _, row in rows.iterrows():
                print(f'row: {row["nan"]}; col: {row["header"]}')
                cell = Cell(id = row["id"], 
                            xbrl_tag = None, 
                            row_name = str(row["nan"]), 
                            col_name = str(row["header"]),
                            value = row["value"],
                            context = None)
                self._data.append(cell)
        # put data back in its original order
        self._data.sort()

    def n_header_lines(self) -> int:
        # determine number of lines above the first taggable row
        # TODO: fix to find first numeric row?
        return 4 #self._df[self._df.columns[-1]].first_valid_index()

    def reshape_data(self) -> None:
        """
        Process Excel sheet data to extract values and cell locations
        """   
        # Assign column names
        self._df.columns = ["nan", "Amount"]

        # Drop unneeded rows (above taggable portion)
        self._df.drop(index = self._df.index[:self.n_header_lines() + 1], inplace=True)
        self._df.reset_index(drop=True, inplace=True)
        
        # Record original row number
        self._df["row"] = 1 + self.n_header_lines() + len(self.header()) + self._df.index  
        n_rows_orig = len(self._df) # num of rows before reshaping

        # Reshape using 'melt' to give one row per taggable item
        id_cols = self._df.columns[:self.extra_left_cols].tolist() + ["row"]
        val_cols = self._df.columns[self.extra_left_cols:].tolist()
        print(f"id_cols: {id_cols}; val_cols: {val_cols}")
        self._df = pd.melt(self._df, id_vars=id_cols, value_vars=val_cols, var_name="header")

        # Calculate original sheet column and cell in Excel document
        self._df['col'] = [ALPHABET[i] for i in (self.extra_left_cols + (self._df.index // n_rows_orig))]
        cells = [f'{c}{r}' for c, r in zip(self._df['col'], self._df["row"])]
        self._df["id"] = [f'{self.sheet_name.replace(" ", "")}_{cell}' for cell in cells]
        self._df = self._df.sort_values(by=['row', 'col'])  

