from sqlalchemy import select, and_, or_
from app.models import async_session
from app.models import Persons


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