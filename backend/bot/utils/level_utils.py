"""XP va level hisoblash yordamchilari."""

from __future__ import annotations

# Level -> shu levelga kirish uchun minimal XP
XP_TABLE: dict[int, int] = {
    1: 0,
    2: 100,
    3: 250,
    4: 500,
    5: 1000,
    6: 2000,
    7: 5000,
}

LEVEL_NAMES: dict[int, str] = {
    1: "Newbie 🌱",
    2: "Beginner 📖",
    3: "Learner 🎓",
    4: "Practitioner ⚡",
    5: "Expert 🌟",
    6: "Master 👑",
    7: "Legend 🏆",
}

MAX_LEVEL = max(XP_TABLE)


def calculate_level(xp: int) -> int:
    """XP qiymatidan levelni hisoblaydi (monoton: XP ortsa, level kamaymaydi)."""
    level = 1
    for lvl, required in sorted(XP_TABLE.items()):
        if xp >= required:
            level = lvl
        else:
            break
    return level


def get_level_info(xp: int) -> dict:
    """Joriy level, nom, keyingi levelgacha progress va kerakli XP.

    Qaytaradi: {level, name, xp, next_level_xp, xp_needed, progress}
    """
    level = calculate_level(xp)
    name = LEVEL_NAMES.get(level, f"Level {level}")

    if level >= MAX_LEVEL:
        return {
            "level": level,
            "name": name,
            "xp": xp,
            "next_level_xp": None,
            "xp_needed": 0,
            "progress": 100,
        }

    current_threshold = XP_TABLE[level]
    next_threshold = XP_TABLE[level + 1]
    span = next_threshold - current_threshold
    gained = xp - current_threshold
    xp_needed = next_threshold - xp
    progress = round((gained / span) * 100) if span > 0 else 0
    progress = max(0, min(100, progress))

    return {
        "level": level,
        "name": name,
        "xp": xp,
        "next_level_xp": next_threshold,
        "xp_needed": max(0, xp_needed),
        "progress": progress,
    }
