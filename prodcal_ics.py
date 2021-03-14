#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from icalendar import Calendar, Event
from datetime import datetime, timedelta
from lxml import html
import requests
import argparse
import logging
import secrets


def get_holidays_grouped_by_months(year):
    page = requests.get(
        "http://www.consultant.ru/law/ref/calendar/proizvodstvennye/{0}/".format(year)
    )

    if "404 Ресурс не найден!" in page.text:
        return None

    tree = html.fromstring(page.content)
    months = tree.xpath("//th[@class='month']/../../..")

    if len(months) != 12:
        logging.warning(f"Number of months in {year} don't equal to 12")

    holidays = []

    for m in months:
        holidays_in_month = m.xpath(
            ".//td[@class='holiday weekend' or @class='weekend' or @class='nowork']/text()"
        )
        holidays.append([int(day) for day in holidays_in_month])

    return holidays


def create_dayoff_event(year, month, day_start, day_end):
    event = Event()
    event.add("summary", "Выходной")
    event.add("dtstart", datetime(year, month, day_start, 0, 0, 0).date())
    event.add(
        "dtend", datetime(year, month, day_end, 0, 0, 0).date() + timedelta(days=1)
    )

    # UID is REQUIRED https://tools.ietf.org/html/rfc5545#section-3.6.1
    uid = secrets.token_hex(64)
    event.add("uid", uid)

    return event


def generate_events(year, holidays_by_months):
    import more_itertools as mit

    events = []

    for month, holidays in enumerate(holidays_by_months, start=1):
        holidays_groups = [list(group) for group in mit.consecutive_groups(holidays)]

        for g in holidays_groups:
            e = create_dayoff_event(year, month, g[0], g[-1])
            events.append(e)

    return events


def parse_args():
    parser = argparse.ArgumentParser(
        description="This script fetches data about production calendar and generates .ics file with it."
    )

    default_output_file = "test.ics"
    parser.add_argument(
        "-o",
        dest="output_file",
        metavar="out",
        default=default_output_file,
        help="output file (default: {0})".format(default_output_file),
    )

    parser.add_argument(
        "--start-year",
        metavar="yyyy",
        type=int,
        default=datetime.today().year,
        help="year calendar starts (default: current year)",
    )

    parser.add_argument(
        "--end-year",
        metavar="yyyy",
        type=int,
        default=(datetime.today().year + 1),
        help="year calendar ends (default: next year)",
    )

    parser.add_argument("--log-level", metavar="level", default="INFO")

    return parser.parse_args()


def generate_calendar(events):
    cal = Calendar()
    cal.add("prodid", "-//My calendar product//mxm.dk//")
    cal.add("version", "2.0")
    cal.add("NAME", "Производственный календарь")
    cal.add("X-WR-CALNAME", "Производственный календарь")

    for e in events:
        cal.add_component(e)

    return cal


def setup_logging(log_level):
    logging_level = getattr(logging, log_level.upper(), None)

    if not isinstance(logging_level, int):
        raise ValueError("Invalid log level: {0}".format(log_level))

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="[%d/%m/%Y:%H:%M:%S %z]",
    )


if __name__ == "__main__":
    args = parse_args()
    setup_logging(args.log_level)

    events = []

    # (args.end_year + 1) because range() function doesn't include right margin
    for year in range(args.start_year, args.end_year + 1, 1):
        holidays_by_months = get_holidays_grouped_by_months(year)

        if not holidays_by_months:
            break

        events += generate_events(year, holidays_by_months)

    cal = generate_calendar(events)

    with open(args.output_file, "w") as f:
        f.write(cal.to_ical().decode("utf-8"))
