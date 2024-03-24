import pandas as pd
from utils.Sheet import Sheet
from utils.NetPosition import NetPosition
from utils.StatementOfActivities import StatementofActivities
from typing import *

class Acfr:
    """ 
    Class to represent an entire acfr 
    sheets are Excel sheets in the file, contexts are ixbrl contexts
    """

    def __init__(self, input_file : str):
        self._sheets = self.read_excel(input_file)
        self.contexts = self.get_contexts()

    def read_excel(self, input_file : str) -> List[Sheet]:
        """ Create a Sheet object for each tab in excel """
        sheets = []
        input_xl = pd.ExcelFile(input_file)
        for sheet_name in input_xl.sheet_names:
            if sheet_name == "Statement of Net Position":
                sheets.append(NetPosition(input_file, sheet_name))
            elif sheet_name == "Statement of Activities":
                sheets.append(StatementofActivities(input_file, sheet_name))
            # elif not(sheet_name in ["Label Dropdowns", "Master Info", "Statement of activities labels"]):
            #     sheets.append(Sheet(input_file, sheet_name))
        return sheets
    
    def get_contexts(self):
        """ create a list of all unique contexts across every sheet """
        nested_contexts = [sheet.contexts() for sheet in self._sheets]
        return set(context for context_list in nested_contexts for context in context_list)

    def sheets(self):
        return self._sheets
