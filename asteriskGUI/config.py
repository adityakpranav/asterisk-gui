#config.py


import os

AMI_HOST = os.getenv("ASTERISK_AMI_HOST", "127.0.0.1")
AMI_PORT = int(os.getenv("ASTERISK_AMI_PORT", 5038))
AMI_USER = os.getenv("ASTERISK_AMI_USER", "exch_gui")
AMI_SECRET = os.getenv("ASTERISK_AMI_SECRET", "exch@63974")

AMI_OPR = "operator"
AMI_OPR_SECRET = "operator@123"

TOKENS = ["authenticated_pbx_manager_token","authenticated_pbx_operator_token"]

# SERVER_DIR ="" added to this script Dynamically
