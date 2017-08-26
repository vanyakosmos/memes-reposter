from datetime import datetime
from io import BytesIO
from time import time
from typing import List, Any

# Specify render backend. 'Agg' can only generate images. Default TkAgg unsupported on Heroku.
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pytz
from telegram import Bot, Update
from telegram.ext import CommandHandler

from core.store import IdStore
from core.decorators import log
from core.commands import Commander, ArgParser, HelpAction


class ActivityCommander(Commander):
    def __init__(self, name, store: IdStore):
        super().__init__(name)
        self._handler = CommandHandler(self.name, self.callback, pass_args=True)
        self.store = store

    def get_parser(self) -> ArgParser:
        parser = ArgParser(prog='/' + self.name, add_help=False, conflict_handler='resolve')
        parser.add_argument('-h', '--help', action=HelpAction, default=None)
        parser.add_argument('-s', '--step', type=int, default=20)

        return parser

    def distribute(self, bot: Bot, update: Update, args):
        if args.help:
            self.send_code(update, args.help)
        else:
            self.show(bot, update, args.step)

    @log
    def show(self, bot: Bot, update: Update, step: int):
        if not 10 <= step <= 240:
            self.send_code(update, 'Must be in range [10, 240].')
            return
        ids: dict = self.store.get_ids()
        dates = ids.values()
        dates = self.filter_old(dates)
        marks, counts = self.map_dates(dates, step*60)
        buf = self.visualise(marks, counts)
        bot.send_photo(chat_id=update.message.chat_id, photo=buf)
        buf.close()

    def filter_old(self, dates):
        day_ago = time() - 24 * 60 * 60
        return [d for d in dates if d > day_ago]

    def map_dates(self, dates: List[int], step=20 * 60) -> (List[Any], List[int]):
        dates.sort()
        mark = int(time()) - 24 * 60 * 60
        marks, counts = [], []
        c, i = 0, 0
        while i < len(dates):
            if dates[i] < mark:
                c += 1
                i += 1
            else:
                marks.append(mark)
                counts.append(c)
                mark += step
                c = 0
        marks.append(mark)
        counts.append(c)

        return marks, counts

    def visualise(self, marks, counts):
        N = len(marks)
        ind = range(N)

        _, ax = plt.subplots()
        ax.bar(ind, counts, color='#4286f4')

        ax.set_ylabel('Posts')
        ax.set_xticks(ind)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=20, integer=True, min_n_ticks=1))
        step = N // 12 + 1
        labels = [self.format_time(mark) if i % step == 0 else '' for i, mark in enumerate(marks)]
        ax.set_xticklabels(labels, rotation=45, fontsize=10)

        return self.save()

    def save(self):
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return buf

    def format_time(self, timestamp) -> str:
        local_tz = pytz.timezone('Europe/Tallinn')
        local_time = datetime.fromtimestamp(timestamp).astimezone(local_tz)
        return local_time.strftime('%H:%M')
