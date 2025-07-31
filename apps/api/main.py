from fastapi import FastAPI
from fastapi.security import HTTPBearer
from routers.todos import router as todo_router
from routers.users import router as user_router

app = FastAPI()

app.include_router(todo_router)
app.include_router(user_router)


security = HTTPBearer()
