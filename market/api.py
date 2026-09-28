from xml.dom import ValidationErr

from rest_framework.viewsets import GenericViewSet, mixins

from market import service
from market.exceptions import TradeException
from market.models import InstrumentType, Instrument, Portfolio, Position, PriceHistory, Trade
from market.serializers import InstrumentTypeSerializer, InstrumentSerializer, PortfolioSerializer, PositionSerializer, PriceHistorySerializer, TradeSerializer

class InstrumentTypeViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    GenericViewSet):
    queryset = InstrumentType.objects.all()
    serializer_class = InstrumentTypeSerializer

class InstrumentViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    GenericViewSet):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer

class PortfolioViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    GenericViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer

class PositionViewset(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class PriceHistoryViewset(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet):
    queryset = PriceHistory.objects.all()
    serializer_class = PriceHistorySerializer

class TradeViewset(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    GenericViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer

    def perform_create(self, serializer):
        trade = serializer.save()
        if trade.execution_type == Trade.ExecutionType.market:
            try:
                service.execute_trade(trade)
            except TradeException:
                trade.status = Trade.Status.cancelled
                trade.save()
                raise


