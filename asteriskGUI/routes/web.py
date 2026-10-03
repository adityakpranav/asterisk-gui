# routes/web.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from fastapi import Response, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse

import config
from panoramisk import Manager


router = APIRouter()
templates = Jinja2Templates(directory="templates")
    
    
'''
@router.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """
    Serves the main real-time dashboard frontend.
    Passes initial rendering parameters down to Jinja2 context templates.
    """
    return templates.TemplateResponse(
        request=request, 
        name="base.html", 
        context={"title": "Asterisk Dashboard", "status": "Connected"}
    )
'''

ADMIN_USER = config.AMI_USER
ADMIN_PASS = config.AMI_SECRET

OPERATOR_USER = config.AMI_OPR
OPERATOR_PASS = config.AMI_OPR_SECRET

VALID_TOKENS = config.TOKENS

# Helper check dependency function to validate session status cookies
def get_current_user(request: Request):
    
    print("request.cookies : ",request.cookies)
    session_token = request.cookies.get("session_auth_token",None)
    print("session_token : ",session_token)
    
    # Redirect target boundary exception to cleanly force page shifts if intercept fails
    if not session_token or session_token not in VALID_TOKENS:
        return None

    if session_token == VALID_TOKENS[0]:
        return ADMIN_USER

    return OPERATOR_USER

# Render Login view
@router.get("/login", response_class=HTMLResponse)
async def render_login_portal(request: Request):
    # If user is already authenticated, jump past the login view straight to console dashboard
    try:
        if get_current_user(request):
            return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        print("Exception occured in login",str(e))
    #return templates.TemplateResponse("login.html", {"request": request})
    return templates.TemplateResponse(
            request=request, 
            name="login.html", 
            context={"title": "Login to PBX"}
        )

# Check Credentials
@router.post("/login")
async def execute_login_authentication(
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    if username == ADMIN_USER and password == ADMIN_PASS:
        # Create redirect response payload
        res_payload = {"status": "success", "message": "Console session verification achieved.","user":"0"}
        
        # Instantiate a secure HTTPOnly session cookie token inside the client web browser
        response.set_cookie(
            key="session_auth_token", 
            value=VALID_TOKENS[0],
            httponly=True,       # Prevents JavaScript XSS attack vectors from reading session state data
            max_age=28800,       # Automatic session expiration window set to 8 Hours
            samesite="lax"
        )
        return res_payload
    
    elif username == OPERATOR_USER and password == OPERATOR_PASS:
        # Create redirect response payload
        res_payload = {"status": "success", "message": "Console session verification achieved.","user":"1"}
        
        # Instantiate a secure HTTPOnly session cookie token inside the client web browser
        response.set_cookie(
            key="session_auth_token", 
            value=VALID_TOKENS[1],
            httponly=True,       # Prevents JavaScript XSS attack vectors from reading session state data
            max_age=28800,       # Automatic session expiration window set to 8 Hours
            samesite="lax"
        )
        return res_payload
        
    # Throw structured error handling to form capture
    raise HTTPException(status_code=401, detail="Invalid administrative connection credentials.")


@router.get("/logout")
async def execute_session_logout():
    # Flush the browser session cookie token entirely and force clear re-route back to login page
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_auth_token")
    return response


@router.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    
    # 1. Fire Session Token Intercept Authentication Check
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    user = current_user == OPERATOR_USER
    # 2. Render Main Page for 
    return templates.TemplateResponse(
        request=request, 
        name="base.html", 
        context={"title": "Asterisk Dashboard", "status": "Connected","access":user}
    )
