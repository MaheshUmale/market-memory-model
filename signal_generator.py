import pandas as pd

class SignalGenerator:
    def __init__(self, previous_day_data: pd.DataFrame):
        # Extract the scalar value using .values[0]
        self.previous_day_high = previous_day_data['high'].values[0]
        self.previous_day_low = previous_day_data['low'].values[0]
        self.john_wick_candle = None
        print(f"Key levels set: High={self.previous_day_high}, Low={self.previous_day_low}")

    def is_john_wick_candle(self, candle):
        """
        Identifies a John Wick Candle pattern.
        A JWC has a long wick and a small body, indicating a rejection of a price level.
        """
        body_size = abs(candle['open'] - candle['close'])
        total_range = candle['high'] - candle['low']

        if total_range == 0:
            return None

        # Simplified definition: Body is less than 30% of the total range
        if body_size / total_range < 0.3:
            upper_wick = candle['high'] - max(candle['open'], candle['close'])
            lower_wick = min(candle['open'], candle['close']) - candle['low']

            # Bearish JWC: Long upper wick at resistance
            if upper_wick > lower_wick and upper_wick / total_range > 0.5:
                # Check if price is near the previous day's high
                if abs(candle['high'] - self.previous_day_high) / self.previous_day_high < 0.005:
                    return 'BEARISH'

            # Bullish JWC: Long lower wick at support
            elif lower_wick > upper_wick and lower_wick / total_range > 0.5:
                # Check if price is near the previous day's low
                if abs(candle['low'] - self.previous_day_low) / self.previous_day_low < 0.005:
                    return 'BULLISH'

        return None

    def process_candle(self, candle):
        """
        Processes a new candle to generate a trading signal.
        """
        if self.john_wick_candle:
            # Entry logic: trade on the break of the JWC
            if self.john_wick_candle['type'] == 'BEARISH' and candle['close'] < self.john_wick_candle['low']:
                signal = {'signal': 'SELL', 'price': candle['close'], 'stop_loss': self.john_wick_candle['high']}
                self.john_wick_candle = None # Reset after signal
                return signal

            if self.john_wick_candle['type'] == 'BULLISH' and candle['close'] > self.john_wick_candle['high']:
                signal = {'signal': 'BUY', 'price': candle['close'], 'stop_loss': self.john_wick_candle['low']}
                self.john_wick_candle = None # Reset after signal
                return signal

        jwc_type = self.is_john_wick_candle(candle)
        if jwc_type:
            print(f"John Wick Candle detected: {jwc_type} at {candle['close']}")
            self.john_wick_candle = {
                'type': jwc_type,
                'high': candle['high'],
                'low': candle['low'],
                'close': candle['close']
            }

        return {'signal': 'HOLD'}

if __name__ == '__main__':
    # Example usage for testing
    # Create sample previous day data
    data = {'high': [105], 'low': [95], 'open': [100], 'close': [102]}
    previous_day = pd.DataFrame(data)

    signal_gen = SignalGenerator(previous_day)

    # Test candles
    # 1. Bearish JWC near previous day high
    test_candle_1 = {'open': 104.5, 'high': 105.5, 'low': 104, 'close': 104.2}
    print(f"Processing candle 1: {signal_gen.process_candle(test_candle_1)}")

    # 2. Break of the JWC low
    test_candle_2 = {'open': 104, 'high': 104.1, 'low': 103.8, 'close': 103.9}
    print(f"Processing candle 2: {signal_gen.process_candle(test_candle_2)}")

    # 3. Bullish JWC near previous day low
    signal_gen.john_wick_candle = None # Reset
    test_candle_3 = {'open': 95.5, 'high': 96, 'low': 94.8, 'close': 95.8}
    print(f"Processing candle 3: {signal_gen.process_candle(test_candle_3)}")

    # 4. Break of the JWC high
    test_candle_4 = {'open': 95.9, 'high': 96.2, 'low': 95.8, 'close': 96.1}
    print(f"Processing candle 4: {signal_gen.process_candle(test_candle_4)}")
