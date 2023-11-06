from utils.helper_functions import *
from datetime import datetime, timedelta # for date parsing

# look up period or instance by statement
period_dict = {"statement_of_net_position" : "I",
               "balance_sheet" : "I",
               "statement_of_revenues,_expenditures_and_changes_in_fund_balance" : "D",
               "statement_of_net_position" : "I",
               "statement_of_revenues,_expenses_and_changes_in_net_position" : "D",
               "statement_of_cash_flows" : "D"}

# Explicit members of axes plus their axis name
explicit_axis_members = {"governmental_activities" : "TypeOfGovernmentUnit",
                         "business-type_activities" : "TypeOfGovernmentUnit",
                         "component-units" : "TypeOfGovernmentUnit", 
                         "general_fund" : "GovernmentalFunds",
                         "total" : "GovernmentalFunds"}

# Axes with typed members
# ALL FundIdentifier
# typed_axis_members = {"Balance Sheet" : "FundIdentifier",
#                       "Statement of Revenues, Expenditures and Changes in Fund Balance" : "FundIdentifier",
#                       "Statement of Net Position" : }

class Context:
    """ define xbrl context object """
    __slots__ = ["id", "date", "time_type", "place_id", "memberType",
                 "dimension_member", "axis", "period_start"]

    def __init__(self, context_name_map, statement, date, col_name):
        self.id = context_name_map[col_name]
        self.date = datetime.strptime(date, "%B %d, %Y")
        self.time_type = period_dict[statement] # replace with lookup table
        self.period_start = None
        if self.time_type == "D":
            self.period_start = self.date - timedelta(days=364)
        self.place_id = "0613882" # replace with a lookup function from Census
        if(col_name in explicit_axis_members):
            self.axis = f"acfr:{explicit_axis_members[col_name]}Axis"
            self.memberType = "explicit"
            if col_name == "component_units":
                self.dimension_member = f'acfr:{"ComponentUnitDiscretelyPresented"}Member'
            self.dimension_member = f'acfr:{print_nicely(col_name).replace(" ", "")}Member'
        else:
            self.axis = "afcr:FundIdentifierAxis"
            self.memberType = "typed"
            self.dimension_member = print_nicely(col_name)
        
    def __eq__(self, other):
        """ Equality check """
        return(hash(self) == hash(other))

    def __hash__(self):
        return hash(self.id)
    
    def view_date(self, date):
        """ format date as needed """
        return date.strftime("%Y-%m-%d")
    