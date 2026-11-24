import pyotp
from django.test import TestCase
from rest_framework.test import APIClient
from model_bakery import baker
from market.models import InstrumentType, Instrument, Portfolio, Position, PriceHistory, Trade, Profile


def authenticate_with_otp(client, user):
    client.force_authenticate(user=user)
    profile, _ = Profile.objects.get_or_create(user=user)
    response = client.post(
        '/api/profile/otp-login/',
        {'key': pyotp.TOTP(profile.otp_key).now()},
        format='json',
    )
    assert response.status_code == 200


def response_results(response):
    data = response.json()
    return data.get('results', data)


class InstrumentTypeViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = baker.make('auth.User', is_staff=True)
        authenticate_with_otp(self.client, self.user)

    def test_get_list(self):
        instr_type = baker.make(InstrumentType)
        r = self.client.get('/api/instrumenttype/')
        data = response_results(r)
        assert len(data) == 1
        assert data[0]['name'] == instr_type.name

    def test_create(self):
        r = self.client.post('/api/instrumenttype/', {'name': 'test2'})

        new_id = r.json()['id']
        assert InstrumentType.objects.count() == 1
        assert InstrumentType.objects.get(id=new_id).name == 'test2'

    def test_stats(self):
        types = baker.make(InstrumentType, _quantity=2)
        baker.make(Instrument, instrument_type=types[0], _quantity=2)

        r = self.client.get('/api/instrumenttype/stats/')

        assert r.status_code == 200
        assert r.json()['type_count'] == 2
        assert r.json()['instrument_count'] == 2

    def test_delete(self):
        instr_types = baker.make(InstrumentType, 10)
        r = self.client.get('/api/instrumenttype/')
        data = response_results(r)
        assert len(data) == 10

        instr_type_id_to_delete = instr_types[3].id
        self.client.delete(f'/api/instrumenttype/{instr_type_id_to_delete}/')

        r = self.client.get('/api/instrumenttype/')
        data = response_results(r)
        assert len(data) == 9
        assert instr_type_id_to_delete not in [i['id'] for i in data]

    def test_update(self):
        instr_types = baker.make(InstrumentType, 10)
        instr_type: InstrumentType = instr_types[3]

        r = self.client.get(f'/api/instrumenttype/{instr_type.id}/')
        data = r.json()
        assert data['name'] == instr_type.name

        r = self.client.put(f'/api/instrumenttype/{instr_type.id}/', {'name': 'test2'})
        assert r.status_code == 200
        r = self.client.get(f'/api/instrumenttype/{instr_type.id}/')
        data = r.json()
        assert data['name'] == 'test2'

        instr_type.refresh_from_db()
        assert data['name'] == instr_type.name


class InstrumentViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = baker.make('auth.User', is_staff=True)
        authenticate_with_otp(self.client, self.user)

    def test_get_list(self):
        instrument = baker.make(Instrument)
        r = self.client.get('/api/instrument/')
        data = response_results(r)
        assert len(data) == 1
        assert data[0]['ticker'] == instrument.ticker

    def test_create(self):
        instr_type = baker.make(InstrumentType)
        r = self.client.post('/api/instrument/', {
            'ticker': 'AAPL',
            'name': 'Apple Inc.',
            'instrument_type': instr_type.id,
        })

        new_id = r.json()['id']
        assert Instrument.objects.count() == 1
        new_instrument = Instrument.objects.get(id=new_id)
        assert new_instrument.ticker == 'AAPL'
        assert new_instrument.current_price == 0

    def test_stats_and_leaders_for_authenticated_user(self):
        user = baker.make('auth.User')
        self.client.force_authenticate(user=user)
        baker.make(Instrument, current_price=10)
        baker.make(Instrument, current_price=20, _quantity=2)

        stats = self.client.get('/api/instrument/stats/')
        leaders = self.client.get('/api/instrument/leaders/')

        assert stats.status_code == 200
        assert stats.json()['count'] == 3
        assert float(stats.json()['median']) == 20
        assert leaders.status_code == 200
        assert len(leaders.json()) == 3

    def test_delete(self):
        instruments = baker.make(Instrument, 10)
        r = self.client.get('/api/instrument/')
        data = response_results(r)
        assert len(data) == 10

        instrument_id_to_delete = instruments[3].id
        self.client.delete(f'/api/instrument/{instrument_id_to_delete}/')

        r = self.client.get('/api/instrument/')
        data = response_results(r)
        assert len(data) == 9
        assert instrument_id_to_delete not in [i['id'] for i in data]

    def test_update(self):
        instruments = baker.make(Instrument, 10)
        instrument: Instrument = instruments[3]

        r = self.client.get(f'/api/instrument/{instrument.id}/')
        data = r.json()
        assert data['ticker'] == instrument.ticker

        r = self.client.put(f'/api/instrument/{instrument.id}/', {
            'ticker': 'NEWTICKER',
            'name': instrument.name,
            'instrument_type': instrument.instrument_type.id,
        })
        assert r.status_code == 200
        r = self.client.get(f'/api/instrument/{instrument.id}/')
        data = r.json()
        assert data['ticker'] == 'NEWTICKER'

        instrument.refresh_from_db()
        assert data['ticker'] == instrument.ticker


class PortfolioViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = baker.make('auth.User')
        authenticate_with_otp(self.client, self.user)

    def test_get_list(self):
        portfolio = baker.make(Portfolio, user=self.user)
        r = self.client.get('/api/portfolio/')
        data = response_results(r)
        assert len(data) == 1
        assert data[0]['name'] == portfolio.name

    def test_create(self):
        r = self.client.post('/api/portfolio/', {'name': 'test2'})

        new_id = r.json()['id']
        assert Portfolio.objects.count() == 1
        new_portfolio = Portfolio.objects.get(id=new_id)
        assert new_portfolio.name == 'test2'
        assert new_portfolio.balance == 0
        assert new_portfolio.user == self.user

    def test_stats(self):
        portfolio = baker.make(Portfolio, user=self.user, balance=1000)
        instrument = baker.make(Instrument, current_price=20)
        baker.make(
            Position,
            portfolio=portfolio,
            instrument=instrument,
            quantity=3,
            average_price=10,
        )

        r = self.client.get('/api/portfolio/stats/')
        data = r.json()

        assert r.status_code == 200
        assert data['count'] == 1
        assert data['balance'] == 1000
        assert data['positionsValue'] == 60
        assert data['totalValue'] == 1060
        assert data['profit'] == 30
        assert data['positionsCount'] == 1

    def test_delete(self):
        portfolios = baker.make(Portfolio, user=self.user, _quantity=10)
        r = self.client.get('/api/portfolio/')
        data = response_results(r)
        assert len(data) == 10

        portfolio_id_to_delete = portfolios[3].id
        self.client.delete(f'/api/portfolio/{portfolio_id_to_delete}/')

        r = self.client.get('/api/portfolio/')
        data = response_results(r)
        assert len(data) == 9
        assert portfolio_id_to_delete not in [i['id'] for i in data]

    def test_update(self):
        portfolios = baker.make(Portfolio, user=self.user, _quantity=10)
        portfolio: Portfolio = portfolios[3]

        r = self.client.get(f'/api/portfolio/{portfolio.id}/')
        data = r.json()
        assert data['name'] == portfolio.name

        r = self.client.put(f'/api/portfolio/{portfolio.id}/', {
            'name': 'test2',
        })
        assert r.status_code == 200
        r = self.client.get(f'/api/portfolio/{portfolio.id}/')
        data = r.json()
        assert data['name'] == 'test2'

        portfolio.refresh_from_db()
        assert data['name'] == portfolio.name


class PositionViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = baker.make('auth.User')
        self.client.force_authenticate(user=self.user)

    def test_get_list(self):
        portfolio = baker.make(Portfolio, user=self.user)
        position = baker.make(Position, portfolio=portfolio)
        r = self.client.get('/api/position/')
        data = response_results(r)
        assert len(data) == 1
        assert data[0]['id'] == position.id

    def test_get_detail(self):
        portfolio = baker.make(Portfolio, user=self.user)
        positions = baker.make(Position, portfolio=portfolio, _quantity=10)
        position: Position = positions[3]

        r = self.client.get(f'/api/position/{position.id}/')
        data = r.json()
        assert data['id'] == position.id
        assert data['portfolio'] == position.portfolio.id
        assert data['instrument'] == position.instrument.id

    def test_create(self):
        r = self.client.post('/api/position/', {})
        assert r.status_code == 405
        assert Position.objects.count() == 0


class PriceHistoryViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = baker.make('auth.User')
        self.client.force_authenticate(user=self.user)

    def test_get_list(self):
        instrument = baker.make(Instrument)
        PriceHistory.objects.all().delete()
        price_history = baker.make(PriceHistory, instrument=instrument)

        r = self.client.get('/api/pricehistory/')
        data = response_results(r)
        assert len(data) == 1
        assert data[0]['id'] == price_history.id

    def test_get_detail(self):
        instrument = baker.make(Instrument)
        history = baker.make(PriceHistory, instrument=instrument, _quantity=10)
        record: PriceHistory = history[3]

        r = self.client.get(f'/api/pricehistory/{record.id}/')
        data = r.json()
        assert data['id'] == record.id
        assert data['instrument'] == record.instrument.id

    def test_create(self):
        r = self.client.post('/api/pricehistory/', {})
        assert r.status_code == 405
        assert PriceHistory.objects.count() == 0

    def test_stats(self):
        instrument = baker.make(Instrument)
        PriceHistory.objects.filter(instrument=instrument).delete()
        baker.make(PriceHistory, instrument=instrument, price=10)
        baker.make(PriceHistory, instrument=instrument, price=20)

        r = self.client.get('/api/pricehistory/stats/', {'instrument': instrument.id})
        data = r.json()

        assert r.status_code == 200
        assert data['count'] == 2
        assert float(data['avg']) == 15
        assert float(data['min']) == 10
        assert float(data['max']) == 20
        assert {float(data['first']), float(data['last'])} == {10, 20}


class TradeViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = baker.make('auth.User')
        authenticate_with_otp(self.client, self.user)

    def test_get_list(self):
        portfolio = baker.make(Portfolio, user=self.user)
        trade = baker.make(Trade, portfolio=portfolio)
        r = self.client.get('/api/trade/')
        data = response_results(r)
        assert len(data) == 1
        assert data[0]['id'] == trade.id

    def test_create_market_buy(self):
        portfolio = baker.make(Portfolio, user=self.user, balance=1000)
        instrument = baker.make(Instrument, current_price=100)

        r = self.client.post('/api/trade/', {
            'portfolio': portfolio.id,
            'instrument': instrument.id,
            'order_type': 'buy',
            'execution_type': 'market',
            'quantity': 5,
        })

        new_id = r.json()['id']
        assert Trade.objects.count() == 1
        trade = Trade.objects.get(id=new_id)
        assert trade.status == Trade.Status.executed
        assert trade.execution_price == 100

        portfolio.refresh_from_db()
        assert portfolio.balance == 500
        position = Position.objects.get(portfolio=portfolio, instrument=instrument)
        assert position.quantity == 5

    def test_create_limit_pending(self):
        portfolio = baker.make(Portfolio, user=self.user, balance=1000)
        instrument = baker.make(Instrument, current_price=100)

        r = self.client.post('/api/trade/', {
            'portfolio': portfolio.id,
            'instrument': instrument.id,
            'order_type': 'buy',
            'execution_type': 'limit',
            'quantity': 5,
            'price': 80,
        })

        trade = Trade.objects.get(id=r.json()['id'])
        assert trade.status == Trade.Status.pending

        portfolio.refresh_from_db()
        assert portfolio.balance == 1000

    def test_create_not_enough_money(self):
        portfolio = baker.make(Portfolio, user=self.user, balance=100)
        instrument = baker.make(Instrument, current_price=100)

        r = self.client.post('/api/trade/', {
            'portfolio': portfolio.id,
            'instrument': instrument.id,
            'order_type': 'buy',
            'execution_type': 'market',
            'quantity': 5,
        })
        assert r.status_code == 400
        assert 'detail' in r.json()

    def test_delete(self):
        portfolio = baker.make(Portfolio, user=self.user)
        trades = baker.make(Trade, portfolio=portfolio, _quantity=10)
        r = self.client.get('/api/trade/')
        data = response_results(r)
        assert len(data) == 10

        trade_id_to_delete = trades[3].id
        self.client.delete(f'/api/trade/{trade_id_to_delete}/')

        r = self.client.get('/api/trade/')
        data = response_results(r)
        assert len(data) == 9
        assert trade_id_to_delete not in [i['id'] for i in data]