from django.test import TestCase
from rest_framework.test import APIClient
from model_bakery import baker
from market.models import InstrumentType, Instrument, Portfolio, Position, PriceHistory, Trade


class InstrumentTypeViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        instr_type = baker.make(InstrumentType)
        r = self.client.get('/api/instrumenttype/')
        data = r.json()
        assert len(data) == 1
        assert data[0]['name'] == instr_type.name

    def test_create(self):
        r = self.client.post('/api/instrumenttype/', {'name': 'test2'})

        new_id = r.json()['id']
        assert InstrumentType.objects.count() == 1
        assert InstrumentType.objects.get(id=new_id).name == 'test2'

    def test_delete(self):
        instr_types = baker.make(InstrumentType, 10)
        r = self.client.get('/api/instrumenttype/')
        data = r.json()
        assert len(data) == 10

        instr_type_id_to_delete = instr_types[3].id
        self.client.delete(f'/api/instrumenttype/{instr_type_id_to_delete}/')

        r = self.client.get('/api/instrumenttype/')
        data = r.json()
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

    def test_get_list(self):
        instrument = baker.make(Instrument)
        r = self.client.get('/api/instrument/')
        data = r.json()
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

    def test_delete(self):
        instruments = baker.make(Instrument, 10)
        r = self.client.get('/api/instrument/')
        data = r.json()
        assert len(data) == 10

        instrument_id_to_delete = instruments[3].id
        self.client.delete(f'/api/instrument/{instrument_id_to_delete}/')

        r = self.client.get('/api/instrument/')
        data = r.json()
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

    def test_get_list(self):
        portfolio = baker.make(Portfolio)
        r = self.client.get('/api/portfolio/')
        data = r.json()
        assert len(data) == 1
        assert data[0]['name'] == portfolio.name

    def test_create(self):
        user = baker.make('auth.User')
        r = self.client.post('/api/portfolio/', {'name': 'test2', 'user': user.id})

        new_id = r.json()['id']
        assert Portfolio.objects.count() == 1
        new_portfolio = Portfolio.objects.get(id=new_id)
        assert new_portfolio.name == 'test2'
        assert new_portfolio.balance == 0

    def test_delete(self):
        portfolios = baker.make(Portfolio, 10)
        r = self.client.get('/api/portfolio/')
        data = r.json()
        assert len(data) == 10

        portfolio_id_to_delete = portfolios[3].id
        self.client.delete(f'/api/portfolio/{portfolio_id_to_delete}/')

        r = self.client.get('/api/portfolio/')
        data = r.json()
        assert len(data) == 9

        assert portfolio_id_to_delete not in [i['id'] for i in data]

    def test_update(self):
        portfolios = baker.make(Portfolio, 10)
        portfolio: Portfolio = portfolios[3]

        r = self.client.get(f'/api/portfolio/{portfolio.id}/')
        data = r.json()
        assert data['name'] == portfolio.name

        r = self.client.put(f'/api/portfolio/{portfolio.id}/', {
            'name': 'test2',
            'user': portfolio.user.id,
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

    def test_get_list(self):
        position = baker.make(Position)
        r = self.client.get('/api/position/')
        data = r.json()
        assert len(data) == 1
        assert data[0]['id'] == position.id

    def test_get_detail(self):
        positions = baker.make(Position, 10)
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

    def test_get_list(self):
        price_history = baker.make(PriceHistory)
        r = self.client.get('/api/pricehistory/')
        data = r.json()
        assert len(data) == 1
        assert data[0]['id'] == price_history.id

    def test_get_detail(self):
        history = baker.make(PriceHistory, 10)
        record: PriceHistory = history[3]

        r = self.client.get(f'/api/pricehistory/{record.id}/')
        data = r.json()
        assert data['id'] == record.id
        assert data['instrument'] == record.instrument.id

    def test_create(self):
        r = self.client.post('/api/pricehistory/', {})
        assert r.status_code == 405
        assert PriceHistory.objects.count() == 0


class TradeViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        trade = baker.make(Trade)
        r = self.client.get('/api/trade/')
        data = r.json()
        assert len(data) == 1
        assert data[0]['id'] == trade.id

    def test_create_market_buy(self):
        portfolio = baker.make(Portfolio, balance=1000)
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
        portfolio = baker.make(Portfolio, balance=1000)
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
        portfolio = baker.make(Portfolio, balance=100)
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
        trades = baker.make(Trade, 10)
        r = self.client.get('/api/trade/')
        data = r.json()
        assert len(data) == 10

        trade_id_to_delete = trades[3].id
        self.client.delete(f'/api/trade/{trade_id_to_delete}/')

        r = self.client.get('/api/trade/')
        data = r.json()
        assert len(data) == 9

        assert trade_id_to_delete not in [i['id'] for i in data]