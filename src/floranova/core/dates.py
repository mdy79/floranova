from datetime import datetime, timedelta, timezone
from typing import List, Dict
import jdatetime

PERSIAN_WEEKDAYS = {
    0: "شنبه",
    1: "یکشنبه",
    2: "دوشنبه",
    3: "سهشنبه",
    4: "چهارشنبه",
    5: "پنجشنبه",
    6: "جمعه",
}

PERSIAN_MONTHS = {
    1: "فروردین",
    2: "اردیبهشت",
    3: "خرداد",
    4: "تیر",
    5: "مرداد",
    6: "شهریور",
    7: "مهر",
    8: "آبان",
    9: "آذر",
    10: "دی",
    11: "بهمن",
    12: "اسفند",
}


def get_today_jalali() -> str:
    now = jdatetime.datetime.now()
    return f"{now.year:04d}-{now.month:02d}-{now.day:02d}"


def get_available_delivery_dates(days_ahead: int = 7) -> List[Dict[str, str]]:
    results = []
    base_gregorian = datetime.now(timezone.utc)
    for i in range(days_ahead):
        g_date = base_gregorian + timedelta(days=i)
        j_date = jdatetime.date.fromgregorian(date=g_date.date())
        date_str = f"{j_date.year:04d}-{j_date.month:02d}-{j_date.day:02d}"
        weekday_name = PERSIAN_WEEKDAYS.get(j_date.weekday(), "")
        month_name = PERSIAN_MONTHS.get(j_date.month, "")
        human_readable = f"{weekday_name} {j_date.day} {month_name}"
        if i == 0:
            human_readable += " (امروز)"
        elif i == 1:
            human_readable += " (فردا)"

        results.append({
            "date_jalali": date_str,
            "display_name": human_readable,
            "weekday": weekday_name,
            "day": str(j_date.day),
            "month_name": month_name,
            "is_today": (i == 0),
        })
    return results


def format_jalali_friendly(jalali_str: str) -> str:
    try:
        parts = [int(p) for p in jalali_str.split("-")]
        j_date = jdatetime.date(parts[0], parts[1], parts[2])
        weekday = PERSIAN_WEEKDAYS.get(j_date.weekday(), "")
        month = PERSIAN_MONTHS.get(j_date.month, "")
        return f"{weekday} {j_date.day} {month} {j_date.year}"
    except Exception:
        return jalali_str
