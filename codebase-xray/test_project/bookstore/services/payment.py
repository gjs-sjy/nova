from utils.validation import validate_card


def charge_card(card, amount):
    validate_card(card)
    return gateway_request("charge", card, amount)


def refund(card, amount):
    return gateway_request("refund", card, amount)


def gateway_request(action, card, amount):
    return {"action": action, "last4": card[-4:], "amount": amount, "ok": True}
