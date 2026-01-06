from backtester import Backtester
from datetime import datetime, timedelta

def main():
    """
    Main entry point for running the backtester.
    """
    today = datetime.now()
    # To ensure we get a full day of trading, we backtest on the previous day's data.
    yesterday = today - timedelta(days=1)
    day_before_yesterday = yesterday - timedelta(days=1)

    backtester = Backtester(
        symbol='SBIN.NS',  # Example: State Bank of India on the National Stock Exchange
        start_date=day_before_yesterday,
        end_date=yesterday
    )

    print(f"Running backtest for {backtester.symbol} from {backtester.start_date.date()} to {backtester.end_date.date()}...")
    backtester.run()
    print("Backtest finished.")

if __name__ == '__main__':
    main()
