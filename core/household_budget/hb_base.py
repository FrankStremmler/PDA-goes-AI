'''
This module contains base classes and functions for handling household budget data.
'''
import os
from dotenv import load_dotenv

import core.household_budget.hb_constants as hb_constants
import core.global_functions as global_functions
import providers.google_parts.drive_google as drive_google

load_dotenv()
