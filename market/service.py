from django.utils import timezone

from market.exceptions import NotEnoughMoney, NotEnoughQuantity
from market.models import Position, Trade


def execute_trade(trade):
    if(trade.execution_type == Trade.Status.pending):
        return trade
    
    portfolio = trade.portfolio
    instrument = trade.instrument
    quantity = trade.quantity
    price = instrument.current_price
    total_cost = quantity * price
    trade.created_at = timezone.now()
    if(trade.order_type == Trade.OrderType.buy):
        if(portfolio.balance < total_cost):
            raise NotEnoughMoney("Недостаточно средств для покупки")
        portfolio.balance -= total_cost
        update_position_on_buy(portfolio, instrument, quantity, price)
    else:
        position = Position.objects.filter(portfolio=portfolio, instrument=instrument).first()
        if(position is not None or position.quantity < quantity):
            raise NotEnoughQuantity("Недостаточно инструментов для продажи")
        portfolio.balance += total_cost
        update_position_on_sell(position, quantity)
    portfolio.save()
    trade.execution_price = price
    trade.status = Trade.Status.executed
    trade.executed_at = timezone.now()
    trade.save()
    return trade
    

def update_position_on_buy(portfolio, instrument, quantity, price):
    position, created = Position.objects.get_or_create(portfolio=portfolio, 
                                                       instrument=instrument, 
                                                       defaults={'quantity': quantity, 'average_price': price})
    if not created:
        total_quantity = position.quantity + quantity
        position.average_price = (position.average_price * position.quantity + price * quantity) / total_quantity
        position.quantity = total_quantity
        position.save()

def update_position_on_sell(possition, quantity):
    possition.quantity -= quantity
    if possition.quantity == 0:
        possition.delete()
    else:
        possition.save()

def check_pending_limit_orders():
    pending_orders = Trade.objects.filter(
        status=Trade.Status.pending, 
        execution_type=Trade.ExecutionType.limit
    )
    for trade in pending_orders:
        curreint_price = trade.instrument.current_price
        is_order_existed =( (trade.order_type == Trade.OrderType.buy and curreint_price <= trade.price) or 
                            (trade.order_type == Trade.OrderType.sell and curreint_price >= trade.price)
                        )
        if(is_order_existed):
            try:
                execute_trade(trade)
            except (NotEnoughQuantity, NotEnoughMoney):
                trade.status = Trade.Status.cancelled
                trade.save()

def get_portfolio_total_value(portfolio):
    total_value = portfolio.balance
    positions = Position.objects.filter(portfolio=portfolio)
    for position in positions:
        total_value += position.instrument.current_price * position.quantity
    return total_value