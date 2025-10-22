import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from urllib.parse import urlencode,quote,unquote
import httpx
from fastapi.templating import Jinja2Templates
from jose import jwt
import html
from dotenv import load_dotenv
from pathlib import Path
from fastapi.staticfiles import StaticFiles
import bcrypt, sys
from backend.app.models.users import save_user,check_user
app = FastAPI()
STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "public" / "src" / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent.parent / 'frontend' / 'public' / 'src' / 'templates'
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
# load .env
env_path = Path('../../../.env')
load_dotenv(env_path)

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URL = os.getenv('GOOGLE_REDIRECT_URL')

if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URL]):
    raise RuntimeError('Missing Google authentication credentials')

GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'

# Main root html display
@app.get('/', response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse('home_page.html',{
        'request': request,
    })


@app.get('/login/google', name='login_google')
def login():
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URL,  # Changed from redirect_url
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent',
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"  # Removed extra /
    return RedirectResponse(url)


@app.get('/auth/callback')
async def auth_callback(request: Request):
    code = request.query_params.get('code')
    if not code:
        #--------------Make HTML for user cancel Login page-----------#
        return HTMLResponse('''
            <html>
            <body>
            <h1>You canceled the Login</h1>
            <a href="/">Click here to go to login page</a>
            </body>
            </html>
        ''')

    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URL,  # Changed from redirect_url
        'grant_type': 'authorization_code',
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_URL, data=data)
        token_data = token_response.json()
        access_token = token_data.get('access_token')

        if not access_token:
            raise HTTPException(status_code=401, detail='Invalid access token')

        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        userinfo_response = await client.get(GOOGLE_USERINFO_URL, headers=headers)
        userinfo = userinfo_response.json()
        picture_url = userinfo['picture']
        query_params = {
            'id': userinfo['id'],
            'name': userinfo['name'],
            'email': userinfo['email'],
            'picture': picture_url
        }
        redirect_url = f"/profile?{urlencode(query_params)}"
        return RedirectResponse(redirect_url)



@app.get('/profile',response_class=HTMLResponse)
async def profile(request: Request):
    userinfo = request.query_params
    name = userinfo.get('name')
    email = userinfo.get('email')
    picture = userinfo.get('picture','')

    # user_data = {
    #     'name': name,
    #     'email': email,
    #     'field': 'Google',
    #     'picture': picture,
    # }
    save_user(name=str(name), email=str(email), picture=str(picture),field='google')
    return templates.TemplateResponse(
        'user_profile.html',
        {
            'request': request,
            'name': name,
            'email': email,
            'picture': picture,
        }
    )

@app.get('/signup', response_class=HTMLResponse,name='signup')
async def signup(request: Request):
    return templates.TemplateResponse(
        'sign_up.html',
        {
            'request': request,
        }
    )

