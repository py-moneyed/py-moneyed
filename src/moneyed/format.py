from decimal import Decimal, ROUND_HALF_EVEN

def format_money(money, include_symbol=True, decimal_places=2, group_size=3,
           group_separator=',', decimal_point='.',
           positive_sign='', trailing_positive_sign='',
           negative_sign='-', trailing_negative_sign='',
           rounding_method=ROUND_HALF_EVEN):
    """Create a human-readable string from a Money instance.
    
    Based on the moneyfmt python recipe from http://docs.python.org/library/decimal.html#recipes

    inlude_symbol:          optional include currency prefix and/or suffix symbol (default is true)
    decimal_places:         optional number of decimal places to include
    group_size:             optional size of number grouping (1.000.000-type stuff, default is 3)
    group_separator:        optional grouping separator (default is comma, ',')
    decimal_point:          optional decimal point indicato (default is .)
    positive_sign:          optional sign for positive numbers (default is nothing, '')
    trailing_positive_sign: optional trailing sign for positive numbers (default is nothing, '')
    negative_sign:          optional sign for negative numbers (default is minus, '-')
    trailing_negative_sign: optional trailing minus indicator (default is nothing, '')

    """
    q = Decimal(10) ** -decimal_places      # 2 places --> '0.01'
    sign, digits, exp = money.amount.quantize(q).as_tuple()
    
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop
    
    # Trailing sign
    build(trailing_negative_sign if sign else trailing_positive_sign)
    
    # Suffix
    if include_symbol:
        build(money.currency.suffix)
    
    # Decimals
    for i in range(decimal_places):
        build(next() if digits else '0')
        
    # Decimal points
    build(decimal_point)
    
    # Grouped number
    if not digits:
        build('0')
    else:
        i = 0
        while digits:
            build(next())
            i += 1
            if i == group_size and digits:
                i = 0
                build(group_separator)
    
    # Prefix
    if include_symbol:
        build(money.currency.prefix)
    
    # Sign
    build(negative_sign if sign else positive_sign)
    
    return u''.join(reversed(result))
