from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, data, reports, users
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="数据统计报表系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

@app.get("/")
def read_root():
    return {"message": "数据统计报表系统 API"}
