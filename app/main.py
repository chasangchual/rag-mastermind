from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from app.routers import home_router, chat_router, documents_router
from app.repository.repository_factory import RepositoryFactory
from app.utils.session_util import SessionUtils, SESSION_ID_NAME
import os 

app = FastAPI()
container = RepositoryFactory()
container.wire(modules=[documents_router])
app.container = container

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.middleware("http")
async def inject_session_cookie(request: Request, call_next):
    # Why: Ensure every visitor gets a stable session id
    session_id = request.cookies.get(SESSION_ID_NAME)
    new_session = False
    if not session_id:
        session_id = SessionUtils.get_or_create_session_id(None)
        new_session = True

    # Executes your Route (e.g., /ping) & generates Response
    response = await call_next(request)

    if new_session:
        SessionUtils.set_session_cookie(response, session_id)
    return response

@app.get("/ping")
def pong():
    return "pong"

@app.get("/", response_class=RedirectResponse)
async def redirect_to_app():
    return "/app/"

app.include_router(home_router.home_router)
app.include_router(chat_router.chat_router)
app.include_router(documents_router.documents_router)
