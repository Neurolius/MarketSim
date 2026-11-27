from rest_framework import serializers
from market.models import InstrumentType, Instrument, Portfolio, Position, PriceHistory, Trade, TradeImage

class InstrumentTypeSerializer(serializers.ModelSerializer):
    instruments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = InstrumentType
        fields = ['id', 'name', 'instruments_count']

class InstrumentSerializer(serializers.ModelSerializer):
    prev_price = serializers.DecimalField(max_digits=15, decimal_places=4, read_only=True, allow_null=True)
    price_updated_at = serializers.DateTimeField(read_only=True, allow_null=True)
    change_percent = serializers.FloatField(read_only=True)
    instrument_type_name = serializers.CharField(
        source="instrument_type.name", read_only=True
    )
    
    class Meta:
        model = Instrument
        fields = ['id', 'ticker', 'name', 
                  'instrument_type', 'current_price', 'logo', 
                  'prev_price', 'price_updated_at',
                  'change_percent','instrument_type_name']

class PortfolioSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    positions_count = serializers.IntegerField(read_only=True, default=0)
    positions_value = serializers.DecimalField(
        max_digits=30, decimal_places=4, read_only=True, default=0
    )
    positions_cost = serializers.DecimalField(
        max_digits=30, decimal_places=4, read_only=True, default=0
    )
    total_value = serializers.DecimalField(
        max_digits=30, decimal_places=4, read_only=True
    )
    
    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('balance', None)
        return super().update(instance, validated_data)

    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("Баланс не может быть отрицательным")
        return value

    class Meta:
        model = Portfolio
        fields = [
            'id', 'name', 'user', 'user_name', 'balance', 'cover_image',
            'positions_count', 'positions_value', 'positions_cost', 'total_value'
        ]
        read_only_fields = ['user']


class PositionSerializer(serializers.ModelSerializer):
    instrument_info = InstrumentSerializer(source='instrument', read_only=True)
    position_value = serializers.DecimalField(
        max_digits=30, decimal_places=8, read_only=True
    )
    position_profit = serializers.DecimalField(
        max_digits=30, decimal_places=8, read_only=True
    )

    class Meta:
        model = Position
        fields = ['id', 'portfolio', 'instrument', 
                  'instrument_info', 'quantity', 
                  'average_price','position_value','position_profit']
        read_only_fields = ['portfolio', 'instrument', 'quantity', 'average_price']


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['id', 'instrument', 'price', 'timestamp']
        read_only_fields = ['instrument', 'price', 'timestamp']


class TradeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeImage
        fields = ['id', 'image']


class TradeSerializer(serializers.ModelSerializer):
    instrument_info = InstrumentSerializer(source='instrument', read_only=True)
    portfolio_name = serializers.CharField(source='portfolio.name', read_only=True)
    images = TradeImageSerializer(many=True, read_only=True)
    new_images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True,
    )
    total_amount = serializers.DecimalField(
        max_digits=30, decimal_places=8, read_only=True
    )

    class Meta:
        model = Trade
        fields = ['id', 'portfolio', 'portfolio_name', 'instrument', 'instrument_info', 'order_type',
                  'execution_type', 'quantity', 'price', 'status',
                  'execution_price', 'total_amount', 'created_at', 
                  'executed_at', 'images', 'new_images']
        read_only_fields = ['execution_price', 'status', 'created_at', 'executed_at']

    def create(self, validated_data):
        images = validated_data.pop('new_images', [])
        trade = super().create(validated_data)
        for image in images:
            TradeImage.objects.create(trade=trade, image=image)
        return trade

    def validate(self, data):
        request = self.context.get('request')
        if (
            request
            and not request.user.is_superuser
            and data['portfolio'].user_id != request.user.id
        ):
            raise serializers.ValidationError({'portfolio': 'Это портфель другого пользователя.'})
        if data['quantity'] <= 0:
            raise serializers.ValidationError({'quantity': 'Количество должно быть положительным числом.'})
        if data['execution_type'] == Trade.ExecutionType.limit:
            if not data.get('price') or data['price'] <= 0:
                raise serializers.ValidationError({'price': 'Укажите положительную цену для лимитного заказа.'})
        else:
            data['price'] = None
        return data

class TradeUpdateSerializer(serializers.ModelSerializer):
    new_images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Trade
        fields = ['quantity', 'price', 'new_images']

    def update(self, instance, validated_data):
        images = validated_data.pop('new_images', [])
        trade = super().update(instance, validated_data)
        for image in images:
            TradeImage.objects.create(trade=trade, image=image)
        return trade

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Количество должно быть больше нуля')
        return value

    def validate_price(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError('Укажите положительную лимитную цену')
        return value