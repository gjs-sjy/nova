from services.pricing import calculate_order_total
from services.payment import charge_card, refund
from services.notifications import send_receipt
from services.audit import record_event


class OrderService:
    def place(self, user_id, book_ids, card):
        total = calculate_order_total(book_ids)
        charge_card(card, total)
        send_receipt(user_id, total)
        record_event("order_placed", user_id)
        return {"total": total}

    def cancel(self, order):
        # Not wired up to any route yet.
        refund(order["card"], order["total"])
