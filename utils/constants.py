"""
K. Wheelan 
Updated March 2024
"""

__all__ = ["period_dict", "axis_dict"]

# =============================================================
# Global variables
# =============================================================

global ALPHABET
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# =============================================================
# Dictionaries for XBRL taxonomy
# =============================================================

# XBRL period type (instance or duration) by financial table
period_dict = {"statement_of_net_position"  : "I",
               "balance_sheet"              : "I",
               "statement_of_activites"     : "D",
               "statement_of_revenues,_expenditures_and_changes_in_fund_balance" : "D",
               "statement_of_revenues,_expenses_and_changes_in_net_position" : "D",
               "statement_of_cash_flows"    : "D"}

# Axes with their Members by column name
axis_dict = {"TypeOfGovernmentUnit" : {"governmental_activities" : "GovernmentalActivitiesMember",
                                       "business-type_activities" : "BusinessTypeActivitiesMember",
                                       "total_primary_government" : "PrimaryGovernmentActivitiesMember",
                                       "component_units" : "ComponentUnitDiscretelyPresentedMember"},
            "FundIdentifier"        : {}, # I think these are all typed, not explicit
            "GovernmentalFunds"     : {"governmental_funds" : "GovernmentalFundsMember",
                                       "general_fund" : "GeneralFundMember"},
                                       "aggregate_nonmajor_fund" : "AggregateNonmajorFundMember",
                                       "major_funds_excluding_general_funds_member" : "MajorFundsExcludingGeneralFundsMember"}

# Dimension axis and member name by column name in Excel template
axis_dict = {"governmental_activities"  : ("acfr:TypeOfGovernmentUnitAxis", "GovernmentalActivitiesMember"),
             "business-type_activities" : ("acfr:TypeOfGovernmentUnitAxis", "BusinessTypeActivitiesMember"),
             "total_primary_government" : ("acfr:TypeOfGovernmentUnitAxis", "PrimaryGovernmentActivitiesMember"),
             "component_units"          : ("acfr:TypeOfGovernmentUnitAxis", "ComponentUnitDiscretelyPresentedMember"),
             "charges_for_services"     : ("acfr:TypeOfProgramRevenuesAxis", "ProgramRevenuesFromChargesForServicesMember"),
             "operating_grants_and_contributions" : ("acfr:TypeOfProgramRevenuesAxis", "ProgramRevenuesFromOperatingGrantsAndContributionsMember"),
             "capital_grants_and_contributions"   : ("acfr:TypeOfProgramRevenuesAxis", "ProgramRevenuesFromCapitalGrantsAndContributionsMember")}
