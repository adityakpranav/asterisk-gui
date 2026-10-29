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
    

USER_DATA = config.USER_DATA
TOKEN_USER = config.TOKEN_USER

# Helper check dependency function to validate session status cookies
def get_current_user(request: Request):
    
    session_token = request.cookies.get("session_auth_token",None)
    print("session_token : ",session_token)
    
    # Redirect target boundary exception to cleanly force page shifts if intercept fails
    if not session_token or session_token not in TOKEN_USER:
        return None

    login_User = TOKEN_USER.get(session_token,None)

    return login_User

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

    username_exist = USER_DATA.get(username,None)
    print("username_exist : ",username_exist)
    if username_exist and username_exist.get("pass",None) == password:
        # if user Exist and password matched

        res_payload = {"status": "success", "message": "Console session verification achieved.","user":username_exist,"access":username_exist.get("access",[])}
        
        # Instantiate a secure HTTPOnly session cookie token inside the client web browser
        response.set_cookie(
            key="session_auth_token", 
            value=username_exist.get("token",None),
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
    
    data_context = {"title": "NER PBX Dashboard", "status": "Connected","user":current_user,"access":USER_DATA.get(current_user).get("access",[])}
    
    # 2. Render Main Page for 
    return templates.TemplateResponse(
        request=request, 
        name="base.html", 
        context=data_context
    )
