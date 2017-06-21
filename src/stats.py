from io import BytesIO
from time import gmtime
from typing import List, Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def get_stats_image(dates):
    dates = list(map(lambda x: int(float(x)) + 3 * 60 * 60, dates))
    marks, counts = map_dates(dates)
    return vizualize(marks, counts)


def vizualize(marks, counts):
    N = len(marks)

    ind = range(N)
    width = 0.5  # the width of the bars

    _, ax = plt.subplots()
    bars = ax.bar(ind, counts, width, color='r')

    ax.set_ylabel('Hit times')
    ax.set_xticks([i + width/2 for i in ind])
    step = N // 10 + 1
    labels = [seconds_format(mark) if i % step == 0 else '' for i, mark in enumerate(marks)]
    ax.set_xticklabels(labels, rotation=60)

    autolabel(ax, bars, marks)

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf


def autolabel(ax, rects, marks):
    """
    Attach a text label above each bar displaying its height
    """
    for i, rect in enumerate(rects):
        height = rect.get_height()
        if height != 0:
            d, h, m = seconds2dhm(marks[i])
            note = f'{h:2d}:{m:02d}'
            ax.text(x=rect.get_x() + rect.get_width() * 0.75,
                    y=1 + height,
                    s=note,
                    ha='center',
                    va='bottom',
                    rotation=60)


def seconds2dhm(seconds):
    one_min = 60
    one_hour = 60 * one_min
    one_day = 24 * one_hour
    d = seconds // one_day % 3 + 1  # ?
    h = seconds // one_hour % 24
    m = seconds // one_min % 60
    return d, h, m


def seconds_format(seconds) -> str:
    d, h, m = seconds2dhm(seconds)
    return f'{h:2d}:{m:02d}'


def map_dates(dates, step=60 * 60) -> (List[Any], List[int]):
    dates.sort()
    marks = []
    counts = []
    cut = 60 * 60
    anchor = dates[0]//cut * cut

    i = 0
    while i < len(dates):
        if anchor >= dates[i]:
            counts[-1] += 1
            i += 1
        else:
            anchor += step
            marks.append(anchor)
            counts.append(0)

    return marks, counts

if __name__ == '__main__':
    get_stats_image([b'1497986779.099305', b'1497986814.3257542', b'1497986887.0540328', b'1497986945.538256',
                     b'1497987827.568172', b'1497987861.052853', b'1497987911.340299', b'1497988627.726075',
                     b'1497988778.906404', b'1497988887.101014', b'1497990397.328518', b'1497990515.96535'])
