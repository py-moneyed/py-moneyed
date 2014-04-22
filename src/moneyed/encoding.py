# -*- coding: utf-8 -*-
from classes import Money, MultiMoney
from pymongo.son_manipulator import SONManipulator

from json import dumps, JSONEncoder, JSONDecoder

class MSONEncoder(JSONEncoder):
    item_separator = ', '
    key_separator = ': '
    def __init__(self, skipkeys=False, ensure_ascii=True,
            check_circular=True, allow_nan=True, sort_keys=False,
            indent=None, separators=None, encoding='utf-8', default=None):
        super(MSONEncoder, self).__init__(skipkeys=skipkeys, ensure_ascii=ensure_ascii,
            check_circular=check_circular, allow_nan=allow_nan, sort_keys=sort_keys,
            indent=indent, separators=(', ', ': '), encoding=encoding, default=default)

    def default(self, obj):
        if isinstance(obj, MultiMoney) or isinstance(obj, Money):
            return obj.prep_json()
        return super(MSONEncoder, self).default(obj)

class MSONDecoder(JSONDecoder):
    item_separator = ', '
    key_separator = ': '
    def __init__(self, encoding=None, object_hook=money_object_hook, parse_float=None,
                 parse_int=None, parse_constant=None, strict=True,
                 object_pairs_hook=None):
        super(MSONDecoder, self).__init__(encoding=encoding, object_hook=object_hook, parse_float=parse_float,
            parse_int=parse_int, parse_constant=parse_constant, strict=strict,
            object_pairs_hook=object_pairs_hook)

def money_object_hook(doc):
    if isEncodedMultiMoney(doc):
        return decodeMultiMoney(doc)
    elif isEncodedMoney(doc):
        return decodeMoney(doc)
    return doc

def isEncodedMoney(doc):
    return (isinstance(doc, dict) and 'a' in doc and 'c' in doc and
            (isinstance(doc['c'], str) or isinstance(doc['c'], unicode)) and len(doc['c']) == 3)

def isEncodedMultiMoney(doc):
    return isinstance(doc, dict) and 'mm' in doc and doc['mm'] is True

def decodeMultiMoney(doc):
    if isEncodedMultiMoney(doc):
        moneys = MultiMoney()
        for key, val in doc.iteritems():
            if key == 'mm':
                continue
            moneys += decodeMoney(val)
        return moneys
    return doc

def decodeMoney(doc):
    if isEncodedMoney(doc):
        return Money(amount=doc['a'], currency=doc['c'])
    return doc

# pymongo manipulator for encoding/decoding db actions
class MoneyManipulator(SONManipulator):
    def transform_incoming(self, son, collection):
        for (key, value) in son.items():
            if isinstance(value, Money):
                son[key] = value.prep_json()
            elif isinstance(value, dict):
                son[key] = self.transform_incoming(value, collection)
        return son

    def transform_outgoing(self, son, collection):
        for (key, value) in son.items():
            if isinstance(value, dict):
                if isEncodedMoney(value):
                    son[key] = decodeMoney(value)
                elif isEncodedMultiMoney(value):
                    son[key] = decodeMultiMoney(value)
                else: # Again, make sure to recurse into sub-docs
                    son[key] = self.transform_outgoing(value, collection)
        return son
