"""
K. Wheelan 
Updated March 2024
"""

__all__ = ["axis_dict", "ALPHABET", "ROOT", "UPLOAD_FOLDER", 
           "SPREADSHEET_EXTENSIONS", "ALLOWED_EXTENSIONS", 
           "DIMENSIONS"]

# =============================================================
# Global variables
# =============================================================

global ALPHABET
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# =============================================================
# Constants
# =============================================================

# dependencies
import os

ROOT = os.getcwd()
UPLOAD_FOLDER = 'static/input_files/webapp_uploads' # set to your own path
SPREADSHEET_EXTENSIONS = ['xlsx', 'xls']
ALLOWED_EXTENSIONS = SPREADSHEET_EXTENSIONS + ['docx', 'doc']

# =============================================================
# Dictionaries for XBRL taxonomy
# =============================================================

# Axes with their Members by column name
DIMENSIONS = {"TypeOfGovernmentUnit" : ["governmental_activities",
                                        "business-type_activities",
                                        "total_primary_government",
                                        "component_units"],
            "FundIdentifier"        : [], # I think these are all typed, not explicit
            "TypeOfProgramRevenues" : ["charges_for_services",
                                           "operating_grants_and_contributions",
                                           "capital_grants_and_contributions"],
            "GovernmentalFunds"     : {"governmental_funds" : "GovernmentalFundsMember",
                                       "general_fund" : "GeneralFundMember"},
                                       "aggregate_nonmajor_fund" : "AggregateNonmajorFundMember",
                                       "major_funds_excluding_general_funds_member" : "MajorFundsExcludingGeneralFundsMember"}

# Dimension axis and member name by column name in Excel template
axis_dict = {"governmental_activities"  : ("acfr:TypeOfGovernmentUnitAxis", "GovernmentalActivities"),
             "business-type_activities" : ("acfr:TypeOfGovernmentUnitAxis", "BusinessTypeActivities"),
             "total_primary_government" : ("acfr:TypeOfGovernmentUnitAxis", "PrimaryGovernmentActivities"),
             "component_units"          : ("acfr:TypeOfGovernmentUnitAxis", "ComponentUnitDiscretelyPresented"),
             "charges_for_services"     : ("acfr:TypeOfProgramRevenuesAxis", "ProgramRevenuesFromChargesForServicesMember"),
             "operating_grants_and_contributions" : ("acfr:TypeOfProgramRevenuesAxis", "ProgramRevenuesFromOperatingGrantsAndContributions"),
             "capital_grants_and_contributions"   : ("acfr:TypeOfProgramRevenuesAxis", "ProgramRevenuesFromCapitalGrantsAndContributions")}
