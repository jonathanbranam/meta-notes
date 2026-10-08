"""
Outlook: a day's weather, sun and alerts for a place, as note lines.

Open-Meteo gives the geocoding and the forecast (no key); the US National
Weather Service gives alerts (US only). Standard library only. All network
access goes through fetch_json(), so tests replace that one function.
"""

import json
import math
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from meta_notes import __version__, config

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ALERTS_URL = "https://api.weather.gov/alerts/active"
CACHE_FILE = os.path.join(".meta-notes-cache", "outlook-places.json")
HEADING = "### Outlook"
TIMEOUT = 10

# line name -> on by default
SWITCHES = {"weather": True, "temps": True, "sun": True, "alert": True,
            "moon": False, "wind": False, "freeze": False, "uv": False}
BLOCKS = "▁▂▃▄▅▆▇█"

US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida",
    "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky",
    "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
    "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}


class OutlookError(ValueError):
    """The outlook can't be made; the message is the reason."""


# Network

def fetch_json(url: str, params: dict | None = None,
               headers: dict | None = None) -> dict:
    """GET a URL and decode its JSON. The only function that uses the network."""
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        raise OutlookError(f"{urllib.parse.urlsplit(url).netloc} "
                           f"returned HTTP {e.code}") from None
    except (urllib.error.URLError, OSError, ValueError) as e:
        reason = getattr(e, "reason", None) or e
        raise OutlookError(f"no network ({reason})") from None


# Settings

def settings(root: str, location: str | None) -> tuple[str, dict]:
    """The place to look up and the line switches, from the flag and config."""
    table = config.table(config.load(root), "outlook")
    on = dict(SWITCHES)
    for name in SWITCHES:
        if name in table:
            if not isinstance(table[name], bool):
                raise OutlookError(f"[outlook] {name} must be true or false")
            on[name] = table[name]
    place = location or table.get("location")
    if not isinstance(place, str) or not place.strip():
        raise OutlookError("no location (set location in [outlook] in "
                           ".meta-notes, or pass --location)")
    return place.strip(), on


# Geocoding

def _load_cache(root: str) -> dict:
    try:
        with open(os.path.join(root, CACHE_FILE), encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_cache(root: str, cache: dict) -> None:
    path = os.path.join(root, CACHE_FILE)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=1)
    except OSError:
        pass  # the cache only saves a lookup


def _describe(r: dict) -> str:
    parts = [r.get("name"), r.get("admin1"), r.get("country_code")]
    return ", ".join(p for p in parts if p)


def _state_matches(admin1: str, state: str) -> bool:
    wanted = US_STATES.get(state.upper(), state).lower()
    return (admin1 or "").lower() == wanted


def geocode(root: str, place: str) -> dict:
    """
    Coordinates for "City, ST" or a ZIP code, cached in .meta-notes-cache/.

    Returns:
        {"name", "latitude", "longitude", "country", "timezone"}

    Raises:
        OutlookError: Nothing matches, or several places match a city with
            no state; the message lists them.
    """
    key = place.lower()
    cache = _load_cache(root)
    if key in cache:
        return cache[key]

    name, _, state = (s.strip() for s in place.partition(","))
    data = fetch_json(GEOCODE_URL, {"name": name, "count": 10,
                                    "language": "en", "format": "json"})
    results = data.get("results") or []
    if state:
        results = [r for r in results
                   if _state_matches(r.get("admin1", ""), state)
                   or (r.get("country_code") or "").upper() == state.upper()]
    if not results:
        raise OutlookError(f"no place found for {place!r}")
    if len(results) > 1 and not name.isdigit() and not state:
        listed = "; ".join(_describe(r) for r in results[:5])
        raise OutlookError(f"{place!r} matches several places ({listed}); "
                           "add a state, as in \"Mason, OH\"")
    r = results[0]
    found = {"name": _describe(r), "latitude": r["latitude"],
             "longitude": r["longitude"],
             "country": (r.get("country_code") or "").upper(),
             "timezone": r.get("timezone", "UTC")}
    cache[key] = found
    _save_cache(root, cache)
    return found


