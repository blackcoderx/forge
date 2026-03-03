"""
Seed the database with test data for local development.
Usage: uv run python seed.py
"""
from datetime import datetime, timezone, timedelta

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.core.security import hash_password, encrypt_secret
from app.models.user import User
from app.models.hackathon import Hackathon
from app.models.team import Team


def seed():
    init_db()
    db = SessionLocal()

    try:
        # ── Admin ──────────────────────────────────────────────────────────────
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(
                username="admin",
                hashed_password=hash_password("admin123"),
                role="admin",
            ))
            print("Created admin / admin123")

        # ── Judges ─────────────────────────────────────────────────────────────
        for i in range(1, 3):
            uname = f"judge{i:02d}"
            if not db.query(User).filter(User.username == uname).first():
                db.add(User(
                    username=uname,
                    hashed_password=hash_password(f"judge{i}pass"),
                    role="judge",
                ))
                print(f"Created {uname} / judge{i}pass")

        db.flush()

        # ── Hackathon ──────────────────────────────────────────────────────────
        hackathon = db.query(Hackathon).filter(Hackathon.name == "Studentrepreneur AI Hackathon").first()
        if not hackathon:
            now = datetime.now(timezone.utc)
            hackathon = Hackathon(
                name="Studentrepreneur AI Hackathon",
                description="Build AI agents that solve real student and entrepreneur problems.",
                rules=(
                    "1. Teams of 1–4 participants.\n"
                    "2. All agents must be built using the provided Langflow environment.\n"
                    "3. Projects must be original work created during the hackathon.\n"
                    "4. Teams have 8 hours to build and submit.\n"
                    "5. Judges score on Innovation, Execution, Impact, and Presentation."
                ),
                theme="AI for Student Entrepreneurs",
                start_at=now - timedelta(hours=1),
                end_at=now + timedelta(hours=7),
                event_code="FORGE2025",
                langflow_url="http://localhost:7860",
                langflow_admin_username="admin",
                langflow_admin_password=encrypt_secret("langflow_admin_pass"),
            )
            db.add(hackathon)
            db.flush()
            print(f"Created hackathon: {hackathon.name} (event code: FORGE2025)")

        # ── Teams ──────────────────────────────────────────────────────────────
        teams_data = [
            ("Team Alpha", "team_alpha", "alpha123", "lf_alpha", "lf_alpha_pass"),
            ("Team Beta",  "team_beta",  "beta123",  "lf_beta",  "lf_beta_pass"),
            ("Team Gamma", "team_gamma", "gamma123", "lf_gamma", "lf_gamma_pass"),
        ]

        for team_name, username, password, lf_user, lf_pass in teams_data:
            if not db.query(User).filter(User.username == username).first():
                user = User(
                    username=username,
                    hashed_password=hash_password(password),
                    role="participant",
                )
                db.add(user)
                db.flush()

                team = Team(
                    name=team_name,
                    hackathon_id=hackathon.id,
                    user_id=user.id,
                    langflow_username=lf_user,
                    langflow_password=encrypt_secret(lf_pass),
                )
                db.add(team)
                print(f"Created {team_name}: portal={username}/{password} | langflow={lf_user}/{lf_pass}")

        db.commit()
        print("\nSeed complete.")
        print("\nTest accounts:")
        print("  Admin:       admin / admin123")
        print("  Judge:       judge01 / judge1pass")
        print("  Judge:       judge02 / judge2pass")
        print("  Participant: team_alpha / alpha123  (event code: FORGE2025)")
        print("  Participant: team_beta  / beta123   (event code: FORGE2025)")
        print("  Participant: team_gamma / gamma123  (event code: FORGE2025)")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
