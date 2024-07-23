# Third-Party
import asyncio
from sqlalchemy import select, and_

# Python
from datetime import datetime, timezone

# Local
from src.settings.base import celery, session, logger
from src.apps.models.reserv import BookReservation


@celery.task(name="reset-reservations")
def main():
    asyncio.run(check_db())


async def check_db():
    now = datetime.now(tz=timezone.utc)
    query = select(BookReservation).where(and_(
        BookReservation.end_date <= now.date(),
        BookReservation.is_returned == False
    ))
    async with session() as conn:
        result = await conn.execute(query)
        reservations = result.scalars().all()
        logger.info(msg=f"Found {len(reservations)} reservations!")
        
        for reservation in reservations:
            reservation.is_returned = True
            await conn.add(reservation)
            logger.info(msg=f"Reservation {reservation.id} is finished!")
        
        await conn.commit()
        
    return None
