import uvicorn
import fastapi
from src.routes import contacts,auth,users
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis


app = fastapi.FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts.router, prefix = '/api')
app.include_router(auth.router, prefix = '/api')
app.include_router(users.router, prefix='/api')

@app.on_event("startup")
async def startup():
    r = await redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',host = 'localhost', port = 8000 , reload = True
    )