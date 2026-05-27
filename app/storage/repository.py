from decimal import Decimal

from app.storage.database import get_connection


class TripRepository:
    def create_trip(self, chat_id: int) -> None:
        with get_connection() as db:
            db.execute(
                """
                DELETE FROM participants
                WHERE chat_id = ?
                """,
                (chat_id,),
            )

            db.execute(
                """
                DELETE FROM expenses
                WHERE chat_id = ?
                """,
                (chat_id,),
            )

            db.commit()

    def clear_trip(self, chat_id: int) -> None:
        self.create_trip(chat_id)

    def add_participants(
        self,
        chat_id: int,
        participants: list[str],
    ) -> None:
        with get_connection() as db:
            db.execute(
                """
                DELETE FROM participants
                WHERE chat_id = ?
                """,
                (chat_id,),
            )

            for participant in participants:
                db.execute(
                    """
                    INSERT INTO participants (
                        chat_id,
                        name
                    )
                    VALUES (?, ?)
                    """,
                    (
                        chat_id,
                        participant,
                    ),
                )

            db.commit()

    def get_participants(
        self,
        chat_id: int,
    ) -> list[str]:
        with get_connection() as db:
            rows = db.execute(
                """
                SELECT name
                FROM participants
                WHERE chat_id = ?
                """,
                (chat_id,),
            ).fetchall()

        return [row[0] for row in rows]

    def add_expense(
        self,
        chat_id: int,
        payer: str,
        amount: Decimal,
        description: str,
    ) -> None:
        with get_connection() as db:
            db.execute(
                """
                INSERT INTO expenses (
                    chat_id,
                    payer,
                    amount,
                    description
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    chat_id,
                    payer,
                    float(amount),
                    description,
                ),
            )

            db.commit()

    def get_expenses(
        self,
        chat_id: int,
    ) -> list[dict]:
        with get_connection() as db:
            rows = db.execute(
                """
                SELECT
                    id,
                    payer,
                    amount,
                    description
                FROM expenses
                WHERE chat_id = ?
                ORDER BY id
                """,
                (chat_id,),
            ).fetchall()

        return [
            {
                "id": row[0],
                "payer": row[1],
                "amount": row[2],
                "description": row[3],
            }
            for row in rows
        ]

    def delete_expense(
        self,
        chat_id: int,
        expense_id: int,
    ) -> None:
        with get_connection() as db:
            db.execute(
                """
                DELETE FROM expenses
                WHERE chat_id = ?
                AND id = ?
                """,
                (
                    chat_id,
                    expense_id,
                ),
            )

            db.commit()
