import datetime
import logging

def traffic_percent(duration: datetime.timedelta, duration_in_traffic: datetime.timedelta):
    logging.debug('Duration seconds: %d'%duration.total_seconds())
    logging.debug('Duration in traffic seconds: %d' % duration_in_traffic.total_seconds())
    return 100 * ((duration_in_traffic.total_seconds() / duration.total_seconds()) - 1)


def mapping_function(x):
    if x <= 0:
        y = 0
    elif x >= 30:
        y = 270
    else:
        y = int(-0.2064 * x ** 2 + 14.818 * x)
    logging.debug('Mapped %s to %s'%(str(x), str(y)))
    return y
