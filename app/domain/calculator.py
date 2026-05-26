from decimal import Decimal


def calculate_result(
    participants: list[str],
    expenses: list[dict],
):
    paid = {
        participant: Decimal("0")
        for participant in participants
    }

    for expense in expenses:
        payer = expense["payer"]

        amount = Decimal(str(expense["amount"]))

        paid[payer] += amount

    total_amount = sum(
        paid.values(),
        Decimal("0"),
    )

    share = total_amount / Decimal(len(participants))

    balances = {}

    for participant in participants:
        balances[participant] = (
            paid[participant] - share
        )

    creditors = []
    debtors = []

    for participant, balance in balances.items():
        if balance > 0:
            creditors.append({
                "name": participant,
                "amount": balance,
            })

        elif balance < 0:
            debtors.append({
                "name": participant,
                "amount": abs(balance),
            })

    settlements = []

    creditor_index = 0
    debtor_index = 0

    while (
        creditor_index < len(creditors)
        and debtor_index < len(debtors)
    ):
        creditor = creditors[creditor_index]
        debtor = debtors[debtor_index]

        amount = min(
            creditor["amount"],
            debtor["amount"],
        )

        settlements.append({
            "from": debtor["name"],
            "to": creditor["name"],
            "amount": round(amount, 2),
        })

        creditor["amount"] -= amount
        debtor["amount"] -= amount

        if creditor["amount"] <= 0:
            creditor_index += 1

        if debtor["amount"] <= 0:
            debtor_index += 1

    return {
        "total_amount": round(total_amount, 2),
        "share": round(share, 2),
        "paid": paid,
        "settlements": settlements,
    }
