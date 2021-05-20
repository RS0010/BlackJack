from random import randint
from json import dumps, load, decoder
from copy import deepcopy
from hashlib import sha256
from time import time

DEALER = 0
PLAYER = 1

BUSTS = 0
FIVE = 1
WIN = 2
LOSE = 3
PLAYER_BLACKJACK = 5
DEALER_BLACKJACK = 6
DEUCE = 7
CONTINUE = 8

STAND = 0
HIT = 1
FIRST = 2
SPLIT = 3
INSURANCE = 4
DOUBLE = 5
SURRENDER = 6

HANDLE = 0
USER = 1
FUNCTION = 2


class BlackJack:
    class __Information:
        class __Get:
            def __init__(self, info):  # todo: 将Information导入，以使用文件名。
                self.__info = info
                self.__game = 0

            def __call__(self, info):  # todo: 导入文件，在每次写入后调用此函数，写入发生位置有：insert， information __init__
                self.__data = load(info)['games']

        class __Insert:
            def __init__(self, info, get):
                self.__info = info
                self.__get = get
                self.__game = deepcopy(self.__info.TEMPLATE_GAME)
                self.__game['salt'] = randint(1, 10 ** self.__info.SALT_COMPLEXITY)

            def __call__(self, *args, **kwargs):
                with open(self.__info.FILE_NAME, 'r') as file_read:
                    info = load(file_read)
                    self.__game['money']['player'] += info['games'][-1]['money']['player']
                    self.__game['money']['dealer'] += info['games'][-1]['money']['dealer']
                    info['games'].append(self.__game)
                    _hash = deepcopy(self.__info.TEMPLATE_HASH)
                    _hash['data'] = sha256(bytes(dumps(self.__game), encoding='utf8')).hexdigest()
                    _hash['chain'] = sha256(bytes(dumps(info['hash'][-1]), encoding='utf8')).hexdigest()
                    info['hash'].append(_hash)
                    info['verification'] = sha256(bytes(dumps(_hash), encoding='utf8')).hexdigest()
                    with open(self.__info.FILE_NAME, 'w') as file_write:
                        file_write.write(dumps(info, indent=2))
                self.__get(info)
                self.__game.clear()
                self.__game = deepcopy(self.__info.TEMPLATE_GAME)
                self.__game['salt'] = randint(1, 10 ** self.__info.SALT_COMPLEXITY)

            @property
            def wager(self):
                return

            @wager.setter
            def wager(self, value):
                self.__game['money']['wager'] = value

            @property
            def change(self):
                return

            @change.setter
            def change(self, value):
                self.__game['money']['player'] += value
                self.__game['money']['dealer'] -= value

            def record(self, operation, layer=None, value=None):
                record = {"operation": operation, "layer": layer}
                if operation == 'Draw':
                    record['card'] = value % 13 + 1
                elif operation == 'Split':
                    record['new layer'] = value
                elif operation == 'Insurance':
                    del record['layer']
                self.__game["records"].append(deepcopy(record))

        SALT_COMPLEXITY = 4
        FILE_NAME = 'log.json'
        TEMPLATE_INFO = {"verification": None, "games": [], "hash": []}
        TEMPLATE_GAME = {"money": {"wager": None, "player": 0, "dealer": 0}, "records": [], "salt": None}
        TEMPLATE_RECORD = {"layer": None, "operation": None, "card": None}
        TEMPLATE_HASH = {"data": None, "chain": None}
        base_money_player = 10000
        base_money_dealer = 100000

        def __init__(self):
            self.get = self.__Get(self)
            self.insert = self.__Insert(self, self.get)
            with open(self.FILE_NAME, 'r') as file_read:
                try:
                    info = load(file_read)
                except decoder.JSONDecodeError:
                    info = self.start()
                if info:
                    self.check(info)
                self.get(info)

        def start(self):
            info = deepcopy(self.TEMPLATE_INFO)
            info['games'].append(deepcopy(self.TEMPLATE_GAME))
            info['games'][-1]['money']['player'] = self.base_money_player
            info['games'][-1]['money']['dealer'] = self.base_money_dealer
            info['games'][-1]['salt'] = randint(1, 10 ** self.SALT_COMPLEXITY)
            info['hash'].append(deepcopy(self.TEMPLATE_HASH))
            info['hash'][-1]['data'] = sha256(bytes(dumps(info['games'][-1]), encoding='utf8')).hexdigest()
            info['hash'][-1]['chain'] = sha256(bytes(str(randint(1, 10 ** self.SALT_COMPLEXITY)), encoding='utf8')).hexdigest()
            info['verification'] = sha256(bytes(dumps(info['hash'][-1]), encoding='utf8')).hexdigest()
            with open(self.FILE_NAME, 'w') as file_write:
                file_write.write(dumps(info, indent=2))
            return info

        @staticmethod
        def check(data):
            verification_calculate = sha256(bytes(dumps(data['hash'][-1]), encoding='utf8')).hexdigest()
            verification_store = data['verification']
            if verification_calculate != verification_store:
                raise ValueError('Chain Verification failed1!!!')
            data_hash_calculate = sha256(bytes(dumps(data['games'][-1]), encoding='utf8')).hexdigest()
            data_hash_store = data['hash'][-1]['data']
            if data_hash_calculate != data_hash_store:
                raise ValueError('Data Verification Failed!!!')

        @property
        def money(self):
            return

        @money.setter
        def money(self, value):
            self.base_money_player = value

    class __CardPile:
        __card_pile = {DEALER: [], PLAYER: []}

        def __init__(self, _deck_amount, info):
            if _deck_amount <= 0:
                raise ValueError('deck_amount <= 0')
            self.__DECK_AMOUNT = _deck_amount
            self.__info = info

        def init(self):
            self.__info.insert.cards = self.__card_pile
            self.__card_pile.clear()
            self.__card_pile = {DEALER: [], PLAYER: []}

        def draw(self, user):
            card = randint(0, 52 * self.__DECK_AMOUNT - 1)
            if card in self.__card_pile[DEALER] or card in self.__card_pile[PLAYER]:
                self.draw(user)
            else:
                self.__card_pile[user].append(card)
                return card

        def move(self, user_from, user_to):
            try:
                self.__card_pile[user_to]
            except KeyError:
                self.__card_pile[user_to] = [self.__card_pile[user_from][1]]
                del self.__card_pile[user_from][1]
                return
            raise KeyError('user_to error')

        @property
        def card(self):
            return self.__card_pile

    class __Operation:
        __end = [True, False]

        def __init__(self, pile, info):
            self.__pile = pile
            self.__info = info

        def __init(self):
            self.__pile.init()
            for _ in range(2):
                for user in (PLAYER, DEALER):
                    self.__info.insert.record(layer=user, operation='Deal')
                    self.__draw(user)

        def __cards_sum(self, _user):
            cards = []
            for card in self.__pile.card[_user]:
                points = card % 13 + 1
                points = 10 if points > 10 else points
                cards.append(points)
            _sum = sum(cards)
            _sum += 10 if _sum <= 11 and 1 in cards else 0
            _sum = 0 if _sum > 21 else _sum
            _sum = 22 if len(cards) == 2 and _sum == 21 else _sum
            return _sum

        def __draw(self, user):
            self.__info.insert.record(layer=user, operation='Draw', value=self.__pile.draw(user))

        def __stand_double(self, user):
            dealer = self.__cards_sum(DEALER)
            player = self.__cards_sum(user)
            record = 'Win' if player > dealer else 'Lose' if dealer < player else 'Deuce'
            self.__info.insert.record(layer=user, operation=record)
            self.__end[user] = True
            if False not in self.__end:
                self.__dealer_hit()
            return WIN if player > dealer else LOSE if dealer < player else DEUCE

        def __dealer_hit(self):
            def soft():
                for card in self.__pile.card:
                    if card % 13 == 0:
                        return True
                return False

            def max_player():
                _player = self.__cards_sum(PLAYER)
                for user in range(2, len(self.__pile.card)):
                    _player = max(_player, self.__cards_sum(user))
                return _player

            player = max_player()
            dealer = self.__cards_sum(DEALER)
            while 0 < dealer < max(player, 17) or dealer == 17 and soft():
                self.__info.insert.record(layer=DEALER, operation='Hit')
                self.__draw(DEALER)
                dealer = self.__cards_sum(DEALER)

        def hit(self, user):
            if user < 0:
                raise ValueError('user error')
            self.__info.insert.record(layer=user, operation='Hit')
            self.__draw(user)
            if self.__cards_sum(user) == 0:
                self.__end[user] = True
                return BUSTS
            elif user != DEALER:
                self.__end[user] = True
                return FIVE if len(self.__pile.card[user]) >= 5 else CONTINUE
            else:
                return CONTINUE

        def stand(self, user):
            if user < 0:
                raise ValueError('user error')
            self.__info.insert.record(layer=user, operation='Stand')
            self.__stand_double(user)

        def double(self, user):
            if user < 0:
                raise ValueError('user error')
            self.__info.insert.record(layer=user, operation='Double')
            self.__draw(user)
            self.__stand_double(user)

        def split(self, user_from):
            user_to = len(self.__pile.card)
            self.__pile.move(user_from, user_to)
            self.__info.insert.record(layer=user_from, operation='Split', value=user_to)
            self.__end.append(False)

        def insurance(self):
            self.__info.insert.record(operation='Insurance')
            return True if self.__cards_sum(DEALER) == 22 else False

        def surrender(self):
            pass
        
        @property
        def end(self):
            return False if False in self.__end else True

    class __Get:
        def __init__(self, state):
            self.__state = state

    def __init__(self, _deck_amount):
        self.__info = self.__Information()
        self.__pile = self.__CardPile(_deck_amount, self.__info)
        self.operation = self.__Operation(self.__pile, self.__info)

    # def __cards_sum(self, _user):
    #     _cards = []
    #     for _card in self.cards[_user]:
    #         _points = _card % 13 + 1
    #         _points = 10 if _points > 10 else _points
    #         _cards.append(_points)
    #     _sum = sum(_cards)
    #     _sum += 10 if _sum <= 11 and 1 in _cards else 0
    #     _sum = 0 if _sum > 21 else _sum
    #     _sum = 22 if len(_cards) == 2 and _sum == 21 else _sum
    #     return _sum
    #
    # def __judge(self, _position, _user=PLAYER):
    #     def first():
    #         player = self.__cards_sum(PLAYER)
    #         dealer = self.__cards_sum(DEALER)
    #         t_expose = self.cards[DEALER][0] % 13 + 1 >= 10
    #         if player == 22:
    #             return DEUCE if dealer == 22 else PLAYER_BLACKJACK
    #         elif t_expose and dealer == 22:
    #             return DEUCE if player == 22 else DEALER_BLACKJACK
    #
    #     def hit(_user):
    #         if self.__cards_sum(_user) == 0:
    #             return BUSTS
    #         elif _user != DEALER:
    #             return FIVE if len(self.cards[_user]) >= 5 else CONTINUE
    #         else:
    #             return CONTINUE
    #
    #     def split(user):
    #         return PLAYER_BLACKJACK if self.__cards_sum(
    #             user) == 22 else CONTINUE
    #
    #     def stand(user):
    #         player = self.__cards_sum(user)
    #         dealer = self.__cards_sum(DEALER)
    #         if player > dealer:
    #             return WIN
    #         elif player < dealer:
    #             return LOSE
    #         elif player == dealer:
    #             return DEUCE
    #
    #     def insurance():
    #         return True if self.__cards_sum(DEALER) == 22 else False
    #
    #     if _position == FIRST:
    #         return first()
    #     elif _position == HIT:
    #         return split(_user) if self.cards[_user] == 1 else hit(_user)
    #     elif _position == STAND:
    #         return stand(_user)
    #     elif _position == INSURANCE:
    #         return insurance()
    #
    # def __hit(self, func, user=PLAYER, amount=1):
    #     if amount <= 0:
    #         raise ValueError('amount <= 0')
    #     if user <= 0:
    #         raise ValueError('user error')
    #     for _ in range(amount):
    #         self.pile.draw(user)
    #     func(self.__judge(HIT, user))
    #
    # def __stand(self, func, user):
    #     func(self.__judge(STAND, user))
    #
    # def __double(self, func, user):
    #     self.pile.draw(user)
    #     func(self.__judge(STAND, user))
    #
    # def __split(self, func, user_from):
    #     user_to = len(self.pile.card)
    #     self.pile.move(user_from, user_to)
    #     func()
    #
    # def __surrender(self, func):
    #     self.pile.init()
    #     func()
    #
    # def __insurance(self, func):
    #     func(self.__judge(INSURANCE))
    #
    # @property
    # def cards(self):
    #     return self.pile.card
    #
    # @property
    # def operation(self):
    #     operate = {}
    #     for user in range(1, len(self.cards)):
    #         handle = operate[user] = {}
    #         point = self.__cards_sum(PLAYER)
    #         if point == 0:
    #             handle[HIT] = False
    #
    #     return {HIT: True, STAND: True, SPLIT: True, DOUBLE: True, SURRENDER: True, INSURANCE: True}
    #
    # @operation.setter
    # def operation(self, parameter):  # todo: 删除try，移入if中。
    #     handle = parameter[HANDLE]
    #     func = parameter[FUNCTION]
    #     try:
    #         user = parameter[USER]
    #     except KeyError:
    #         user = PLAYER
    #     if not self.operation[handle]:
    #         raise KeyError('wrong handle')
    #     else:
    #         if handle == HIT:
    #             self.__hit(user)
    #         elif handle == STAND:
    #             self.__stand(func, user)
    #         elif handle == SPLIT:
    #             self.__split(func, user)
    #         elif handle == DOUBLE:
    #             self.__double(func, user)
    #         elif handle == SURRENDER:
    #             self.__surrender(func)
    #         elif handle == INSURANCE:
    #             self.__insurance(func)


if __name__ == '__main__':
    bj = BlackJack(4)
