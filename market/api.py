from rest_framework.viewsets import GenericViewSet, mixins

from market import service
from market.exceptions import TradeException
from market.exports import export_response
from market.models import InstrumentType, Instrument, Portfolio, Position, PriceHistory, Trade, Profile
from market.serializers import InstrumentTypeSerializer, InstrumentSerializer, PortfolioSerializer, PositionSerializer, PriceHistorySerializer, TradeSerializer, TradeUpdateSerializer

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login
from django.contrib.auth import authenticate

from datetime import datetime, timedelta
import pyotp
from django.core.cache import cache
from django.db.models import (
    Avg, Case, Count,
    DecimalField, ExpressionWrapper,
    F, FloatField, Min,
    Max, OuterRef, Q,
    Subquery, Sum, Value,
    When,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import serializers

from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from market.otp import OTPRequired, OTP_VALIDITY_SECONDS, get_session_otp_key

class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


def apply_query_filters(queryset, query_params, filters):
    for param, lookup in filters:
        value = query_params.get(param)
        if value:
            queryset = queryset.filter(**{lookup: value})
    return queryset


def get_admin_permissions(action, read_actions):
    if action in read_actions:
        return [IsAuthenticated()]
    return [IsAdminUser(), OTPRequired()]


def get_otp_permissions(action, protected_actions):
    permissions = [IsAuthenticated()]
    if action in protected_actions:
        permissions.append(OTPRequired())
    return permissions


class OTPSerializer(serializers.Serializer):
    key = serializers.RegexField(regex=r"^\d{6}$")


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
        if self.request.user.is_authenticated and self.request.session.session_key:
            cache.delete(get_session_otp_key(self.request))
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
        email = self.request.data.get('email', '')

        if not username or not password:
            return Response({'success': False, 'detail': 'Укажите логин и пароль'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'success': False, 'detail': 'Пользователь уже существует'}, status=400)

        User.objects.create_user(username=username, password=password, email=email)
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

    @action(detail=False, methods=["GET"], url_path="otp-setup", permission_classes=[IsAuthenticated])
    def otp_setup(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        data = {"configured": profile.otp_enabled}
        if not profile.otp_enabled:
            data["secret"] = profile.otp_key
        return Response(data)

    @action(detail=False, methods=["GET"], url_path="otp-status", permission_classes=[IsAuthenticated])
    def otp_status(self, request):
        expires_at = cache.get(get_session_otp_key(request), 0)
        is_confirmed = expires_at > timezone.now().timestamp()
        active_until = (
            datetime.fromtimestamp(expires_at, tz=timezone.get_current_timezone()).isoformat()
            if is_confirmed
            else None
        )
        return Response({
            "confirmed": is_confirmed,
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
        cache.set(
            get_session_otp_key(request),
            expires_at.timestamp(),
            timeout=OTP_VALIDITY_SECONDS,
        )
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

    def get_permissions(self):
        return get_admin_permissions(
            self.action, ("list", "retrieve", "stats", "export")
        )
    
    def get_queryset(self):
        qs = super().get_queryset().annotate(instruments_count=Count('instrument'))
        return apply_query_filters(
            qs,
            self.request.query_params,
            (
                ("id", "id"),
                ("name", "name__icontains"),
                ("count_from", "instruments_count__gte"),
                ("count_to", "instruments_count__lte"),
            ),
        )

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

    @action(detail=False, methods=["GET"], url_path="export")
    def export(self, request):
        types = self.get_queryset().order_by("id").iterator()
        rows = (
            (item.id, item.name, item.instruments_count)
            for item in types
        )
        return export_response(
            request,
            "instrument_types",
            "Типы инструментов",
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
    queryset = Instrument.objects.all().order_by("id")
    serializer_class = InstrumentSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        return get_admin_permissions(
            self.action, ("list", "retrieve", "stats", "leaders", "export")
        )

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
        change = self.request.query_params.get("change")

        if search:
            qs = qs.filter(Q(ticker__icontains=search) | Q(name__icontains=search))
        qs = apply_query_filters(
            qs,
            self.request.query_params,
            (
                ("type", "instrument_type_id"),
                ("price_from", "current_price__gte"),
                ("price_to", "current_price__lte"),
                ("updated_date", "price_updated_at__date"),
            ),
        )
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
            request,
            "instruments",
            "Инструменты",
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

    def get_permissions(self):
        return get_otp_permissions(
            self.action, ("create", "update", "partial_update", "destroy")
        )

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get("user")
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    def _list_queryset(self):
        qs = self.get_queryset().select_related("user").annotate(
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

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)
        return apply_query_filters(
            qs,
            self.request.query_params,
            (
                ("balance_from", "balance__gte"),
                ("balance_to", "balance__lte"),
                ("value_from", "total_value__gte"),
                ("value_to", "total_value__lte"),
            ),
        )

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self._list_queryset())
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="export")
    def export(self, request):
        portfolios = self._list_queryset().order_by("id")
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
            request,
            "portfolios",
            "Портфели",
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
        qs = apply_query_filters(
            qs,
            self.request.query_params,
            (
                ("quantity_from", "quantity__gte"),
                ("quantity_to", "quantity__lte"),
                ("value_from", "position_value__gte"),
                ("value_to", "position_value__lte"),
            ),
        )
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
            request,
            "positions",
            "Позиции портфеля",
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
        return apply_query_filters(
            qs,
            self.request.query_params,
            (
                ("instrument", "instrument_id"),
                ("date_from", "timestamp__date__gte"),
                ("date_to", "timestamp__date__lte"),
                ("price_from", "price__gte"),
                ("price_to", "price__lte"),
            ),
        )

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

    @action(detail=False, methods=["GET"], url_path="export")
    def export(self, request):
        records = list(
            self.get_queryset()
            .order_by("timestamp", "id")
            .values_list("timestamp", "price")
        )
        rows = []
        older_price = None
        for timestamp, price in records:
            change = (
                (price / older_price - 1) * 100
                if older_price
                else 0
            )
            rows.append((timestamp, price, change))
            older_price = price
        rows.reverse()
        return export_response(
            request,
            "price_history",
            "История цен",
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
    queryset = Trade.objects.all().prefetch_related("images").order_by("-created_at", "-id")
    serializer_class = TradeSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        return get_otp_permissions(
            self.action,
            ("create", "update", "partial_update", "destroy", "cancel"),
        )

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
        qs = apply_query_filters(
            qs,
            self.request.query_params,
            (
                ("created", "created_at__date"),
                ("executed", "executed_at__date"),
                ("order_type", "order_type"),
                ("execution_type", "execution_type"),
                ("status", "status"),
            ),
        )

        ticker = self.request.query_params.get("ticker")
        if ticker:
            qs = qs.filter(instrument__ticker__icontains=ticker)
        return apply_query_filters(
            qs,
            self.request.query_params,
            (
                ("total_from", "total_amount__gte"),
                ("total_to", "total_amount__lte"),
            ),
        )

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
            request,
            "trades",
            "История сделок",
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

