# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
import base64
from ccxt.base.errors import ExchangeError


class coinfloor (Exchange):

    def describe(self):
        return self.deep_extend(super(coinfloor, self).describe(), {
            'id': 'coinfloor',
            'name': 'coinfloor',
            'rateLimit': 1000,
            'countries': 'UK',
            'has': {
                'CORS': False,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28246081-623fc164-6a1c-11e7-913f-bac0d5576c90.jpg',
                'api': 'https://webapi.coinfloor.co.uk:8090/bist',
                'www': 'https://www.coinfloor.co.uk',
                'doc': [
                    'https://github.com/coinfloor/api',
                    'https://www.coinfloor.co.uk/api',
                ],
            },
            'requiredCredentials': {
                'apiKey': True,
                'secret': False,
                'password': True,
                'uid': True,
            },
            'api': {
                'public': {
                    'get': [
                        '{id}/ticker/',
                        '{id}/order_book/',
                        '{id}/transactions/',
                    ],
                },
                'private': {
                    'post': [
                        '{id}/balance/',
                        '{id}/user_transactions/',
                        '{id}/open_orders/',
                        '{id}/cancel_order/',
                        '{id}/buy/',
                        '{id}/sell/',
                        '{id}/buy_market/',
                        '{id}/sell_market/',
                        '{id}/estimate_sell_market/',
                        '{id}/estimate_buy_market/',
                    ],
                },
            },
            'markets': {
                'BTC/GBP': {'id': 'XBT/GBP', 'symbol': 'BTC/GBP', 'base': 'BTC', 'quote': 'GBP'},
                'BTC/EUR': {'id': 'XBT/EUR', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
                'BTC/USD': {'id': 'XBT/USD', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD'},
                'BTC/PLN': {'id': 'XBT/PLN', 'symbol': 'BTC/PLN', 'base': 'BTC', 'quote': 'PLN'},
                'BCH/GBP': {'id': 'BCH/GBP', 'symbol': 'BCH/GBP', 'base': 'BCH', 'quote': 'GBP'},
            },
        })

    def fetch_balance(self, params={}):
        symbols = None
        if 'symbol' in params:
            symbols = [params['symbol']]
        elif 'id' in params:
            symbols = [params['id']]
        else:
            symbols = self.markets

        balances = {
            'info': []
        }
        for symbol in symbols:
            market = self.market(symbol)
            id = market['id']
            base = market['base']
            quote = market['quote']

            resp = self.privatePostIdBalance({
                'id': id,
            })
            balances['info'].append(resp)

            if 'free' not in balances:
                balances['free'] = {}
                balances['used'] = {}
                balances['total'] = {}

            base_key, quote_key = id.lower().split('/')
            balances['free'][base] = resp[base_key+'_available']
            balances['free'][quote] = resp[quote_key + '_available']
            balances['used'][base] = resp[base_key + '_reserved']
            balances['used'][quote] = resp[quote_key + '_reserved']
            balances['total'][base] = resp[base_key + '_balance']
            balances['total'][quote] = resp[quote_key + '_balance']

            balances[base] = {
                'free': balances['free'][base],
                'used': balances['used'][base],
                'total': balances['total'][base]
            }
            balances[quote] = {
                'free': balances['free'][quote],
                'used': balances['used'][quote],
                'total': balances['total'][quote]
            }
        return balances



    def fetch_order_book(self, symbol, limit=None, params={}):
        orderbook = self.publicGetIdOrderBook(self.extend({
            'id': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook)

    def parse_ticker(self, ticker, market=None):
        # rewrite to get the timestamp from HTTP headers
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        vwap = self.safe_float(ticker, 'vwap')
        baseVolume = float(ticker['volume'])
        quoteVolume = None
        if vwap is not None:
            quoteVolume = baseVolume * vwap
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': vwap,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': baseVolume,
            'quoteVolume': quoteVolume,
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        market = self.market(symbol)
        ticker = self.publicGetIdTicker(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market):
        timestamp = trade['date'] * 1000
        return {
            'info': trade,
            'id': str(trade['tid']),
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': None,
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        market = self.market(symbol)
        response = self.publicGetIdTransactions(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_trades(response, market, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        order = {'id': self.market_id(symbol)}
        method = 'privatePostId' + self.capitalize(side)
        if type == 'market':
            order['quantity'] = amount
            method += 'Market'
        else:
            order['price'] = price
            order['amount'] = amount
        return getattr(self, method)(self.extend(order, params))

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostIdCancelOrder({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        # curl -k -u '[User ID]/[API key]:[Passphrase]' https://webapi.coinfloor.co.uk:8090/bist/XBT/GBP/balance/
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            nonce = self.nonce()
            body = self.urlencode(self.extend({'nonce': nonce}, query))
            auth = self.uid + '/' + self.apiKey + ':' + self.password
            signature = self.decode(base64.b64encode(self.encode(auth)))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + signature,
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
