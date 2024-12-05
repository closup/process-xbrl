"""
K. Wheelan 
Updated March 2024
"""

__all__ = ["axis_dict", "ALPHABET", "ROOT", "UPLOAD_FOLDER", 
           "SPREADSHEET_EXTENSIONS", "ALLOWED_EXTENSIONS", 
           "DIMENSIONS", "EXCLUDED_HEADERS"]

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
axis_dict = {"governmental_activities"  : ("TypeOfGovernmentUnit", None, "GovernmentalActivities"),
             "business-type_activities" : ("TypeOfGovernmentUnit", None, "BusinessTypeActivities"),
             "total_primary_government" : ("TypeOfGovernmentUnit", None, "PrimaryGovernmentActivities"),
             "component_units"          : ("TypeOfGovernmentUnit", None, "ComponentUnitDiscretelyPresented"),
             "charges_for_services"     : ("TypeOfProgramRevenues", None, "ProgramRevenuesFromChargesForServices"),
             "operating_grants_and_contributions" : ("TypeOfProgramRevenues", None, "ProgramRevenuesFromOperatingGrantsAndContributions"),
             "capital_grants_and_contributions"   : ("TypeOfProgramRevenues", None, "ProgramRevenuesFromCapitalGrantsAndContributions"),
            # gov funds
             "general_fund"             : ("GovernmentalFunds", None, "GeneralFund"),
             "total_governmental_funds" : ("GovernmentalFunds", None, "GovernmentalFunds"),
             # Prop funds
             "total_enterprise_funds" : ("TypeOfActivitiesProprietaryFunds", "ProprietaryFunds", "BusinessTypeActivitiesEnterpriseFunds"),
             "internal_service_funds" : ("TypeOfActivitiesProprietaryFunds", "ProprietaryFunds", "InternalServiceFunds")}

# =============================================================
# Mammoth style conversions from Word
# =============================================================

custom_style_map = """
p[style-name='title'] => h1.title
p[style-name='header'] => h2.header
p[style-name='header2'] => h3.header2
"""

# OPEB is for cell.py
EXCLUDED_HEADERS = ["OPEB"]  # Headers that shouldn't be treated as section headers

