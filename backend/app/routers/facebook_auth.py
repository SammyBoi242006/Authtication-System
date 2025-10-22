from backend.app.routers.auth import *

FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
FACEBOOK_REDIRECT_URI = os.getenv('FACEBOOK_REDIRECT_URI')

if not all([FACEBOOK_APP_ID, FACEBOOK_APP_SECRET]):
    raise RuntimeError('Missing facebook app credentials')

FACEBOOK_AUTH_URL = "https://www.facebook.com/v24.0/dialog/oauth"
FACEBOOK_ACCESS_TOKEN_URL = 'https://graph.facebook.com/v24.0/oauth/access_token'
FACEBOOK_API_URL = 'https://graph.facebook.com/v24.0/me'


@app.get('/login/facebook', name='login_facebook')
async def f_login(request: Request):
    params = {
        'client_id': FACEBOOK_APP_ID,
        'redirect_uri': FACEBOOK_REDIRECT_URI,
        'scope': 'email,public_profile',
        'response_type': 'code',
    }
    url = f"{FACEBOOK_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)

@app.get('/auth/facebook/callback')
async def f_auth_callback(request: Request,code: str = None,error: str = None):
    if error:
        return HTMLResponse('''
                    <html>
                    <body>
                    <h1>You canceled the Login</h1>
                    <a href="/">Click here to go to login page</a>
                    </body>
                    </html>
                ''')
    if not code:
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
        'client_id': FACEBOOK_APP_ID,
        'client_secret': FACEBOOK_APP_SECRET,
        'redirect_uri': FACEBOOK_REDIRECT_URI,
    }


    async with httpx.AsyncClient() as client:
        token_response = await client.get(FACEBOOK_ACCESS_TOKEN_URL, params=data)
        token_data = token_response.json()

        if 'access_token' not in token_data:
            raise HTTPException(status_code=400,detail='Failed o retrieve access token')

        access_token = token_data['access_token']

        userinfo_response = await client.get(
            FACEBOOK_API_URL,
            params={
                'fields': 'id,name,email,picture',
                'access_token': access_token,
            })
        userinfo = userinfo_response.json()
        picture_url = userinfo['picture']['data']['url']
        print("ORIGINAL PICTURE URL")
        print(picture_url)
        query_params = {
            'id': userinfo['id'],
            'name': userinfo['name'],
            'email': userinfo['email'],
            'picture': picture_url
        }
        redirect_url = f"/facebook/profile?{urlencode(query_params)}"
        return RedirectResponse(redirect_url)

@app.get('/facebook/profile',response_class=HTMLResponse)
async def facebook_profile(request:Request):
    userinfo = request.query_params

    id = userinfo.get('id')
    name = userinfo.get('name')
    email = userinfo.get('email')
    picture = userinfo.get('picture','')
    print(picture)
    save_user(name=name, email=email, picture=picture, field='facebook')
    return templates.TemplateResponse(
        'user_profile.html',
        {
            'request': request,
            'name': name,
            'email': email,
            'picture': picture,
        }
    )
