from app.utils import *

class Dimension():
    """ Class to capture the axis, dimension type, and member """

    def __init__(self, col_name : str, type = None):
        self._member_name = get_col_no_spaces(col_name)  # Default value
        self._member_type = "typed"  # Default type
        self._axis = "DefaultAxis"
        self._domain = "DefaultDomain"

        if col_name in axis_dict:
            self._member_type = "explicit"
            self._axis, self._domain, self._member_name = axis_dict[col_name]
        elif type == "gov":
            # custom gov funds
            self._axis, self._domain = "FundIdentifier", "FundIdentifier"
        elif type == "prop":
            # custom proprietary funds
            self._axis, self._domain = "TypeOfActivitiesProprietaryFunds", "ProprietaryFunds"
        elif type == "custom":
            # Custom line item
            self._axis, self._domain = "DisaggregationLineItem", ""

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