# Forecast

def forecast(place: dict, day: date) -> dict:
    """Open-Meteo's daily and hourly data for one day."""
    data = fetch_json(FORECAST_URL, {
        "latitude": place["latitude"], "longitude": place["longitude"],
        "daily": ",".join([
            "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset",
            "sunshine_duration", "precipitation_probability_max", "rain_sum",
            "showers_sum", "snowfall_sum", "wind_speed_10m_max",
            "wind_gusts_10m_max", "uv_index_max"]),
        "hourly": "temperature_2m,precipitation_probability,snowfall",
        "temperature_unit": "fahrenheit", "wind_speed_unit": "mph",
        "precipitation_unit": "inch", "timezone": "auto",
        "start_date": day.isoformat(), "end_date": day.isoformat()})
    if data.get("error"):
        raise OutlookError(str(data.get("reason") or "forecast unavailable"))
    if not data.get("daily", {}).get("time"):
        raise OutlookError(f"no forecast for {day.isoformat()}")
    return data


def alerts(place: dict, day: date, tz: ZoneInfo) -> list[str]:
    """Active NWS alerts that overlap `day`, as "Event until 6:00 PM"."""
    start = datetime.combine(day, datetime.min.time(), tz)
    end = start + timedelta(days=1)
    data = fetch_json(ALERTS_URL,
                      {"point": f"{place['latitude']:.4f},"
                                f"{place['longitude']:.4f}"},
                      {"User-Agent": f"meta-notes/{__version__}",
                       "Accept": "application/geo+json"})
    out = []
    for feature in data.get("features", []):
        p = feature.get("properties", {})
        try:
            begins = datetime.fromisoformat(p.get("onset") or p["effective"])
            ends = p.get("ends") or p.get("expires")
            ends = datetime.fromisoformat(ends) if ends else None
        except (KeyError, ValueError):
            continue
        if begins >= end or (ends and ends <= start):
            continue
        text = p.get("event", "Alert")
        if ends:
            local = ends.astimezone(tz)
            when = clock(local)
            if local.date() != day:
                when += local.strftime(" %a")
            text += f" until {when}"
        out.append(text)
    return out


# Formatting

def clock(t: datetime) -> str:
    """7:41 AM"""
    return f"{t.hour % 12 or 12}:{t.minute:02d} {'AM' if t.hour < 12 else 'PM'}"


def hour_label(h: int, suffix: bool = True) -> str:
    """3 PM, noon, midnight; without the suffix, 3."""
    if h % 24 == 0:
        return "midnight"
    if h == 12:
        return "noon"
    if not suffix:
        return str(h % 12 or 12)
    return f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}"


def hour_span(first: int, last: int) -> str:
    """The hours first..last (inclusive) as "3-8 PM", "9 AM-2 PM"."""
    start, stop = first, last + 1
    same = (start < 12) == (stop <= 12) and stop != 24
    if same and start != 12 and stop != 12:
        return f"{hour_label(start, False)}-{hour_label(stop)}"
    return f"{hour_label(start)}-{hour_label(stop)}"


def _hours_at(values: list, floor: float) -> tuple[int, int] | None:
    hours = [i for i, v in enumerate(values) if v is not None and v >= floor]
    return (hours[0], hours[-1]) if hours else None


def _inches(x: float) -> str:
    return f"{x:.1f} in" if x >= 0.05 else f"{x:.2f} in"


