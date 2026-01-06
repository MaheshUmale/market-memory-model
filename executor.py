import pandas as pd

class Executor:
    def __init__(self, initial_capital=100000):
        self.capital = initial_capital
        self.position = None  # None, 'LONG', or 'SHORT'
        self.entry_price = 0
        self.stop_loss = 0
        self.trades = []

    def execute_trade(self, signal, current_price, stop_loss):
        # Close existing position if a new signal is received
        if self.position and signal != 'HOLD':
            self._close_position(current_price)

        if signal == 'BUY' and not self.position:
            self.position = 'LONG'
            self.entry_price = current_price
            self.stop_loss = stop_loss
            print(f"Executed BUY at {current_price}, Stop Loss: {stop_loss}")
            self._log_trade('BUY', current_price)

        elif signal == 'SELL' and not self.position:
            self.position = 'SHORT'
            self.entry_price = current_price
            self.stop_loss = stop_loss
            print(f"Executed SELL at {current_price}, Stop Loss: {stop_loss}")
            self._log_trade('SELL', current_price)

    def check_stop_loss(self, current_price):
        if self.position == 'LONG' and current_price <= self.stop_loss:
            print(f"Stop loss triggered for LONG position at {current_price}")
            self._close_position(current_price)
        elif self.position == 'SHORT' and current_price >= self.stop_loss:
            print(f"Stop loss triggered for SHORT position at {current_price}")
            self._close_position(current_price)

    def _close_position(self, exit_price):
        if self.position == 'LONG':
            pnl = exit_price - self.entry_price
        elif self.position == 'SHORT':
            pnl = self.entry_price - exit_price
        else:
            pnl = 0

        self.capital += pnl
        self._log_trade('CLOSE', exit_price, pnl)
        print(f"Closed {self.position} position at {exit_price}. PnL: {pnl:.2f}. Capital: {self.capital:.2f}")

        self.position = None
        self.entry_price = 0
        self.stop_loss = 0

    def _log_trade(self, trade_type, price, pnl=0):
        self.trades.append({
            'type': trade_type,
            'price': price,
            'pnl': pnl,
            'capital': self.capital,
            'timestamp': pd.Timestamp.now()
        })

    def get_portfolio_status(self):
        return {
            'capital': self.capital,
            'position': self.position,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss
        }

    def get_trade_history(self):
        return pd.DataFrame(self.trades)

if __name__ == '__main__':
    # Example Usage
    executor = Executor()

    # Simulate a successful long trade
    executor.execute_trade('BUY', 100, 95)
    executor.check_stop_loss(102) # No stop loss
    executor.execute_trade('SELL', 105, 110) # Close long, open short

    # Simulate a short trade with stop loss
    executor.check_stop_loss(108) # Stop loss triggered

    print("\nTrade History:")
    print(executor.get_trade_history())

    print("\nFinal Portfolio Status:")
    print(executor.get_portfolio_status())
