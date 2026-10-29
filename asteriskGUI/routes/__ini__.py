

# Expose the sub-routers so main.py can import them directly
from .web import router as web_router
from .streamCall import router as streamCall_router
from .telephony import router as telephony_router
from .testAMICommand import router as testAMICommand_router
from .extensionSetting import router as extensionSetting_router
from .streamConfCall import router as streamConfCall_router
