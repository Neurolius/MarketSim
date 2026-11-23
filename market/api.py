from xml.dom import ValidationErr

from rest_framework.viewsets import GenericViewSet, mixins

from market import service
from market.exceptions import TradeException
from market.models import InstrumentType, Instrument, Portfolio, Position, PriceHistory, Trade
from market.serializers import InstrumentTypeSerializer, InstrumentSerializer, PortfolioSerializer, PositionSerializer, PriceHistorySerializer, TradeSerializer, TradeUpdateSerializer

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login
from django.contrib.auth import authenticate

from datetime import timedelta
from django.db.models import (
    Avg,
    Case,
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    FloatField,
    Min,
    Max,
    OuterRef,
    Q,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

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
                "is_superuser": self.request.user.is_superuser,
                "email": self.request.user.email,
                "date_joined": self.request.user.date_joined,
                "last_login": self.request.user.last_login,
                "portfolios_count": self.request.user.portfolios.count()
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

    @action(
    detail=False,
    url_path="users",
    methods=["GET"],
    permission_classes=[IsAdminUser],
    )
    def get_users(self, request, *args, **kwargs):
        users = User.objects.values("id", "username", "first_name", "last_name")
        return Response(list(users))


class InstrumentTypeViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    GenericViewSet):
    queryset = InstrumentType.objects.all().order_by("id")
    serializer_class = InstrumentTypeSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.action in ("list", "retrieve", "stats"):
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        return super().get_queryset().annotate(instruments_count=Count('instrument'))

    def perform_destroy(self, instance):
        if instance.instrument_set.exists():
            raise ValidationError('Нельзя удалить тип, к которому привязаны инструменты')
        instance.delete()

    @action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        data = InstrumentType.objects.annotate(
            instruments_count=Count("instrument")
        ).aggregate(
            type_count=Count("id"),
            instrument_count=Sum("instruments_count"),
        )
        return Response(data)

class InstrumentViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    GenericViewSet):
    queryset = Instrument.objects.all().order_by("id")
    serializer_class = InstrumentSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'stats', 'leaders'):
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()

        hours = {'day': 24, 'week': 24 * 7}.get(self.request.query_params.get('period'),24)
        since = timezone.now() - timedelta(hours=hours)
        history = PriceHistory.objects.filter(instrument=OuterRef('pk'))
        price_before = history.filter(timestamp__lte=since).order_by('-timestamp').values('price')[:1]
        first_price = history.order_by('timestamp').values('price')[:1]
        latest_timestamp = history.order_by('-timestamp').values('timestamp')[:1]

        qs = qs.annotate(
            prev_price=Coalesce(Subquery(price_before), Subquery(first_price)),
            price_updated_at=Subquery(latest_timestamp),
        )
        qs = qs.annotate(
            change_percent=Case(
                When(
                    prev_price__gt=0,
                    then=ExpressionWrapper(
                        (F("current_price") - F("prev_price"))
                        * Value(100.0)
                        / F("prev_price"),
                        output_field=FloatField(),
                    ),
                ),
                default=Value(0.0),
                output_field=FloatField(),
            )
        )

        search = self.request.query_params.get("search")
        instrument_type = self.request.query_params.get("type")
        price_from = self.request.query_params.get("price_from")
        price_to = self.request.query_params.get("price_to")
        change = self.request.query_params.get("change")
        updated_date = self.request.query_params.get("updated_date")

        if search:
            qs = qs.filter(Q(ticker__icontains=search) | Q(name__icontains=search))
        if instrument_type:
            qs = qs.filter(instrument_type_id=instrument_type)
        if price_from:
            qs = qs.filter(current_price__gte=price_from)
        if price_to:
            qs = qs.filter(current_price__lte=price_to)
        if change == "up":
            qs = qs.filter(change_percent__gt=0)
        elif change == "down":
            qs = qs.filter(change_percent__lt=0)
        if updated_date:
            qs = qs.filter(price_updated_at__date=updated_date)
        return qs

    @action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        qs = self.get_queryset()
        aggregate = qs.aggregate(
            count=Count("id"),
            average=Avg("current_price"),
            minimum=Min("current_price"),
            maximum=Max("current_price"),
            rising_count=Count("id", filter=Q(change_percent__gt=0)),
            falling_count=Count("id", filter=Q(change_percent__lt=0)),
        )
        prices = [
            price
            for _, price in qs.order_by("current_price").values_list("id", "current_price")
        ]
        if prices:
            middle = len(prices) // 2
            median = (
                prices[middle]
                if len(prices) % 2
                else (prices[middle - 1] + prices[middle]) / 2
            )
        else:
            median = 0

        cheapest = qs.order_by("current_price").values("ticker", "current_price").first()
        priciest = qs.order_by("-current_price").values("ticker", "current_price").first()
        aggregate.update({
            "median": median,
            "cheapest": cheapest,
            "priciest": priciest,
            "by_type": list(
                qs.values("instrument_type__id", "instrument_type__name")
                .annotate(count=Count("id"))
                .order_by("instrument_type__id")
            ),
        })
        return Response(aggregate)

    @action(detail=False, methods=["GET"], url_path="leaders")
    def leaders(self, request):
        instruments = self.get_queryset().order_by("-change_percent", "id")[:6]
        serializer = self.get_serializer(instruments, many=True)
        return Response(serializer.data)


class PortfolioViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    GenericViewSet):
    queryset = Portfolio.objects.all().order_by("id")
    serializer_class = PortfolioSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get("user")
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset().annotate(
            positions_count=Count("positions", distinct=True),
            positions_value=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F("positions__quantity") * F("positions__instrument__current_price"),
                        output_field=DecimalField(max_digits=30, decimal_places=4),
                    )
                ),
                Value(0, output_field=DecimalField(max_digits=30, decimal_places=4)),
            ),
            positions_cost=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F("positions__quantity") * F("positions__average_price"),
                        output_field=DecimalField(max_digits=30, decimal_places=4),
                    )
                ),
                Value(0, output_field=DecimalField(max_digits=30, decimal_places=4)),
            ),
        ).annotate(total_value=F("balance") + F("positions_value"))

        search = request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)
        for param, lookup in (
            ("balance_from", "balance__gte"),
            ("balance_to", "balance__lte"),
            ("value_from", "total_value__gte"),
            ("value_to", "total_value__lte"),
        ):
            value = request.query_params.get(param)
            if value:
                qs = qs.filter(**{lookup: value})

        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        portfolios = self.get_queryset()
        portfolio_id = request.query_params.get("portfolio")
        if portfolio_id:
            portfolios = portfolios.filter(id=portfolio_id)

        portfolio_data = portfolios.aggregate(
            count=Count("id"),
            balance=Sum("balance"),
        )

        positions_data = Position.objects.filter(
            portfolio__in=portfolios
        ).aggregate(
            count=Count("id"),
            positions_value=Sum(
                ExpressionWrapper(
                    F("quantity") * F("instrument__current_price"),
                    output_field=DecimalField(max_digits=30, decimal_places=4),
                )
            ),
            cost=Sum(
                ExpressionWrapper(
                    F("quantity") * F("average_price"),
                    output_field=DecimalField(max_digits=30, decimal_places=4),
                )
            ),
        )

        trades_data = Trade.objects.filter(portfolio__in=portfolios).aggregate(
            count=Count("id"),
            pending_count=Count("id", filter=Q(status=Trade.Status.pending)),
        )
        count = portfolio_data["count"] or 0
        balance = float(portfolio_data["balance"] or 0)
        positions_value = float(positions_data["positions_value"] or 0)
        cost = float(positions_data["cost"] or 0)
        total_value = balance + positions_value
        profit = positions_value - cost

        return Response({
            "count": count,
            "balance": balance,
            "positionsValue": positions_value,
            "totalValue": total_value,
            "avg": total_value / count if count else 0,
            "profit": profit,
            "profitPercent": profit / cost * 100 if cost else 0,
            "freeShare": balance / total_value * 100 if total_value else 0,
            "positionsCount": positions_data["count"] or 0,
            "tradeCount": trades_data["count"] or 0,
            "pendingCount": trades_data["pending_count"] or 0,
        })

class PositionViewset(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet):
    queryset = Position.objects.select_related('instrument', 'portfolio').order_by("id")
    serializer_class = PositionSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        instrument_id = self.request.query_params.get('instrument')
        portfolio_id = self.request.query_params.get('portfolio')
        qs = qs.annotate(
            position_value=ExpressionWrapper(
                F("quantity") * F("instrument__current_price"),
                output_field=DecimalField(max_digits=30, decimal_places=4),
            ),
            position_profit=ExpressionWrapper(
                F("quantity") * (F("instrument__current_price") - F("average_price")),
                output_field=DecimalField(max_digits=30, decimal_places=4),
            ),
        )
        if portfolio_id:
            qs = qs.filter(portfolio_id=portfolio_id)
        if instrument_id:
            qs = qs.filter(instrument_id=instrument_id)
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get("user")
            if user_id:
                qs = qs.filter(portfolio__user_id=user_id)
        else:
            qs = qs.filter(portfolio__user=self.request.user)

        ticker = self.request.query_params.get("ticker")
        instrument_type = self.request.query_params.get("type")
        result = self.request.query_params.get("result")
        if ticker:
            qs = qs.filter(instrument__ticker__icontains=ticker)
        if instrument_type:
            qs = qs.filter(instrument__instrument_type_id=instrument_type)
        for param, lookup in (
            ("quantity_from", "quantity__gte"),
            ("quantity_to", "quantity__lte"),
            ("value_from", "position_value__gte"),
            ("value_to", "position_value__lte"),
        ):
            value = self.request.query_params.get(param)
            if value:
                qs = qs.filter(**{lookup: value})
        if result == "profit":
            qs = qs.filter(position_profit__gt=0)
        elif result == "loss":
            qs = qs.filter(position_profit__lt=0)
        return qs.order_by("-position_profit", "id")


