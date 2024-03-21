
from utils.helper_functions import *
from utils.constants import *

class Cell:
    """ Class for an individual cell (ix) """

    def __init__(self, row, time_id):
        """ initialization function for the class """
        self.name = row["nan"] # original row name from the spreadsheet
        if str(self.name) == "nan":
            self.name = ""
        self.xbrl_name = str(row["xbrl_element"]).strip() # xbrl element (row name), ex. acfr:FundBalance
        self.id = row["id"] # id for the tab and cell, ex. StatementofNetPosition_D5
        self.value = format_value(row["value"]) # dollar value in cell
        self.col_name = row["header"]
        # context_ref definition
        self.context_id = time_id + "_" + get_col_no_spaces(self.col_name)
        self.sign = '' # set sign to nothing unless value is negative
        if self.value == 0:
            self.format = 'ixt:fixed-zero' 
        else:
            self.format = 'ixt:num-dot-decimal' # default value format
            if not (type(self.value) is str) and self.value < 0:
                self.sign = "negative"
        # hard coded to expect 2 non-taggable columns to the left (based on template)
        n_left_cols = 2
        self.col = self.id[self.id.find('_') + 1]
        self.row = self.id[self.id.find('_') + 2]
        self.row_start = self.col == ALPHABET[n_left_cols]
        self.first_row = False

    def set_first_row(self):
        self.first_row = True

    def show_value(self):
        """
        Format the value as it should appear in the html table
        (ie. add a $ if the first row; add commas, etc)
        """
        if self.value == "":
            return ""
        ret = '{:,}'.format(abs(self.value))
        if ret == "0":
            ret = "-"
        return ret
    
    def prefix(self):
        """
        Add dollar sign and/or negative sign as relevant
        """
        ret = ""
        if self.value < 0:
            ret = "-" + ret
        if self.first_row:
            ret = "$ " + ret
        return ret
    
    def tr_class(self):
        """
        Define row type to determine formatting
        """
        if self.name == "":
            return "empty_row"
        if self.name.isupper():
            return "section_header"
        if self.name[-1] == ":":
            return "subsection_header"
        if "total" in self.name.lower():
            return "total"
        return "row" 
    
    def td_class(self):
        """ Return CSS class for individual table cell """
        if "total" in self.name.lower():
            return "data_total"
        return self.tr_class()
    
    def __repr__(self):
        return self.show_value()