def weather_line(daily: dict, hourly: dict) -> str:
    high = round(daily["temperature_2m_max"][0])
    low = round(daily["temperature_2m_min"][0])
    parts = [f"{high}/{low}"]
    snow = daily["snowfall_sum"][0] or 0
    chance = daily["precipitation_probability_max"][0] or 0
    if snow >= 0.1 or chance >= 20:
        kind = "snow" if snow >= 0.1 else "rain"
        text = f"{kind} {round(chance)}%"
        span = _hours_at(hourly["precipitation_probability"], 40)
        if span:
            text += " " + hour_span(*span)
        parts.append(text)
        if kind == "snow":
            parts.append(_inches(snow))
        else:
            rain = (daily["rain_sum"][0] or 0) + (daily["showers_sum"][0] or 0)
            if rain >= 0.01:
                parts.append(_inches(rain))
    sun = daily["sunshine_duration"][0]
    if sun is not None:
        parts.append(f"{round(sun / 3600)}h sun")
    return "Weather: " + ", ".join(parts)


def temps_line(hourly: dict) -> str | None:
    temps = hourly["temperature_2m"]
    if not temps or any(t is None for t in temps):
        return None
    low, high = min(temps), max(temps)
    span = (high - low) or 1
    spark = "".join(BLOCKS[min(7, int((t - low) / span * 8))] for t in temps)
    return (f"Temps: {round(low)} {spark} {round(high)} "
            f"(low {hour_label(temps.index(low))}, "
            f"high {hour_label(temps.index(high))})")


def sun_line(daily: dict) -> str:
    rise = datetime.fromisoformat(daily["sunrise"][0])
    sets = datetime.fromisoformat(daily["sunset"][0])
    return f"Sun: {clock(rise)} - {clock(sets)}"


def moon_line(day: date) -> str:
    """Phase from the mean synodic month, counted from the 2000-01-06 new moon."""
    synodic = 29.530588853
    new_moon = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    noon = datetime.combine(day, datetime.min.time(), timezone.utc) \
        + timedelta(hours=12)
    age = ((noon - new_moon).total_seconds() / 86400) % synodic
    frac = age / synodic
    lit = round((1 - math.cos(2 * math.pi * frac)) / 2 * 100)
    names = ["new moon", "waxing crescent", "first quarter",
             "waxing gibbous", "full moon", "waning gibbous",
             "last quarter", "waning crescent"]
    return f"Moon: {names[int(frac * 8 + 0.5) % 8]} ({lit}% lit)"


def wind_line(daily: dict) -> str:
    return (f"Wind: {round(daily['wind_speed_10m_max'][0])} mph, "
            f"gusts {round(daily['wind_gusts_10m_max'][0])}")


def freeze_line(daily: dict) -> str | None:
    low = round(daily["temperature_2m_min"][0])
    return f"Freeze: low {low}" if low <= 32 else None


def uv_line(daily: dict) -> str | None:
    uv = daily["uv_index_max"][0]
    return None if uv is None else f"UV: {round(uv)}"


# The command

def lines_for(root: str, day: date, place_text: str, on: dict,
              only: str | None = None) -> tuple[list[str], dict]:
    """The Outlook lines ("- Weather: ..."), and the data behind them."""
    place = geocode(root, place_text)
    data = forecast(place, day)
    daily, hourly = data["daily"], data["hourly"]
    tz = ZoneInfo(data.get("timezone") or place["timezone"])
    now = datetime.now(tz)

    wanted = {only} if only else {n for n, v in on.items() if v}
    found: dict[str, list[str]] = {}
    if "weather" in wanted:
        found["weather"] = [weather_line(daily, hourly)]
    if "temps" in wanted and not only:
        found["temps"] = [t] if (t := temps_line(hourly)) else []
    if "sun" in wanted:
        found["sun"] = [sun_line(daily)]
    if "alert" in wanted and not only and place["country"] == "US":
        try:
            found["alert"] = [f"Alert: {a}" for a in alerts(place, day, tz)]
        except OutlookError:
            found["alert"] = []  # alerts are extra; the rest still shows
    if "moon" in wanted and not only:
        found["moon"] = [moon_line(day)]
    if "wind" in wanted and not only:
        found["wind"] = [wind_line(daily)]
    if "freeze" in wanted and not only:
        found["freeze"] = [t] if (t := freeze_line(daily)) else []
    if "uv" in wanted and not only:
        found["uv"] = [t] if (t := uv_line(daily)) else []

    lines = [f"- {line}" for name in SWITCHES for line in found.get(name, [])]
    stamp = f"{clock(now)} {now.strftime('%a')}"
    return lines, {"date": day.isoformat(), "place": place["name"],
                   "as_of": stamp, "lines": [l[2:] for l in lines],
                   "daily": {k: v[0] for k, v in daily.items()},
                   "hourly": hourly}


