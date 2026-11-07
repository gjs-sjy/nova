from app.server import router
from services.order_service import OrderService

orders = OrderService()


@router.post("/orders")
def place_order_route(data):
    return orders.place(data["user_id"], data["book_ids"], data["card"])
