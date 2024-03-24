from utils.helper_functions import *
from utils.constants import *

class Dimension():
    """ Class to capture the axis, dimension type, and member """

    def __init__(self, col_name : str):
        if(col_name in axis_dict):
            self._member_type = "explicit"
            self._axis, self._member_name = axis_dict[col_name]
        else:
            self._axis, self._member_type = "acfr:FundIdentifierAxis", "typed"
            self._member_name = get_col_no_spaces(col_name)

    def axis(self):
        return self._axis
    
    def member_name(self):
        return self._member_name
    
    def member_type(self):
        return self._member_type
