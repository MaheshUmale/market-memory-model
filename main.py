from backtester import Backtester
from datetime import datetime, timedelta

def main():
    """
    Main entry point for running the backtester for Nifty and BankNifty.
    """
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    day_before_yesterday = yesterday - timedelta(days=1)

    indices = {
        'Nifty': '^NSEI',
        'BankNifty': '^NSEBANK'
    }

    for name, symbol in indices.items():
        output_filename = f"{name.lower()}_trade_log.csv"

        backtester = Backtester(
            symbol=symbol,
            start_date=day_before_yesterday,
            end_date=yesterday,
            output_filename=output_filename
        )

        print(f"--- Running backtest for {name} ({symbol}) ---")
        backtester.run()
        print(f"--- Backtest for {name} finished. Log saved to {output_filename} ---")

if __name__ == '__main__':
    main()
