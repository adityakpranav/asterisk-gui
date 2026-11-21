#config.py


import os

AMI_HOST = os.getenv("ASTERISK_AMI_HOST", "127.0.0.1")
AMI_PORT = int(os.getenv("ASTERISK_AMI_PORT", 5038))
AMI_USER = os.getenv("ASTERISK_AMI_USER", "exch_gui")
AMI_SECRET = os.getenv("ASTERISK_AMI_SECRET", "exch@63974")

AMI_TEMPLATE_FILE = "ami_templates.json"
#AMI_TEMPLATE_FILE = "ami_templates_V2.json"

USER_DATA = {
    "admin":{"pass":"admin@63974",
             "access":[1,2,3,4,5],
             "token":"authenticated_pbx_admin_token"
            },
    "maintainer":{"pass":"maintainer@62977",
                  "access":[1,2,3],
                  "token":"authenticated_pbx_main_token"
                },
    "operator":{"pass":"operator@123",
                  "access":[1],
                  "token":"authenticated_pbx_operator_token"
                }
}

TOKEN_USER = {
    "authenticated_pbx_admin_token":"admin",
    "authenticated_pbx_main_token":"maintainer",
    "authenticated_pbx_operator_token":"operator"
}

FILTER_URLS = ["/extensions-data"]


#SERVER_DIR ="/home/exch" #added to this script Dynamically
#SERVER_IP = '10.24.49.192'

LOG_FILE_PATH = {"logger":os.path.join(SERVER_DIR,"asteriskGUI","Logs/api.log"),
                 "cdr":"/var/log/asterisk/cdr-csv/Master.csv"}