import string, random, datetime

def random_string(size=32):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for __ in range(size))


def format_date(datetime):
    year = datetime.year
    month = datetime.month
    day = datetime.day
    return "{0}/{1}, {2}".format(day, month, year)
