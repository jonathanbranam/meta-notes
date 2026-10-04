"""
Working hours and days by root mode: the one source prime, conventions and
checkin read, so the hours can't drift apart.

The daily template's Time Block rows are static text; templates/daily.md
(work) and templates/daily-personal.md match these hours.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Hours:
    """A mode's day: its first and last hour, the days, and the check-in end."""
    start: str          # HH:MM
    end: str            # HH:MM
    days: str           # in words, for the agent text
    checkin_end: str    # HH:MM, `checkin wait`'s default end


HOURS = {
    # The work check-in end is half an hour past the day's end
    "work": Hours("08:00", "17:00", "Monday to Friday", "17:30"),
    "personal": Hours("07:00", "21:00", "every day of the week", "21:00"),
}


def for_mode(mode: str) -> Hours:
    """The hours for a root mode ("work" or "personal")."""
    return HOURS[mode]


def prime_text(mode: str) -> str:
    """The working-day paragraph of the agent guide."""
    h = for_mode(mode)
    if mode == "work":
        return (f"Work runs {h.start} to {h.end}, {h.days}; don't plan work "
                f"after {h.end}.\n"
                "The time block runs to 18:00 so the last rows can hold "
                "after-work\n"
                "personal events. Keep them, and keep meetings and personal "
                "time the\n"
                "user placed in the time block.")
    return (f"The day runs {h.start} to {h.end}, {h.days}. The time block "
            f"covers the same hours.\n"
            "Keep meetings and personal time the user placed in the time "
            "block.")


def conventions_text(mode: str) -> str:
    """The workdays line of the conventions."""
    if mode == "work":
        return "Workdays are Monday to Friday. Weeks start on Monday."
    return ("Every day of the week is a working day. Weeks start on "
            "Monday.")
