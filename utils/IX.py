
import utils.helper_functions
from utils.constants import *
import re

class IX:
    """ object for an individual cell (ix) """
    def __init__(self, name, xbrl_name, id, value, index, header, context_name_map):
        """ initialization function for the class """
        self.name = name # original row name from the spreadsheet
        self.xbrl_name = xbrl_name # xbrl element (row name), ex. acfr:FundBalance
        self.id = id # id for the tab and cell, ex. StatementofNetPosition_D5
        self.value = utils.helper_functions.format_value(value)
        self.context = context_name_map[index][header] # associated context
        self.sign = '' # set sign to nothing unless value is negative
        if value == 0:
            self.format = 'ixt:fixed-zero' 
        else:
            self.format = 'ixt:num-dot-decimal' # default value format
            if not (type(self.value) is str) and self.value < 0:
                self.sign = 'sign = "-"'
        # HARDCODING header_cols for now
        n_header_lines = 2
        self.row_start = id[id.find('_') + 1] == ALPHABET[n_header_lines]

    def show_value(self):
        if self.value == "":
            return ""
        ret = '{:,}'.format(self.value)
        if ret == "0":
            ret = "-"
        # HARDCODING
        row_start = 8
        # Add $ if first row
        if int(self.id[self.id.find('_') + 2:]) == row_start:
            ret = "$ " + ret
        return ret