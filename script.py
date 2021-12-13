#!/usr/bin/python

import datetime
import os
import sys

from ccxt.gooplex import gooplex


def since():
    last_month = datetime.date.today() - datetime.timedelta(days = 30)
    since = os.environ.get('SINCE', last_month.strftime('%Y-%m-%d'))
    print('Data from {}'.format(since),
          file=sys.stderr)

    frags = since.split('-')
    year = int(frags[0])
    month = int(frags[1])
    day = int(frags[2])

    timestamp = datetime.datetime(year, month, day, 0, 0, 0)
    return int(timestamp.timestamp() * 1000)    # millis


def contains():
    contains = os.environ.get('SYMBOLS', 'usdt,btc')
    print('Should contain the symbols {}'.format(contains),
          file=sys.stderr)
    return contains.split(',')


def build_results_for_symbol(data, buy, sell):
    result = {}
    for entry in data:
        (timestamp, _open, _high, _low, close, _volume) = entry

        date = datetime.datetime\
            .fromtimestamp(timestamp / 1000)\
            .strftime('%Y-%m-%d')

        if date not in result:
            result[date] = {}

        print('\t{date}/{sell} = {close}'.format(
            date=date,
            sell=sell,
            close=close),
              file=sys.stderr)
        result[date][sell] = close
    return result


def load_market(since, contains):
    conn = gooplex()
    market = conn.load_markets()
    result = {}

    for symbol in market.keys():
        (buy, sell) = symbol.split('/')
        sell = sell.lower()

        if sell not in contains:
            print('(Ignoring {})'.format(symbol),
                  file=sys.stderr)
            continue

        print('OHLCV of {}'.format(symbol),
              file=sys.stderr)
        ohlcv = conn.fetch_ohlcv(symbol,
                                 since=since,
                                 limit=100_000,
                                 timeframe='1d')
        result[buy] = build_results_for_symbol(ohlcv, buy, sell)

        if len(result) > 3:
            break
    return result


def export(results):
    for (symbol, symbol_dates) in results.items():
        for (date, values) in symbol_dates.items():
            print('{symbol}\t'
                  '{date}\t'
                  '{usdt:.8f}\t'
                  '{btc:.8f}\n'.format(
                      symbol=symbol,
                      date=date,
                      usdt=(values['usdt']
                            if 'usdt' in values
                            else 0),
                      btc=(values['btc']
                           if 'btc' in values
                           else 0)))


def main():
    timestamp = since()
    symbols = contains()
    data = load_market(timestamp, symbols)
    export(data)


if __name__ == '__main__':
    main()