class PriceHistoryViewset(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet):
    queryset = PriceHistory.objects.all().order_by("-timestamp", "-id")
    serializer_class = PriceHistorySerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        instrument_id = self.request.query_params.get('instrument')
        if instrument_id:
            qs = qs.filter(instrument_id=instrument_id)
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        price_from = self.request.query_params.get("price_from")
        price_to = self.request.query_params.get("price_to")
        if date_from:
            qs = qs.filter(timestamp__date__gte=date_from)
        if date_to:
            qs = qs.filter(timestamp__date__lte=date_to)
        if price_from:
            qs = qs.filter(price__gte=price_from)
        if price_to:
            qs = qs.filter(price__lte=price_to)
        return qs

    @action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        qs = self.get_queryset()
        data = qs.aggregate(
            count=Count("id"),
            avg=Avg("price"),
            min=Min("price"),
            max=Max("price"),
        )
        data["first"] = qs.order_by("timestamp", "id").values_list("price", flat=True).first()
        data["last"] = qs.order_by("-timestamp", "-id").values_list("price", flat=True).first()
        return Response(data)

class TradeViewset(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet):
    queryset = Trade.objects.all().order_by("-created_at", "-id")
    serializer_class = TradeSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        portfolio_id = self.request.query_params.get('portfolio')
        if portfolio_id:
            qs = qs.filter(portfolio_id=portfolio_id)
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get("user")
            if user_id:
                qs = qs.filter(portfolio__user_id=user_id)
        else:
            qs = qs.filter(portfolio__user=self.request.user)

        qs = qs.annotate(
            total_amount=ExpressionWrapper(
                F("quantity") * Coalesce(F("execution_price"), F("price"), Value(0)),
                output_field=DecimalField(max_digits=30, decimal_places=4),
            )
        )
        for param, lookup in (
            ("created", "created_at__date"),
            ("executed", "executed_at__date"),
            ("order_type", "order_type"),
            ("execution_type", "execution_type"),
            ("status", "status"),
        ):
            value = self.request.query_params.get(param)
            if value:
                qs = qs.filter(**{lookup: value})

        ticker = self.request.query_params.get("ticker")
        if ticker:
            qs = qs.filter(instrument__ticker__icontains=ticker)
        for param, lookup in (
            ("total_from", "total_amount__gte"),
            ("total_to", "total_amount__lte"),
        ):
            value = self.request.query_params.get(param)
            if value:
                qs = qs.filter(**{lookup: value})
        return qs

    @action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        stats = self.get_queryset().aggregate(
            total=Count("id"),
            executed=Count("id", filter=Q(status=Trade.Status.executed)),
            pending=Count("id", filter=Q(status=Trade.Status.pending)),
            cancelled=Count("id", filter=Q(status=Trade.Status.cancelled)),
            buys=Sum(
                "total_amount",
                filter=Q(status=Trade.Status.executed, order_type=Trade.OrderType.buy),
            ),
            sells=Sum(
                "total_amount",
                filter=Q(status=Trade.Status.executed, order_type=Trade.OrderType.sell),
            ),
        )
        total = stats["total"] or 0
        executed = stats["executed"] or 0
        cancelled = stats["cancelled"] or 0
        return Response({
            "total": total,
            "executed": executed,
            "executedShare": round(executed / total * 100) if total else 0,
            "pending": stats["pending"] or 0,
            "cancelled": cancelled,
            "cancelledShare": round(cancelled / total * 100) if total else 0,
            "buys": float(stats["buys"] or 0),
            "sells": float(stats["sells"] or 0),
        })

    def perform_create(self, serializer):
        trade = serializer.save()
        if trade.execution_type == Trade.ExecutionType.market:
            try:
                service.StockMatrketService.execute_trade(trade)
            except TradeException:
                trade.status = Trade.Status.cancelled
                trade.save()
                raise
        else:
            service.StockMatrketService.check_pending_limit_orders(trade.instrument)

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return TradeUpdateSerializer
        return TradeSerializer

    def perform_update(self, serializer):
        if serializer.instance.status != Trade.Status.pending:
            raise TradeException('Изменить можно только ожидающую заявку')
        trade=serializer.save()
        service.StockMatrketService.check_pending_limit_orders(trade.instrument)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        trade = self.get_object()
        if trade.status != Trade.Status.pending:
            raise TradeException('Изменить можно только ожидающую заявку')
        trade.status = Trade.Status.cancelled
        trade.save()
        return Response(TradeSerializer(trade, context=self.get_serializer_context()).data)

