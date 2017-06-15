from io import BytesIO
from time import gmtime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def get_stats_image(dates):
    four_hours = 4 * 60 * 60
    dates = list(map(lambda x: int(float(x)) + four_hours, dates))
    marks, counts = map_dates(dates)
    return vizualize(marks, counts)


def vizualize(marks, counts):
    N = len(marks)

    ind = range(N)
    width = 50 / N  # the width of the bars

    _, ax = plt.subplots()
    ax.bar(ind, counts, width, color='r')

    ax.set_ylabel('Hit times')
    ax.set_xticks([i + width/2 for i in ind])
    step = N // 15
    labels = [min2dhm(mark) if i % step == 0 else '' for i, mark in enumerate(marks)]
    ax.set_xticklabels(labels, rotation=60)

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf


def min2dhm(imin):
    # d = imin // (24 * 60) + 1
    h = imin % (24 * 60) // 60
    m = imin % 60
    return f'{h:2d}:{m:02d}'


def map_dates(dates, step=20):
    """
    :param dates: List[datetime]
    :param step: in minutes
    :return: 
    """
    dates.sort()
    first_day = gmtime(dates[0]).tm_yday
    last_day = gmtime(dates[-1]).tm_yday

    days_range = last_day - first_day + 1

    marks = [0] * (days_range * 60 * 24 // step)
    imin = 0
    for i in range(len(marks)):
        imin += step
        marks[i] = imin

    new_dates = []
    for unix_timestamp in dates:
        day = gmtime(unix_timestamp).tm_yday - first_day
        hour = gmtime(unix_timestamp).tm_hour
        minute = gmtime(unix_timestamp).tm_min
        new_dates.append(day * 24 * 60 + hour * 60 + minute)

    counts = [0] * len(marks)
    i = 0
    while i < len(marks):
        if not new_dates:
            break
        r = marks[i]
        d = new_dates[0]
        if r <= d < r + step:
            counts[i] += 1
            new_dates.pop(0)
        else:
            i += 1
    return marks, counts