def run(root: str, day: date, location: str | None,
        only: str | None = None, lenient: bool = False) -> tuple[list[str], dict]:
    """
    The text lines and JSON data for `meta-notes outlook`.

    Args:
        only: "weather" or "sun" for just that line, with no heading.
        lenient: On failure, return one "- Weather: unavailable (reason)"
            line instead of raising, so a note template never fails.

    Raises:
        OutlookError: When not lenient and the outlook can't be made.
    """
    try:
        place_text, on = settings(root, location)
        lines, data = lines_for(root, day, place_text, on, only)
    except (OutlookError, ValueError) as e:
        if not lenient:
            raise OutlookError(str(e)) from None
        reason = str(e)
        line = f"- Weather: unavailable ({reason})"
        return [HEADING, "", line], {"date": day.isoformat(),
                                 "unavailable": reason, "lines": [line[2:]]}
    if only:
        return lines, data
    return [f"{HEADING} (as of {data['as_of']})", ""] + lines, data


# Refresh

GENERATED = tuple(f"- {n}:" for n in
                  ("Weather", "Temps", "Sun", "Alert", "Moon", "Wind",
                   "Freeze", "UV"))


def refresh_note(root: str, day: date, location: str | None) -> dict:
    """
    Rewrite the Outlook section of `day`'s daily note.

    The section runs from the heading to the next heading. Its time and the
    lines the command writes are replaced; any other line in it is kept,
    after them. A blank line follows the heading, and the next heading,
    whatever the note had. The write is guarded
    with note_write's --expect check.

    Returns:
        {"date", "path", "status"}, status one of "refreshed", "unchanged",
        "no note", "no heading", or "failed: <reason>" (note untouched).
    """
    from meta_notes import note, note_write

    path = note.periodic_note("daily", day)[0]
    result = {"date": day.isoformat(), "path": path}
    try:
        with open(os.path.join(root, path), encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return {**result, "status": "no note"}
    start = next((i for i, l in enumerate(lines)
                  if l.startswith(HEADING)), None)
    if start is None:
        return {**result, "status": "no heading"}
    end = start + 1
    while end < len(lines) and not lines[end].startswith("#"):
        end += 1
    try:
        fresh, _ = run(root, day, location)
    except OutlookError as e:
        return {**result, "status": f"failed: {e}"}
    kept = [l for l in lines[start + 1:end] if not l.startswith(GENERATED)]
    while kept and not kept[0].strip():
        kept.pop(0)
    while kept and not kept[-1].strip():
        kept.pop()
    # One blank line after the heading and one before the next heading,
    # however many the note had.
    tail = [""] if end < len(lines) else []
    try:
        written = note_write.write(
            path, "\n".join(lines[start:end]) + "\n",
            "\n".join(fresh + kept + tail) + "\n", start + 1, end)
    except note_write.NoteWriteError as e:
        return {**result, "status": f"failed: {e}"}
    return {**result, "status": "refreshed" if written.changed
            else "unchanged"}


def refresh(root: str, day: date | None, location: str | None) -> list[dict]:
    """
    Refresh today's note and, when it exists, tomorrow's; or only `day`'s.
    """
    if day:
        return [refresh_note(root, day, location)]
    today = date.today()
    results = [refresh_note(root, today, location)]
    tomorrow = refresh_note(root, today + timedelta(days=1), location)
    if tomorrow["status"] != "no note":
        results.append(tomorrow)
    return results
