from app.utils import *

class Dimension():
    """ Class to capture the axis, dimension type, and member """

    def __init__(self, col_name : str, type = None):
        if(col_name in axis_dict):
            self._member_type = "explicit"
            self._axis, self._domain, self._member_name = axis_dict[col_name]
        elif(type == "gov"):
            # custom gov funds
            self._member_type = "typed"
            self._axis, self._domain = "FundIdentifier", "FundIdentifier"
            self._member_name = get_col_no_spaces(col_name)
        elif(type == "prop"):
            # custom proprietary funds
            self._member_type = "typed"
            self._axis, self._domain = "TypeOfActivitiesProprietaryFunds", "ProprietaryFunds"
            self._member_name = get_col_no_spaces(col_name)
        elif(type == "custom"):
            # Custom line item
            self._member_type = "typed"
            self._axis, self._domain = "DisaggregationLineItem", ""
            self._member_name = col_name

    @property
    def axis(self):
        return f"acfr:{self._axis}Axis"
    
    @property
    def domain(self):
        return f"acfr:{self._domain}Domain"
    
    @property
    def member_name(self):
        return f"acfr:{self._member_name}Member"
    
    @property
    def member_type(self):
        return self._member_type
