    #!/usr/bin/env python3

import seaborn as sns 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO

from PIL import Image
from matplotlib.ticker import FormatStrFormatter
from .utils import *


def chart_new(db, charts):

    f, axes = plt.subplots(2, 2, figsize=(9, 4.5), sharex=True)
    def plot(data, axes, title, desc):
        plot = sns.lineplot(data=data, ax=axes)
        plot.set(title=title, frame_on=False, label=desc)
        plot.xaxis.set_major_locator(mdates.HourLocator(interval=4))
        plot.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.HourLocator()))
        plot.yaxis.set_major_formatter(FormatStrFormatter("%.1f{}".format(unit)))
        plot.legend().remove()
        plot.grid(ls="--")
    
    line = 0
    for i in range(0, 2):
        for j in range(0, 2):
            (title, desc, sensor, interval, unit) = charts[line]
            d = db.get_series(desc, sensor, interval)[desc]
            plot(d, axes[i, j], title, desc)
            line += 1

    f.set_tight_layout(True)
    buf = BytesIO()
    f.savefig(buf, dpi=200)
    buf.seek(0)

    f.clf()
    plt.clf()
    
    return Image.open(buf)


def chart(db, title, desc, sensor, interval, unit):
    res = db.get_series(desc, sensor, interval)[desc]
    sns.set_context("talk", font_scale=0.5)

    plot = sns.lineplot(data=res)
    plot.set(title=title, frame_on=False, label=desc)
    plot.grid(ls="--")
    plot.tick_params(width=0)
    plot.xaxis.set_major_locator(mdates.HourLocator())
    plot.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.HourLocator()))
    plot.yaxis.set_major_formatter(FormatStrFormatter("%.1f\u2009{}".format(unit)))
    plot.legend().remove()
    

    fig = plot.get_figure()
    fig.set_tight_layout(True)
    fig.set_size_inches(7.15, 4.5)
    fig.autofmt_xdate()

    buf = BytesIO()
    fig.savefig(buf, dpi=200)
    fig.clf()

    buf.seek(0)

    return Image.open(buf)

def paint_box(w, h, title, value, unit):
    (img, draw) = image(w, h)
    
    # Center title
    title = "{} ({})".format(title, unit)
    x = center(w, title, font(36))
    draw.text((x, 15), title, font = font(36), fill = GRAY_MEDIUM)

    # Draw value
    value_string = '{:.1f}'.format(value)
    x = center(w, value_string, font(104))
    draw.text((x, 50), value_string, font = font(104), fill = BLACK)

    return img