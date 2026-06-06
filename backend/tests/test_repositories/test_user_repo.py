"""UserRepository testlari."""

from __future__ import annotations

import pytest

from bot.repositories.user_repo import UserRepository


@pytest.mark.asyncio
async def test_create_new_user(db_session):
    repo = UserRepository(db_session)
    user = await repo.create_or_update(
        user_id=100,
        username="tg_user",
        school21_login="toyneden",
        nickname="Toyne",
        directions=["python", "ml_ai"],
    )
    await db_session.commit()

    assert user.id == 100
    assert user.coins == 5  # DEFAULT_COINS
    assert user.max_coins == 15
    assert user.directions == ["python", "ml_ai"]
    assert user.is_active is True


@pytest.mark.asyncio
async def test_get_by_id_and_login(db_session):
    repo = UserRepository(db_session)
    await repo.create_or_update(
        user_id=101, username=None, school21_login="alice", nickname="Alice"
    )
    await db_session.commit()

    by_id = await repo.get_by_id(101)
    by_login = await repo.get_by_login("alice")
    assert by_id is not None
    assert by_login is not None
    assert by_id.id == by_login.id == 101


@pytest.mark.asyncio
async def test_create_or_update_existing(db_session):
    repo = UserRepository(db_session)
    await repo.create_or_update(user_id=102, username="old", school21_login="bob", nickname="Bob")
    await db_session.commit()

    updated = await repo.create_or_update(
        user_id=102,
        username="new",
        school21_login="bob",
        nickname="Bobby",
        directions=["backend"],
    )
    await db_session.commit()

    assert updated.username == "new"
    assert updated.nickname == "Bobby"
    assert updated.directions == ["backend"]


@pytest.mark.asyncio
async def test_update_fields(db_session):
    repo = UserRepository(db_session)
    await repo.create_or_update(
        user_id=103, username=None, school21_login="carol", nickname="Carol"
    )
    await db_session.commit()

    await repo.update(103, xp=150, level=2, coins=8)
    await db_session.commit()

    user = await repo.get_by_id(103)
    assert user.xp == 150
    assert user.level == 2
    assert user.coins == 8


@pytest.mark.asyncio
async def test_set_language(db_session):
    repo = UserRepository(db_session)
    await repo.create_or_update(user_id=104, username=None, school21_login="dan", nickname="Dan")
    await db_session.commit()

    await repo.set_language(104, "ru")
    await db_session.commit()

    user = await repo.get_by_id(104)
    assert user.language == "ru"
