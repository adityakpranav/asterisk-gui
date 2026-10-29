#config.py


import os

AMI_HOST = os.getenv("ASTERISK_AMI_HOST", "127.0.0.1")
AMI_PORT = int(os.getenv("ASTERISK_AMI_PORT", 5038))
AMI_USER = os.getenv("ASTERISK_AMI_USER", "exch_gui")
AMI_SECRET = os.getenv("ASTERISK_AMI_SECRET", "exch@63974")

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


AMI_OPR = "operator"
AMI_OPR_SECRET = "operator@123"
AMI_OPR_ACCESS = [2]

AMI_MAIN = "maintainer"
AMI_MAIN_SECRET = "maintainer@62977"
AMI_OPR_ACCESS = [1,2,3]

TOKENS = ["authenticated_pbx_manager_token","authenticated_pbx_main_token","authenticated_pbx_operator_token"]

# SERVER_DIR ="" added to this script Dynamically
