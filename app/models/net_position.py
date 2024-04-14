from app.models import Cell, Context, Dimension, Table
from app.utils.helper_functions import *
from typing import *

class NetPosition(Table):
    """ extends the Sheet class for statement of net position """

    def __init__(self, excel_file: str, sheet_name: str, extra_left_cols: int = 2):
        super().__init__(excel_file, sheet_name, extra_left_cols)
        self._data = []
        self._contexts = []
        self.process_cells()
        self.mark_first_numeric_row()

    def process_cells(self):
        """Create a list of Cell objects to represent Excel data"""
        for col_name in self._df['header'].unique():
            # for each column, create the relevant dimension and context 
            dim = [Dimension(col_name)]
            context = Context(self.time_type, self.date, col_name, dim)
            # add new context to sheet's list
            self._contexts.append(context)
            
            # Grab all cells within the given context
            rows = self._df[self._df['header'] == col_name]

            # Iterate through filtered rows and create Cell objects with the specified context
            for _, row in rows.iterrows():
                xbrl_tag = str(row["xbrl_element"]).strip()
                if xbrl_tag != "Choose from drop-down -->":
                    cell = Cell(id = row["id"], 
                                xbrl_tag = xbrl_tag, 
                                row_name = str(row["nan"]), 
                                col_name = str(row["header"]),
                                value = row["value"],
                                context = context)
                    self._data.append(cell)
        # put data back in its original order
        self._data.sort()