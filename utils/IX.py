
import utils.helper_functions
from utils.constants import *
from utils.Context import Context

class IX:
    """ object for an individual cell (ix) """

    def __init__(self, row, context_map):
        """ initialization function for the class """
        self.name = row["nan"] # original row name from the spreadsheet
        self.xbrl_name = row["xbrl_element"] # xbrl element (row name), ex. acfr:FundBalance
        self.id = row["id"] # id for the tab and cell, ex. StatementofNetPosition_D5
        self.value = utils.helper_functions.format_value(row["value"])
        self.col_name = row["header"]
        self.context_id = context_map[self.col_name]
        self.sign = '' # set sign to nothing unless value is negative
        if self.value == 0:
            self.format = 'ixt:fixed-zero' 
        else:
            self.format = 'ixt:num-dot-decimal' # default value format
            if not (type(self.value) is str) and self.value < 0:
                self.sign = 'sign = "-"'
        # HARDCODING header_cols for now
        n_left_cols = 2
        self.row_start = self.id[self.id.find('_') + 1] == ALPHABET[n_left_cols]

    def show_value(self):
        """
        Format the value as it should appear in the html table
        (ie. add a $ if the first row; add commas, etc)
        """
        if self.value == "":
            return ""
        ret = '{:,}'.format(self.value)
        if ret == "0":
            ret = "-"
        # HARDCODING
        # first valid index + n_header_rows -> code here
        row_start = 8
        # Add $ if first row
        if int(self.id[self.id.find('_') + 2:]) == row_start:
            ret = "$ " + ret
        return ret