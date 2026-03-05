from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.init_db import init_db
from app.routers import auth, hackathons, teams, scores, admin, instances

init_db()

app = FastAPI(
    title="Forge API",
    description="Backend for the Forge hackathon platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(hackathons.router)
app.include_router(teams.router)
app.include_router(scores.router)
app.include_router(admin.router)
app.include_router(instances.router)


@app.get("/health")
def health():
    return {"status": "ok"}
