import pandas as pd
from app.models import NetPosition, StatementofActivities, Table, WordDoc
from typing import *
from app.utils.helper_functions import *

class Acfr:
    """ 
    Class to represent an entire acfr 
    sheets are Excel sheets in the file, contexts are ixbrl contexts
    """

    def __init__(self, file_list : List[Any]):
        self._pages, self._tables = self.handle_multiple_docs(file_list)
        self.contexts = self.get_contexts()

    def handle_multiple_docs(self, file_list) -> Tuple[List[Any], List[Table]]:
        """ TODO """
        pages = []
        tables = []
        for file in file_list:
            if is_spreadsheet(file.filename):
                tables = self.read_excel(file)
                pages += tables
            else:
                # is word doc
                pages.append(WordDoc(file))

        return pages, tables

    def read_excel(self, input_file : str) -> List[Table]:
        """ Create a Sheet object for each tab in excel """
        sheets = []
        input_xl = pd.ExcelFile(input_file)
        for sheet_name in input_xl.sheet_names:
            if sheet_name in ["Statement of Net Position", "Prop Funds - Net Position", "GovFund Stmt of Rev Exp and Chg"]:
                sheets.append(NetPosition(input_file, sheet_name))
            elif sheet_name == "Statement of Activities":
                sheets.append(StatementofActivities(input_file, sheet_name))
            # TODO: add support for other tables here
        return sheets
    
    def get_contexts(self):
        """ create a list of all unique contexts across every sheet """
        unique_contexts = set()

        for table in self._tables:
            for context in table.contexts():
                if context.dims() is not None:
                    unique_contexts.add(context)
        return unique_contexts

    @property
    def pages(self):
        return self._pages
    
    @staticmethod
    def is_table(page) -> bool:
        return isinstance(page, Table)

    