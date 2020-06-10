#!/usr/bin/env python3

import seaborn as sns 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO

from PIL import Image
from matplotlib.ticker import FormatStrFormatter
from .utils import *

def chart(title, desc, sensor, interval, unit):
    res = self.db.get_series(desc, sensor, interval)[desc]
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
    value_string = '{:.2f}'.format(value)
    x = center(w, value_string, font(104))
    draw.text((x, 50), value_string, font = font(104), fill = BLACK)

    return img