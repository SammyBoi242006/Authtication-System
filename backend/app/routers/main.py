from github_auth import *
from fastapi import Form
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import bcrypt

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# from ..routers import auth, github_auth, facebook_auth
# app.include_router(auth.router)
# app.include_router(github_auth.router)
# app.include_router(facebook_auth.router)


@app.post('/login/web',name='login_web')
async def web_login(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        ):

    userinfo = {
        'name': name,
        'email': email,
        'password': password,
    }
    save_user(name=name, email=email, password=password, field='web')
    return templates.TemplateResponse(
        'user_profile.html',
        {
            'request': request,
            'name': name,
            'email': email,
            'picture': None,
        }
    )

@app.post('/signin/web',name='signin_web')
async def web_signin(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        ):
    valid,name,picture = check_user(email=email,password=password)
    if valid:
        return templates.TemplateResponse(
            'user_profile.html',
            {
                'request': request,
                'name': name,
                'email': email,
                'picture': picture,
            }
        )
    else:
        return HTMLResponse('''
            <h2>could not log you in</h2>
        ''')

if __name__ == "__main__":
    uvicorn.run("backend.app.routers.main:app",reload=True)

handler = Mangum(app)