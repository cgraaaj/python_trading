import pandas as pd


def wwma(values, n):
    return values.ewm(alpha=1 / n, min_periods=n, adjust=False).mean()


def atr(df, n=20):
    data = df.copy()
    high = data["High"]
    low = data["Low"]
    close = data["Close"]
    data["tr0"] = abs(high - low)
    data["tr1"] = abs(high - close.shift())
    data["tr2"] = abs(low - close.shift())
    tr = data[["tr0", "tr1", "tr2"]].max(axis=1)
    atr = self.wwma(tr, n)
    return atr
