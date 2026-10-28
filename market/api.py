from xml.dom import ValidationErr

from rest_framework.viewsets import GenericViewSet, mixins

from market import service
from market.exceptions import TradeException
from market.models import InstrumentType, Instrument, Portfolio, Position, PriceHistory, Trade
from market.serializers import InstrumentTypeSerializer, InstrumentSerializer, PortfolioSerializer, PositionSerializer, PriceHistorySerializer, TradeSerializer

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login
from django.contrib.auth import authenticate


class ProfileViewSet(GenericViewSet):
    queryset = User.objects.all()
    @action(detail=False, url_path="me", methods=['GET'])
    def get_me(self, request, *args, **kwargs):
        data = {
            'is_authenticated': self.request.user.is_authenticated
        }
        if self.request.user.is_authenticated:
            data.update({
                "username": self.request.user.username,
                "id": self.request.user.id,
                "is_superuser": self.request.user.is_superuser
            })
        return Response(data=data)

    @action(detail=False, url_path="logout", methods=['POST'])
    def logout(self, *args, **kwargs):
        django_logout(self.request)
        return Response()

    @action(detail=False, url_path="login", methods=['POST'])
    def login(self, *args, **kwargs):
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        success = False
        status_code = 403
        user = authenticate(username=username, password=password)
        if user:
            success = True
            status_code = 200
            django_login(self.request, user)
        return Response({
            'success': success
        }, status=status_code)

    @action(detail=False, url_path="register", methods=['POST'])
    def register(self, *args, **kwargs):
        username = self.request.data.get('username')
        password = self.request.data.get('password')

        if not username or not password:
            return Response({'success': False, 'detail': 'Укажите логин и пароль'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'success': False, 'detail': 'Пользователь уже существует'}, status=400)

        User.objects.create_user(username=username, password=password)
        user = authenticate(username=username, password=password)
        if user:
            django_login(self.request, user)
            Portfolio.objects.create(user=user, name='Основной', balance=10000)
        return Response({'success': True}, status=200)


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

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs

class PositionViewset(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet):
    queryset = Position.objects.select_related('instrument', 'portfolio')
    serializer_class = PositionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(portfolio__user=self.request.user)
        return qs


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

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(portfolio__user=self.request.user)
        return qs

    def perform_create(self, serializer):
        trade = serializer.save()
        if trade.execution_type == Trade.ExecutionType.market:
            try:
                service.StockMatrketService.execute_trade(trade)
            except TradeException:
                trade.status = Trade.Status.cancelled
                trade.save()
                raise


