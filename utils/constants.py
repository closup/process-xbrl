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
            "GovernmentalFunds"     : ["total", "general_fund"] }

# Dimension axis, domain, and member name by column name in Excel template
axis_dict = {"governmental_activities"  : ("TypeOfGovernmentUnit", "ConsolidatedActivities", "GovernmentalActivities"),
             "business-type_activities" : ("TypeOfGovernmentUnit", "ConsolidatedActivities", "BusinessTypeActivities"),
             "total_primary_government" : ("TypeOfGovernmentUnit", "ConsolidatedActivities", "PrimaryGovernmentActivities"),
             "component_units"          : ("TypeOfGovernmentUnit", "ConsolidatedActivities", "ComponentUnitDiscretelyPresented"),
             "charges_for_services"     : ("TypeOfProgramRevenues", "TypeOfProgramRevenues", "ProgramRevenuesFromChargesForServices"),
             "operating_grants_and_contributions" : ("TypeOfProgramRevenues", "TypeOfProgramRevenues", "ProgramRevenuesFromOperatingGrantsAndContributions"),
             "capital_grants_and_contributions"   : ("TypeOfProgramRevenues", "TypeOfProgramRevenues", "ProgramRevenuesFromCapitalGrantsAndContributions"),
            # figure out these domains
             "general_fund"             : ("GovernmentalFunds", None, "GeneralFund"),
             "total_governmental_funds" : ("GovernmentalFunds", None, "GovernmentalFunds")}
