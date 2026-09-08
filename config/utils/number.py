def format_number(num):
    try:
        number = int(num)
    except ValueError:
        return num
    return format(number, ",")
