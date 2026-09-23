from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, path
from django.conf import settings
from rest_framework.routers import DefaultRouter

from market.api import InstrumentTypeViewset, InstrumentViewset, PortfolioViewset, PositionViewset, PriceHistoryViewset, TradeViewset, ProfileViewset


router = DefaultRouter()
router.register("instrumenttype", InstrumentTypeViewset, basename="market")
router.register("instrument", InstrumentViewset, basename="instrument")
router.register("portfolio", PortfolioViewset, basename="portfolio")
router.register("position", PositionViewset, basename="position")
router.register("pricehistory", PriceHistoryViewset, basename="pricehistory")
router.register("trade", TradeViewset, basename="trade")
router.register("profile", ProfileViewset, basename="profile")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
