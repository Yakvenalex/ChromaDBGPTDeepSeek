from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.utils import get_optional_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def chat_page(
    request: Request,
    user_id: int = Depends(get_optional_current_user),
):
    if user_id:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return RedirectResponse(url="/login")


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    user_id: int = Depends(get_optional_current_user),
):
    if user_id:
        return RedirectResponse(url="/")
    else:
        return templates.TemplateResponse("login.html", {"request": request})
