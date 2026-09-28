from rest_framework.exceptions import APIException

class TradeException(APIException):
    status_code = 400
    default_code = 'trade_error'

class NotEnoughMoney(TradeException):
    default_detail = "Недостаточно средств"

class NotEnoughQuantity(TradeException):
    default_detail = "Недостаточно инструментов"