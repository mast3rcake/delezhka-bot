from aiogram.fsm.state import State, StatesGroup


class AddExpenseState(StatesGroup):
    waiting_for_payer = State()
    waiting_for_amount = State()
    waiting_for_description = State()


class AddParticipantsState(StatesGroup):
    waiting_for_participants = State()
