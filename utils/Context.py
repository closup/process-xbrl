
from utils.helper_functions import *
from datetime import datetime, timedelta # for date parsing
from constants import *


class Context:
    """ define xbrl context object """
    __slots__ = ["id", "date", "time_type", "place_id", "memberType",
                 "dimension_member", "axis", "period_start"]

    def __init__(self, context_name_map, statement, date, col_name):
        """
        Build out context for each entity: government-type activities, business-type, etc 
        """
        self.date = datetime.strptime(date, "%B %d, %Y")
        self.time_type = period_dict[statement] # instance or duration
        self.period_start = None
        # if duration, set the start of the period as the first day of the FY
        if self.time_type == "D":
            self.period_start = self.date - timedelta(days=364)
        self.place_id = "0613882" # TODO: replace with a lookup function from Census
        
        # id is the context name
        # TODO: replace this by replacing "print_nicely" with one of the dictionaries + removing references to contexts
        # self.id = context_name_map[col_name]
        self.id = self.time_type + self.date.strftime('%Y%m%d') + "_" + print_nicely(col_name)

        if(col_name in axis_dict[""]):
            self.memberType = "explicit"
            self.axis, self.dimension_member = axis_dict[col_name]
        else:
            self.axis = "acfr:FundIdentifierAxis"
            self.memberType = "typed"
            self.dimension_member = print_nicely(col_name)
        
    def __eq__(self, other):
        """ Equality check """
        return(self.id == other.id)

    def __hash__(self):
        return hash(self.id)
    
    def view_date(self, date):
        """ format date as needed """
        return date.strftime("%Y-%m-%d")
    
    def __repr__(self):
        return self.id
    