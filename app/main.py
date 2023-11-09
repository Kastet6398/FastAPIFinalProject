from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from app.web_pages import router_web_pages
from app.sockets import router_websocket
from app.api import router_api

app = FastAPI(
    title='BoneRecipes',
    description="I'm not a writer, sorry.",
    version='0.0.1',
    debug=True
)


app.include_router(router_web_pages.router)
app.include_router(router_websocket.router)
app.include_router(router_api.router)

app.mount("/app/static/", StaticFiles(directory='app/static'), name='static')
