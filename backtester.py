import yfinance as yf
import pandas as pd
from signal_generator import SignalGenerator
from executor import Executor
from datetime import datetime, timedelta

class Backtester:
    def __init__(self, symbol, start_date, end_date):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date

    def get_last_trading_day(self, date):
        """
        Gets the last valid trading day by fetching data until a non-empty DataFrame is returned.
        """
        offset = 1
        while True:
            current_date = date - timedelta(days=offset)
            data = yf.download(self.symbol, start=current_date - timedelta(days=1), end=current_date, interval="1d")
            if not data.empty:
                return data
            offset += 1
            if offset > 10: # Safety break to prevent infinite loops
                return None

    def run(self):
        # Fetch data for the day before the start date to get the previous day's high and low
        previous_day_data = self.get_last_trading_day(self.start_date)

        if previous_day_data is None or previous_day_data.empty:
            print("Could not fetch previous day's data.")
            return

        try:
            # Flatten multi-index columns if they exist
            if isinstance(previous_day_data.columns, pd.MultiIndex):
                previous_day_data.columns = previous_day_data.columns.get_level_values(0)

            # yfinance column names are capitalized, so we need to adjust
            previous_day_data.rename(columns={
                'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
            }, inplace=True)

            # Fetch intraday data for the backtesting period
            intraday_data = yf.download(
                self.symbol,
                start=self.start_date,
                end=self.end_date,
                interval="1m"
            )
            if intraday_data.empty:
                print("No intraday data for the selected date. It might be a weekend or holiday.")
                return

            if isinstance(intraday_data.columns, pd.MultiIndex):
                intraday_data.columns = intraday_data.columns.get_level_values(0)

            intraday_data.rename(columns={
                'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'
            }, inplace=True)

        except Exception as e:
            print(f"Error processing data: {e}")
            return

        signal_generator = SignalGenerator(previous_day_data)
        executor = Executor()

        for index, row in intraday_data.iterrows():
            candle = {
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume']
            }

            # Check for stop loss first
            executor.check_stop_loss(candle['close'])

            # Process candle for signals
            signal = signal_generator.process_candle(candle)

            if signal['signal'] != 'HOLD':
                executor.execute_trade(signal['signal'], signal['price'], signal['stop_loss'])

        # Final portfolio status
        print("\nBacktest Complete.")
        print("Trade History:")
        print(executor.get_trade_history())
        print("\nFinal Portfolio Status:")
        print(executor.get_portfolio_status())

        # Save the trade history to a CSV file
        executor.save_trade_history_to_csv('trade_log.csv')

if __name__ == '__main__':
    # Example usage for today's data
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    backtester = Backtester(
        symbol='SBIN.NS', # Use the .NS suffix for NSE stocks
        start_date=yesterday,
        end_date=today
    )
    backtester.run()
