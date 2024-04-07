from utils.Table import Table
from utils.Cell import Cell
from utils.Context import Context
from utils.Dimension import Dimension
from utils.helper_functions import *
from typing import *
from utils.constants import *

class StatementofActivities(Table):
    """ extends the Sheet class for statement of activities """

    def __init__(self, excel_file: str, sheet_name: str, extra_left_cols: int = 2):
        super().__init__(excel_file, sheet_name, extra_left_cols)
        self._data = []
        self._contexts = []
        self.process_cells()
        self.mark_first_numeric_row()

    def add_context(self, col_name : str, dims : List[Dimension]) -> Context:
        """ create a new context and add it to the sheet list """
        # create context
        context = Context(self.time_type, self.date, col_name, dims)
        # add new context to sheet's list
        self._contexts.append(context) 
        return context

    def process_cells(self):
        """Create a list of Cell objects to represent Excel data"""
        for col_name in self._df['header'].unique():

            # for each column, create corresponding context
            dims = [Dimension(col_name)]
            context = self.add_context(col_name, dims)        
            
            # Grab all cells in the given column
            rows = self._df[self._df['header'] == col_name]
            # initialize section
            section = ""
            for _, row in rows.iterrows():

                # process xbrl tags according to the relevant column groups 
                # (see color coding on Excel sheet)
                xbrl_list = str(row["xbrl_element"]).strip().split(',')
                if len(xbrl_list) == 1 or col_name == "expenses":
                    xbrl_tag = xbrl_list[0]
                elif col_name in DIMENSIONS["TypeOfProgramRevenues"]:
                    xbrl_tag = xbrl_list[1]
                else:
                    xbrl_tag = xbrl_list[2]
                
                # create cell data
                if xbrl_tag != "Choose from drop-down -->":
                    cell = Cell(id = row["id"], 
                                xbrl_tag = xbrl_tag, 
                                row_name = str(row["nan"]), 
                                col_name = str(row["header"]),
                                value = row["value"],
                                context = context)
                    self._data.append(cell)

                # reassign the relevant section name if appropriate
                if cell.tr_class() in ["section_header", "subsection_header"]:
                    section = clean(cell.row_name())
                    # if the current section is a dimension, record it (ex. Governmental Activities)
                    if section in axis_dict: #and col_name not in DIMENSIONS["TypeOfGovernmentUnit"]:
                        if dims[-1].axis() == "acfr:TypeOfGovernmentUnitAxis":
                            dims.pop()
                        dims.append(Dimension(section))
                        # create new context with additional dimension
                        context = self.add_context(col_name, dims)

        # put data back in its original order
        self._data.sort()