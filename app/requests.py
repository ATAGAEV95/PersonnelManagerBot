from sqlalchemy import select, and_, or_
from app.models import async_session, Persons, Relationship, Marriage, Admins


async def search_persons(search_str: str):
    try:
        async with async_session() as session:
            search_str = search_str.strip()
            search_terms = search_str.split()
            query = select(Persons)
            conditions = []
            if len(search_terms) == 2:
                term1, term2 = search_terms
                conditions.extend([
                    and_(
                        Persons.first_name.ilike(f"%{term1}%"),
                        Persons.last_name.ilike(f"%{term2}%")
                    ),
                    and_(
                        Persons.first_name.ilike(f"%{term2}%"),
                        Persons.last_name.ilike(f"%{term1}%")
                    )
                ])
            else:
                term = search_str
                conditions.extend([
                    Persons.last_name.ilike(f"%{term}%"),
                    Persons.first_name.ilike(f"%{term}%")
                ])
            query = query.where(or_(*conditions))
            result = await session.execute(query)
            return result.scalars().all()
    except Exception as e:
        print(f"Ошибка поиска: {e}")
        return []


async def delete_person(person_id: int) -> (bool, str):
    try:
        async with async_session() as session:
            query = select(Persons).where(Persons.person_id == person_id)
            result = await session.execute(query)
            person = result.scalar_one_or_none()
            if person is None:
                return False, f"Персонаж с ID {person_id} не найден"
            await session.delete(person)
            await session.commit()
            return True, f"Персонаж с ID {person_id} удалён"
    except Exception as e:
        return False, f"Ошибка удаления персонажа: {e}"


async def delete_marriage(husband_id: int, wife_id: int) -> (bool, str):
    try:
        async with async_session() as session:
            query = select(Marriage).where(
                Marriage.husband_id == husband_id,
                Marriage.wife_id == wife_id
            )
            result = await session.execute(query)
            marriage = result.scalar_one_or_none()
            if marriage is None:
                return False, f"Связь муж-жена для мужа {husband_id} и жены {wife_id} не найдена"
            await session.delete(marriage)
            await session.commit()
            return True, f"Связь муж-жена для мужа (ID {husband_id}) и жены (ID {wife_id}) удалена"
    except Exception as e:
        return False, f"Ошибка удаления связи муж-жена: {e}"


async def delete_relationship(parent_id: int, child_id: int) -> (bool, str):
    try:
        async with async_session() as session:
            query = select(Relationship).where(
                Relationship.parent_id == parent_id,
                Relationship.child_id == child_id
            )
            result = await session.execute(query)
            relationship = result.scalar_one_or_none()
            if relationship is None:
                return False, f"Связь родитель-ребёнок для родителя {parent_id} и ребёнка {child_id} не найдена"
            await session.delete(relationship)
            await session.commit()
            return True, f"Связь родитель (ID {parent_id}) - ребёнок (ID {child_id}) удалена"
    except Exception as e:
        return False, f"Ошибка удаления связи родитель-ребёнок: {e}"


async def get_user_by_id(user_id: int):
    try:
        async with async_session() as session:
            query = select(Admins).where(Admins.user_id == user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    except Exception as e:
        print(f"Ошибка получения пользователя: {e}")
        return None


async def add_user(user_id: int, username: str):
    try:
        async with async_session() as session:
            user = Admins(user_id=user_id, username=username)
            session.add(user)
            await session.commit()
    except Exception as e:
        print(f"Ошибка добавления пользователя: {e}")