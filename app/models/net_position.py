from app.models import Cell, Context, Dimension, Table
from app.utils.helper_functions import *
from typing import *
import pandas as pd

class NetPosition(Table):
    """ extends the Table class for statement of net position """

    def __init__(self, excel_file: str, sheet_name: str, extra_left_cols: int = 2):
        super().__init__(excel_file, sheet_name, extra_left_cols)
        self._data = []
        self._contexts = []
        self.process_cells()
        self.mark_first_numeric_row()

    @staticmethod
    def create_dim_list(col_name, fund_type = None):
        return [Dimension(col_name, fund_type)]

    def process_cells(self):
        """Create a list of Cell objects to represent Excel data"""
        
        for col_name in self._df['header'].unique():
            
            # for each column, create the relevant dimension and context 
            dim = self.create_dim_list(col_name)
            context = Context(self.time_type, self.date, col_name, dim)
            self._contexts.append(context)
            
            # Grab all cells within the given context
            rows = self._df[self._df['header'] == col_name]

            # Iterate through filtered rows and create Cell objects
            for _, row in rows.iterrows():
                xbrl_tag = str(row["xbrl_element"]).strip()
                value = row["value"]
                
                # Skip empty cells or those without XBRL tags
                if xbrl_tag == "Choose from drop-down -->":
                    continue
                
                try:
                    cell = Cell(id = row["id"], 
                              xbrl_tag = xbrl_tag, 
                              row_name = str(row["nan"]), 
                              col_name = str(row["header"]),
                              value = value,
                              context = context)
                    self._data.append(cell)
                except Exception as e:
                    print(f"Debug: Error creating cell for row {row}: {str(e)}")
                    continue
                    
        if self._data:
            self._data.sort()