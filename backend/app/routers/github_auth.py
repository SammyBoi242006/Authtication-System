from facebook_auth import *

GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
GITHUB_REDIRECT_URI = os.getenv('GITHUB_REDIRECT_URI')

if not all([GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET]):
    raise RuntimeError('Missing github credentials')

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API_URL = "https://api.github.com/user"

@app.get('/login/github',name='login_github')
async def g_login(request: Request):
    params = {
        'client_id': GITHUB_CLIENT_ID,
        'redirect_uri': GITHUB_REDIRECT_URI,
        'scope': 'read:user user:email',
    }
    url = f"{GITHUB_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)


@app.get('/auth/github/callback')
async def f_auth_callback(request: Request,code: str=None,error: str=None):
    if error:
        raise HTTPException(status_code=400, detail=f"GitHub OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided")

    data = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code,
        'redirect_uri': GITHUB_REDIRECT_URI,
    }
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GITHUB_TOKEN_URL,
            data=data,
            headers={'Accept': 'application/json'}
        )
        if token_response.status_code !=200:
            raise HTTPException(status_code=400,detail="Failed to get access token")

        token_data = token_response.json()
        if 'access_token' not in token_data:
            raise HTTPException(status_code=400,detail="No access token provided in data")
        access_token = token_data['access_token']

        user_response = await client.get(
            GITHUB_USER_API_URL,
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
        )

        if user_response.status_code !=200:
            raise HTTPException(status_code=400,detail="Failed to get user info")
        user_data = user_response.json()

        email_response = await client.get(
            f"{GITHUB_USER_API_URL}/emails",
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
        )
        emails = email_response.json() if email_response.status_code !=200 else []
        primary_email = next((e['email'] for e in emails if e.get('primary')),None)

        query_params = {
            'id':user_data.get('id'),
            'login':user_data.get('login'),
            'name': user_data.get('name'),
            'email': primary_email or user_data.get('email'),
            'picture': user_data.get('avatar_url'),
        }

        redirect_url = f"/github/profile?{urlencode(query_params)}"
        return RedirectResponse(redirect_url)


@app.get('/github/profile',response_class=HTMLResponse)
async def github_profile(request: Request):
    userinfo = request.query_params
    id = userinfo.get('id')
    name = userinfo.get('name')
    email = userinfo.get('email') if None else "Your email is set private on github"
    picture = userinfo.get('picture', '')
    print(picture)
    save_user(name=str(name), email=str(email), picture=str(picture), field='github')
    return templates.TemplateResponse(
        'user_profile.html',
        {
            'request': request,
            'name': name,
            'email': email,
            'picture': picture,
        }
    )



if __name__ == '__main__':
    uvicorn.run('github_auth:app',reload=True)