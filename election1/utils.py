import secrets


def unique_security_token():
    return str(secrets.token_hex())


def get_token():
    return str(secrets.token_hex())


# def before_start_date():
#     date = Dates.query.first()
#     # Convert the epoch time to a datetime object
#     start_date_time = datetime.fromtimestamp(date.start_date_time)
#
#     # Get the current date time
#     current_date_time = datetime.now()
#
#     # Check if current date time is less than start date time
#     if current_date_time < start_date_time:
#         return True
#     else:
#         return False


# def after_start_date():
#     date = Dates.query.first()
#     # Convert the epoch time to a datetime object
#     start_date_time = datetime.fromtimestamp(date.start_date_time)
#
#     # Get the current date time
#     current_date_time = datetime.now()
#
#     # Check if current date time is less than start date time
#     if current_date_time > start_date_time:
#         return True
#     else:
#         return False
#

# def after_end_date():
#     date = Dates.query.first()
#     # Convert the epoch time to a datetime object
#     end_date_time = datetime.fromtimestamp(date.end_date_time)
#
#     # Get the current date time
#     current_date_time = datetime.now()
#
#     # Check if current date time is greater than end date time
#     if current_date_time > end_date_time:
#         return True
#     else:
#         return False
#
#

