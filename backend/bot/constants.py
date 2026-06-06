"""Umumiy konstantalar (yo'nalishlar, skill mapping)."""

from __future__ import annotations

# Yo'nalishlar ro'yxati (PRD bo'limi 8)
DIRECTIONS: list[dict[str, str]] = [
    {"id": "backend", "name": "Backend", "emoji": "⚙️"},
    {"id": "frontend", "name": "Frontend", "emoji": "🎨"},
    {"id": "devops", "name": "DevOps", "emoji": "🔧"},
    {"id": "algorithms", "name": "Algoritmlar", "emoji": "🧮"},
    {"id": "database", "name": "Ma'lumotlar bazasi", "emoji": "🗄️"},
    {"id": "security", "name": "Xavfsizlik", "emoji": "🔒"},
    {"id": "mobile", "name": "Mobile", "emoji": "📱"},
    {"id": "ml_ai", "name": "ML/AI", "emoji": "🤖"},
    {"id": "game_dev", "name": "Game Dev", "emoji": "🎮"},
    {"id": "c_lang", "name": "C/C++", "emoji": "💻"},
    {"id": "python", "name": "Python", "emoji": "🐍"},
    {"id": "javascript", "name": "JavaScript", "emoji": "📜"},
    {"id": "rust", "name": "Rust", "emoji": "🦀"},
    {"id": "docker_k8s", "name": "Docker/K8s", "emoji": "🐳"},
    {"id": "git", "name": "Git", "emoji": "📦"},
]

DIRECTION_IDS: set[str] = {d["id"] for d in DIRECTIONS}

# Yo'nalish id -> ko'rsatiladigan nom/emoji
DIRECTION_BY_ID: dict[str, dict[str, str]] = {d["id"]: d for d in DIRECTIONS}

# School 21 skill nomi -> PeerLearn yo'nalish id (yo'nalish taklifi uchun)
SKILL_TO_DIRECTION: dict[str, str] = {
    "Python": "python",
    "ML & AI": "ml_ai",
    "Algorithms": "algorithms",
    "C": "c_lang",
    "SQL": "database",
    "DB & Data": "database",
    "Linux": "devops",
    "Network & system administration": "devops",
    "Graphics": "game_dev",
    "OOP": "backend",
    "Shell/Bash": "devops",
    "Math": "algorithms",
}


def direction_label(direction_id: str) -> str:
    """Yo'nalish id'sidan emoji + nom qaytaradi (topilmasa id'ning o'zi)."""
    d = DIRECTION_BY_ID.get(direction_id)
    if not d:
        return direction_id
    return f"{d['emoji']} {d['name']}"


def suggest_directions_from_skills(skills: list[dict], limit: int = 5) -> list[str]:
    """Skill ballari asosida eng yuqori yo'nalishlarni taklif qiladi.

    skills: [{"name": str, "points": int}, ...]
    Qaytaradi: yo'nalish id'lari ro'yxati (eng yuqori balldan past tomon, limit'gacha).
    """
    direction_points: dict[str, int] = {}
    for skill in skills:
        name = skill.get("name", "")
        points = skill.get("points", 0) or 0
        direction_id = SKILL_TO_DIRECTION.get(name)
        if direction_id:
            direction_points[direction_id] = direction_points.get(direction_id, 0) + points
    ranked = sorted(direction_points.items(), key=lambda kv: kv[1], reverse=True)
    return [direction_id for direction_id, _ in ranked[:limit]]
