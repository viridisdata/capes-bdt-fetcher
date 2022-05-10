import argparse
import json
import logging
import pathlib
import time

from capes_btd_fetcher import buscar_todos_ano


def fetch(year, start_page, end_page, destdir, sleep):
    for data in buscar_todos_ano(year, start_page, end_page):
        page = data["pagina"]
        filename = f"capes-btd_{year}-{page:04}.json"
        filepath = destdir / str(year) / filename
        if not filepath.parent.exists():
            filepath.parent.mkdir(parents=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)
        time.sleep(sleep)


def fetch_years(year_start, year_end, destdir, sleep):
    for year in range(year_start, year_end + 1):
        fetch(year, 1, None, destdir=destdir, sleep=sleep)


def parse_year_range(year_range):
    if ":" in year_range:
        year_start, year_end = year_range.split(":")
        return {"year_start": int(year_start), "year_end": int(year_end)}
    return {"year_start": int(year_range), "year_end": int(year_range)}


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("year")
    parser.add_argument("-start-page", default=1, type=int)
    parser.add_argument("-end-page", default=None, type=int)
    parser.add_argument(
        "-dest",
        "-o",
        "--output-dir",
        default=pathlib.Path("."),
        type=pathlib.Path,
    )
    parser.add_argument("-sleep", default=1.0, type=float)

    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    year = parse_year_range(args.year)
    start_page = args.start_page
    end_page = args.end_page
    destdir = args.output_dir
    sleep = args.sleep

    logger = logging.getLogger("capes_btd_fetcher")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    try:
        fetch_years(**year, destdir=destdir, sleep=sleep)
    except Exception:
        logger.exception("Unexpected Error")
        raise
