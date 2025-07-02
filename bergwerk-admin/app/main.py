from auth.auth import *
from models.models import *
from middleware.middleware import RootPathMiddleware
import requests
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from redis_config import get_all_config, update_config
from fastapi import Depends, FastAPI, Request, Form, UploadFile, File, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
    
app = FastAPI()
app.add_middleware(RootPathMiddleware)
templates = Jinja2Templates(directory="templates")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
@limiter.limit("10/hour;50/day")
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    form_data = OAuth2PasswordRequestForm(
        username=username,
        password=password,
        scope="",
        client_id=None,
        client_secret=None,
    )
    try:
        token = await login_for_access_token(request, form_data)

        response = RedirectResponse(url=request.scope.get("root_path", "") + "/", status_code=302)
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,         
            max_age=1800,          
            path="/",
            secure=False,          
            samesite="lax",
        )
        return response

    except HTTPException as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": e.detail})



@app.post("/token")
@limiter.limit("10/hour;50/day")
async def login_for_access_token(request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/admin/login")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except InvalidTokenError:
        return RedirectResponse("/admin/login")

    config = get_all_config()
    return templates.TemplateResponse("index.html", {"request": request, "config": config})


@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/admin/login")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except InvalidTokenError:
        return RedirectResponse("/admin/login")
    
    content = await file.read()
    files = {'file': (file.filename, content, 'multipart/form-data')}
    response = requests.post("http://api/admin/import/", files=files)
    return RedirectResponse(request.scope.get("root_path") + "/", status_code=302)

@app.get("/trigger/build")
async def build_intent_classifier(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/admin/login")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except InvalidTokenError:
        return RedirectResponse("/login")
    
    response = requests.get("http://api/admin/build_intent_classifier/")
    return RedirectResponse(request.scope.get("root_path") + "/", status_code=302)

@app.get("/trigger/export")
async def trigger_export(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/admin/login")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except InvalidTokenError:
        return RedirectResponse("/login")
    
    response = requests.get("http://api/admin/export/")
    with open("export.json", "wb") as f:
        f.write(response.content)
    return FileResponse("export.json", filename="export.json", media_type='application/json')

@app.get("/trigger/generate")
async def trigger_generate(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/admin/login")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except InvalidTokenError:
        return RedirectResponse("/admin/login")

    response = requests.get("http://api/llm/llm_training_data/")
    return RedirectResponse(request.scope.get("root_path") + "/", status_code=302)


@app.post("/config/update")
async def config_update(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/admin/login")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except InvalidTokenError:
        return RedirectResponse("/admin/login")

    form = await request.form()
    update_config(dict(form))
    return RedirectResponse(request.scope.get("root_path") + "/", status_code=302)

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
