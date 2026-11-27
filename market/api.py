from market import service
from market.exceptions import TradeException
from market.exports import export_response
from market.models import InstrumentType, Instrument, Portfolio, Position, PriceHistory, Trade, Profile
from market.serializers import InstrumentTypeSerializer, InstrumentSerializer, PortfolioSerializer, PositionSerializer, PriceHistorySerializer, TradeSerializer, TradeUpdateSerializer

from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login
from django.contrib.auth import authenticate

from datetime import datetime, timedelta
import pyotp
from django.db.models import (
    Avg, Case, Count,
    DecimalField,
    F, FloatField, Min,
    Max, OuterRef, Q,
    Subquery, Sum,
    When,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import serializers

from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from market.otp import OTPRequired, OTP_VALIDITY_SECONDS, get_otp_expiration

from statistics import median
from decimal import Decimal

class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

class OTPSerializer(serializers.Serializer):
    key = serializers.RegexField(regex=r"^\d{6}$")

class ProfileViewSet(GenericViewSet):
    queryset = User.objects.all()

    @action(detail=False, url_path="me", methods=["GET"])
    def get_me(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response({"is_authenticated": False})

        return Response({
            "is_authenticated": True,
            "username": user.username,
            "id": user.id,
            "is_superuser": user.is_superuser,
            "email": user.email,
            "date_joined": user.date_joined,
            "last_login": user.last_login,
            "portfolios_count": user.portfolios.count(),
        })

    @action(detail=False, url_path="logout", methods=["POST"])
    def logout(self, request, *args, **kwargs):
        django_logout(request)
        return Response()

    @action(detail=False, url_path="login", methods=["POST"])
    def login(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"success": False}, status=403)

        django_login(request, user)
        return Response({"success": True})

    @action(detail=False, url_path="register", methods=['POST'])
    def register(self, *args, **kwargs):
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        email = self.request.data.get('email', '')

        if not username or not password:
            return Response({'success': False, 'detail': 'Укажите логин и пароль'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'success': False, 'detail': 'Пользователь уже существует'}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email)
        django_login(self.request, user)
        Portfolio.objects.create(user=user, name='Основной', balance=10000)
        return Response({'success': True}, status=201)

    @action(
    detail=False,
    url_path="users",
    methods=["GET"],
    permission_classes=[IsAdminUser],
    )
    def get_users(self, request, *args, **kwargs):
        users = User.objects.values("id", "username", "first_name", "last_name")
        return Response(list(users))

    @action(detail=False, methods=["GET"], url_path="otp-setup", permission_classes=[IsAuthenticated])
    def otp_setup(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        data = {"configured": profile.otp_enabled}
        if not profile.otp_enabled:
            data["secret"] = profile.otp_key
        return Response(data)

    @action(detail=False, methods=["GET"], url_path="otp-status", permission_classes=[IsAuthenticated])
    def otp_status(self, request):
        expires_at = get_otp_expiration(request)
        active_until = None

        if expires_at is not None:
            active_until = datetime.fromtimestamp(
                expires_at, tz=timezone.get_current_timezone()
            ).isoformat()

        return Response({
            "confirmed": expires_at is not None,
            "active_until": active_until,
        })

    @action(detail=False, methods=["POST"], url_path="otp-login", permission_classes=[IsAuthenticated])
    def otp_login(self, request):
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not pyotp.TOTP(profile.otp_key).verify(serializer.validated_data["key"], valid_window=1):
            return Response({
                "success": False,
                "detail": "Неверный код. Проверьте код в приложении-аутентификаторе.",
            }, status=400)

        if not profile.otp_enabled:
            profile.otp_enabled = True
            profile.save(update_fields=["otp_enabled"])

        expires_at = timezone.now() + timedelta(seconds=OTP_VALIDITY_SECONDS)
        request.session["otp"] = {
            "user_id": request.user.pk,
            "expires_at": expires_at.timestamp(),
        }
        return Response({
            "success": True,
            "active_until": expires_at.isoformat(),
        })


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
    permission_classes = [IsAdminUser, OTPRequired]

    def get_permissions(self):
        if self.action in ("list", "retrieve", "stats", "export"):
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def get_queryset(self):
        qs = super().get_queryset().annotate(instruments_count=Count("instrument"))
        params = self.request.query_params
        type_id = params.get("id")
        name = params.get("name")
        count_from = params.get("count_from")
        count_to = params.get("count_to")
        if type_id:
            qs = qs.filter(id=type_id)
        if name:
            qs = qs.filter(name__icontains=name)
        if count_from:
            qs = qs.filter(instruments_count__gte=count_from)
        if count_to:
            qs = qs.filter(instruments_count__lte=count_to)

        return qs

    def perform_destroy(self, instance):
        if instance.instrument_set.exists():
            raise ValidationError('Нельзя удалить тип, к которому привязаны инструменты')
        instance.delete()

    @action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        data = InstrumentType.objects.aggregate(
            type_count=Count("id", distinct=True),
            instrument_count=Count("instrument"),
        )
        return Response(data)

    @action(detail=False, methods=["GET"], url_path="export")
    def export(self, request):
        types = self.get_queryset().order_by("id").iterator()
        rows = (
            (item.id, item.name, item.instruments_count)
            for item in types
        )
        return export_response(
            "instrument_types",
            ["ID", "Название", "Инструментов"],
            rows,
        )

class InstrumentViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    GenericViewSet):
    queryset = Instrument.objects.select_related("instrument_type").order_by("id")
    serializer_class = InstrumentSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAdminUser, OTPRequired]

    def get_permissions(self):
        if self.action in ("list", "retrieve", "stats", "leaders", "export"):
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        days = 7 if params.get("period") == "week" else 1
        since = timezone.now() - timedelta(days=days)

        history = PriceHistory.objects.filter(instrument_id=OuterRef("pk"))
        newest_first = history.order_by("-timestamp")
        price_before_period = newest_first.filter(timestamp__lte=since).values("price")[:1]
        oldest_price = history.order_by("timestamp").values("price")[:1]

        qs = qs.annotate(
            prev_price=Coalesce(Subquery(price_before_period), Subquery(oldest_price)),
            price_updated_at=Subquery(newest_first.values("timestamp")[:1]),
        )

        change_percent = (F("current_price") - F("prev_price")) * 100.0 / F("prev_price")
        qs = qs.annotate(
            change_percent=Case(
                When(prev_price__gt=0, then=change_percent),
                default=0.0,
                output_field=FloatField(),
            )
        )

        search = params.get("search")
        change = params.get("change")

        if search:
            qs = qs.filter(Q(ticker__icontains=search) | Q(name__icontains=search))
        if params.get("type"):
            qs = qs.filter(instrument_type_id=params["type"])
        if params.get("price_from"):
            qs = qs.filter(current_price__gte=params["price_from"])
        if params.get("price_to"):
            qs = qs.filter(current_price__lte=params["price_to"])
        if params.get("updated_date"):
            qs = qs.filter(price_updated_at__date=params["updated_date"])
        
        if change == "up":
            qs = qs.filter(change_percent__gt=0)
        elif change == "down":
            qs = qs.filter(change_percent__lt=0)
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
        prices = list(qs.order_by().values_list("current_price", flat=True))

        cheapest = qs.order_by("current_price").values("ticker", "current_price").first()
        priciest = qs.order_by("-current_price").values("ticker", "current_price").first()
        aggregate.update({
            "median": median(prices) if prices else 0,
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

    @action(detail=False, methods=["GET"], url_path="export")
    def export(self, request):
        instruments = self.get_queryset().select_related("instrument_type").order_by("id")
        rows = (
            (
                item.ticker,
                item.name,
                item.instrument_type.name,
                item.current_price,
                item.change_percent,
                item.price_updated_at,
            )
            for item in instruments.iterator()
        )
        return export_response(
            "instruments",
            ["Тикер", "Название", "Тип", "Цена", "Изменение, %", "Обновлено"],
            rows,
        )

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
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), OTPRequired()]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        params = self.request.query_params

        if not user.is_superuser:
            qs = qs.filter(user=user)
        elif params.get("user"):
            qs = qs.filter(user_id=params["user"])

        if self.action not in ("list", "export"):
            return qs

        qs = qs.select_related("user").annotate(
            positions_count=Count("positions", distinct=True),
            positions_value=Sum(
                F("positions__quantity") * F("positions__instrument__current_price"),
                default=0,
                output_field=DecimalField(max_digits=30, decimal_places=4),
            ),
            positions_cost=Sum(
                F("positions__quantity") * F("positions__average_price"),
                default=0,
                output_field=DecimalField(max_digits=30, decimal_places=4),
            ),
            total_value=F("balance") + F("positions_value"),
        )

        if params.get("search"):
            qs = qs.filter(name__icontains=params["search"])
        if params.get("balance_from"):
            qs = qs.filter(balance__gte=params["balance_from"])
        if params.get("balance_to"):
            qs = qs.filter(balance__lte=params["balance_to"])
        if params.get("value_from"):
            qs = qs.filter(total_value__gte=params["value_from"])
        if params.get("value_to"):
            qs = qs.filter(total_value__lte=params["value_to"])

        return qs

    @action(detail=False, methods=["GET"], url_path="export")
    def export(self, request):
        portfolios = self.get_queryset()
        rows = (
            (
                item.name,
                item.user.username,
                item.balance,
                item.positions_count,
                item.positions_value,
                item.positions_cost,
                item.total_value,
                item.positions_value - item.positions_cost,
            )
            for item in portfolios.iterator()
        )
        return export_response(
            "portfolios",
            [
                "Название",
                "Владелец",
                "Баланс",
                "Позиций",
                "Стоимость позиций",
                "Вложено в позиции",
                "Общая стоимость",
                "Прибыль/убыток",
            ],
            rows,
        )

    @action(detail=False, methods=["GET"], url_path="stats")
    def stats(self, request):
        portfolios = self.get_queryset()
        portfolio_id = request.query_params.get("portfolio")
        if portfolio_id:
            portfolios = portfolios.filter(id=portfolio_id)

        portfolio_data = portfolios.aggregate(
            count=Count("id"),
            balance=Sum("balance", default=0),
        )

        positions_data = Position.objects.filter(
            portfolio__in=portfolios
        ).aggregate(
            count=Count("id"),
            positions_value=Sum(F("quantity") * F("instrument__current_price"), default=0),
            cost=Sum(F("quantity") * F("average_price"), default=0),
        )

        trades_data = Trade.objects.filter(portfolio__in=portfolios).aggregate(
            count=Count("id"),
            pending_count=Count("id", filter=Q(status=Trade.Status.pending)),
        )
        count = portfolio_data["count"]
        balance = float(portfolio_data["balance"])
        positions_value = float(positions_data["positions_value"])
        cost = float(positions_data["cost"])
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
    queryset = Position.objects.select_related(
        "instrument__instrument_type", "portfolio"
    ).order_by("id")
    serializer_class = PositionSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        instrument_id = self.request.query_params.get('instrument')
        portfolio_id = self.request.query_params.get('portfolio')
        qs = qs.annotate(
            position_value=F("quantity") * F("instrument__current_price"),
            position_profit=F("quantity") * (F("instrument__current_price") - F("average_price")),
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

        params = self.request.query_params
        result = params.get("result")

        if params.get("ticker"):
            qs = qs.filter(instrument__ticker__icontains=params["ticker"])
        if params.get("type"):
            qs = qs.filter(instrument__instrument_type_id=params["type"])
        if params.get("quantity_from"):
            qs = qs.filter(quantity__gte=params["quantity_from"])
        if params.get("quantity_to"):
            qs = qs.filter(quantity__lte=params["quantity_to"])
        if params.get("value_from"):
            qs = qs.filter(position_value__gte=params["value_from"])
        if params.get("value_to"):
            qs = qs.filter(position_value__lte=params["value_to"])
        
        if result == "profit":
            qs = qs.filter(position_profit__gt=0)
        elif result == "loss":
            qs = qs.filter(position_profit__lt=0)
        return qs.order_by("-position_profit", "id")

    @action(detail=False, methods=["GET"], url_path="export")
    def export(self, request):
        positions = self.get_queryset().select_related(
            "instrument__instrument_type"
        )
        rows = (
            (
                item.instrument.ticker,
                item.instrument.name,
                item.instrument.instrument_type.name,
                item.quantity,
                item.average_price,
                item.instrument.current_price,
                item.position_value,
                item.position_profit,
                (
                    item.position_profit
                    / (item.quantity * item.average_price)
                    * 100
                    if item.quantity and item.average_price
                    else 0
                ),
            )
            for item in positions.iterator()
        )
        return export_response(
            "positions",
            [
                "Тикер",
                "Инструмент",
                "Тип",
                "Количество",
                "Средняя цена",
                "Текущая цена",
                "Стоимость",
                "Прибыль/убыток",
                "Прибыль/убыток, %",
            ],
            rows,
        )


class PriceHistoryViewset(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet):
    queryset = PriceHistory.objects.all().order_by("-timestamp", "-id")
    serializer_class = PriceHistorySerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        if params.get("instrument"):
            qs = qs.filter(instrument_id=params["instrument"])
        if params.get("date_from"):
            qs = qs.filter(timestamp__date__gte=params["date_from"])
        if params.get("date_to"):
            qs = qs.filter(timestamp__date__lte=params["date_to"])
        if params.get("price_from"):
            qs = qs.filter(price__gte=params["price_from"])
        if params.get("price_to"):
            qs = qs.filter(price__lte=params["price_to"])

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
        prices = qs.values_list("price", flat=True)
        data["first"] = prices.reverse().first()
        data["last"] = prices.first()
        return Response(data)

    @action(detail=False, methods=["GET"], url_path="export")
    def export(self, request):
        records = (
            self.get_queryset()
            .order_by("timestamp", "id")
            .values_list("timestamp", "price")
            .iterator()
        )
        rows = []
        older_price = None
        for timestamp, price in records:
            change = (price / older_price - 1) * 100 if older_price else 0
            rows.append((timestamp, price, change))
            older_price = price
        rows.reverse()
        return export_response(
            "price_history",
            ["Дата и время", "Цена", "Изменение, %"],
            rows,
        )

class TradeViewset(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet):
    queryset = (
        Trade.objects.select_related("instrument__instrument_type")
        .prefetch_related("images")
        .order_by("-created_at", "-id")
    )
    serializer_class = TradeSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "cancel"):
            return [IsAuthenticated(), OTPRequired()]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        user = self.request.user

        if not user.is_superuser:
            qs = qs.filter(portfolio__user=user)
        elif params.get("user"):
            qs = qs.filter(portfolio__user_id=params["user"])

        unit_price = Coalesce("execution_price", "price", Decimal("0"))
        qs = qs.annotate(total_amount=F("quantity") * unit_price)

        if params.get("portfolio"):
            qs = qs.filter(portfolio_id=params["portfolio"])
        if params.get("ticker"):
            qs = qs.filter(instrument__ticker__icontains=params["ticker"])
        if params.get("created"):
            qs = qs.filter(created_at__date=params["created"])
        if params.get("executed"):
            qs = qs.filter(executed_at__date=params["executed"])
        if params.get("order_type"):
            qs = qs.filter(order_type=params["order_type"])
        if params.get("execution_type"):
            qs = qs.filter(execution_type=params["execution_type"])
        if params.get("status"):
            qs = qs.filter(status=params["status"])
        if params.get("total_from"):
            qs = qs.filter(total_amount__gte=params["total_from"])
        if params.get("total_to"):
            qs = qs.filter(total_amount__lte=params["total_to"])

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
        total = stats["total"]
        stats["executedShare"] = round(stats["executed"] / total * 100) if total else 0
        stats["cancelledShare"] = round(stats["cancelled"] / total * 100) if total else 0
        stats["buys"] = float(stats["buys"] or 0)
        stats["sells"] = float(stats["sells"] or 0)
        return Response(stats)

    @action(detail=False, methods=["GET"], url_path="export")
    def export(self, request):
        trades = self.get_queryset().select_related(
            "portfolio", "instrument"
        ).order_by("-created_at", "-id")
        rows = (
            (
                item.created_at,
                item.executed_at,
                item.portfolio.name,
                item.instrument.ticker,
                item.instrument.name,
                item.get_order_type_display(),
                item.get_execution_type_display(),
                item.quantity,
                item.price,
                item.execution_price,
                item.total_amount,
                item.get_status_display(),
                ", ".join(image.image.name for image in item.images.all()),
            )
            for item in trades.iterator(chunk_size=2000)
        )
        return export_response(
            "trades",
            [
                "Создана",
                "Исполнена",
                "Портфель",
                "Тикер",
                "Инструмент",
                "Операция",
                "Исполнение",
                "Количество",
                "Лимитная цена",
                "Цена исполнения",
                "Сумма",
                "Статус",
                "Изображения",
            ],
            rows,
        )

    def perform_create(self, serializer):
        trade = serializer.save()

        if trade.execution_type != Trade.ExecutionType.market:
            service.StockMatrketService.check_pending_limit_orders(trade.instrument)
            return

        try:
            service.StockMatrketService.execute_trade(trade)
        except TradeException:
            trade.status = Trade.Status.cancelled
            trade.save()
            raise

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
        return Response(self.get_serializer(trade).data)

