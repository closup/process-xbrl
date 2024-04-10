from app.models.Table import Table
from app.models.Cell import Cell
from app.models.Context import Context
from app.models.Dimension import Dimension
from app.utils.helper_functions import *
from typing import *
from app.utils.constants import *

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
            
            # Grab all cells in the given column
            rows = self._df[self._df['header'] == col_name]
            # initialize section
            section = ""
            for _, row in rows.iterrows():

                # for each column, create corresponding context
                if col_name == "expenses":
                    # avoid assuming that this is a typed dim for FundIdentifierAxis
                    dims = []
                else:
                    dims = [Dimension(col_name)]   

                # if the current section is a dimension, record it unless the column contradicts it
                if section in axis_dict and col_name not in DIMENSIONS["TypeOfGovernmentUnit"]:
                    dims.append(Dimension(section))

                # create new context for the column and section
                context = self.add_context(col_name, dims)   

                # process xbrl tags according to the relevant column groups 
                # (see color coding on Excel sheet)
                xbrl_list = str(row["xbrl_element"]).strip().split(',')
                if len(xbrl_list) == 1 or col_name == "expenses":
                    # first tag in list from relevant cell in column A in the excel sheet
                    xbrl_tag = xbrl_list[0]
                elif col_name in DIMENSIONS["TypeOfProgramRevenues"]:
                    # second tag in list from relevant cell in column A (revenue)
                    xbrl_tag = xbrl_list[1]
                else:
                    # third tag in list from relevant cell in column A (net revenue/deficit)
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


        # put data back in its original order
        self._data.sort()