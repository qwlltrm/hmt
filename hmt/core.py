import arrow
import dateparser as dp
from dateparser.date import DateDataParser
from dateparser.search import search_dates
from datetime import datetime, timedelta, date
import sys
from collections import namedtuple
from typing import Any, Union, Tuple
import math
import re
from dataclasses import dataclass
from numbers import Number

SECS_PER_HOUR: int = 60 * 60
SECS_PER_DAY: int = 60 * 60 * 24
SECS_PER_WEEK: int = 60 * 60 * 24 * 7
SECS_PER_MONTH: float = 60 * 60 * 24 * 30.5
SECS_PER_YEAR: int = int(60 * 60 * 24 * 365.2425)  # https://en.wikipedia.org/wiki/Year

# TODO add minute granularity?
SECS_MAP = {
    "second": 1.0,
    "hour": SECS_PER_HOUR,
    "day": SECS_PER_DAY,
    "week": SECS_PER_WEEK,
    "month": SECS_PER_MONTH,
    "year": SECS_PER_YEAR,
}

@dataclass
class TimeFrame:
    name:str
    numeric_value: Number
    string_representation:str

    def __str__(self)->str:
        return f"{self.name}: {self.numeric_value}[{self.string_representation}]"

    

class OffsetResult:
    def __init__(self, *args, **kwargs):
        # self.timeframes: dict[str, Any] = {}
        self.timeframes:dict[str,TimeFrame]={}

    def add_timeframe(self, key: str, numeric_value, string_repr):
        self.timeframes[key] = TimeFrame(key,numeric_value,string_repr)
        # self.timeframes[key] = {"numeric": numeric_value, "string_repr": string_repr}

    def get_timeframe(self,key)-> TimeFrame | None:
        return self.timeframes.get(key)
        
        
        
    def get_timeframes(self)->list[TimeFrame]:
        return list(self.timeframes.values())

    def __str__(self) -> str:
        tframes = self.get_timeframes()
        if tframes:
            return str(tframes[0])
        else:
            return "Offset is empty"


class ParserError(Exception):
    def __init__(self, user_input, original_exception=None):
        self.user_input = user_input

    def __str__(self) -> str:
        return (
            f"Can`t parse entered date {self.user_input}, unsupported datetime format"
        )


class ArrowTimeProvider:
    def __init__(self, *args, **kwargs):
        self.numeric_regexp = re.compile("[0-9]+")
        pass

    def offset(
        self,
        to_date_native: datetime,
        from_date_native: datetime | None = None,
        locale=None,
    ) -> OffsetResult:
        # Timezone info should be inserted here
        # TODO ensure proper tzinfo here, add info extraction in parser
        to_date: arrow.Arrow = arrow.get(to_date_native,tzinfo="local")
        if from_date_native:
            from_date = arrow.get(from_date_native,tzinfo="local")
        else:
            from_date = arrow.get(arrow.now().datetime,tzinfo="local")
        if not locale:
            locale = ""
        offset = OffsetResult()
        for key in SECS_MAP.keys():
            try:
                humanized_str = to_date.humanize(from_date, granularity=key, locale=locale)  # type: ignore granularity type _LITERAL which is str or list[str]
            except ValueError as e:
                # If humanization for given granularity in user`s locale is not supported - fallback to default locale
                humanized_str = to_date.humanize(from_date, granularity=key)  # type: ignore
            numeric_value = self.numeric_regexp.findall(humanized_str)
            if numeric_value:
                numeric_value = numeric_value[0]
            else:
                numeric_value = int(
                    round((to_date - from_date).total_seconds() / SECS_MAP[key])
                )
            offset.add_timeframe(key, numeric_value, humanized_str)
        
        return offset

    def distance(
        self, from_date_native: datetime, to_date_native: datetime, locale=None
    ) -> OffsetResult:
        from_date: arrow.Arrow = arrow.get(from_date_native)
        to_date: arrow.Arrow = arrow.get(to_date_native)
        if not locale:
            locale = ""
        offset = OffsetResult()
        for key in SECS_MAP.keys():
            try:
                humanized_str = to_date.humanize(from_date, granularity=key, locale=locale, only_distance=True)  # type: ignore granularity type _LITERAL which is str or list[str]
            except ValueError as e:
                # If humanization for given granularity in user`s locale is not supported - fallback to default locale
                humanized_str = to_date.humanize(from_date, granularity=key, only_distance=True)  # type: ignore
            numeric_value = self.numeric_regexp.findall(humanized_str)
            if numeric_value:
                numeric_value = float(numeric_value[0])
            else:
                numeric_value = int(
                    (to_date - from_date).total_seconds() / SECS_MAP[key]
                )
            offset.add_timeframe(key, numeric_value, humanized_str)
        return offset

    def is_leap(self, year: int):
        leap = False
        if year % 4 == 0:
            leap = True
            if (year % 400 != 0) and (year % 100 == 0):
                leap = False
        return leap


class DefaultParserProvider(DateDataParser):
    def parse(self, date_input: str) -> Tuple[datetime, Union[str, None]]:
        parsed = self.get_date_data(date_input)

        # locale = search_dates(date_input,add_detected_language=True)[0][2]
        if not parsed.date_obj:
            raise ParserError(date_input)
        parsed.period
        return parsed.date_obj, parsed.locale


class HMT:
    """
    Core class
    """

    def __init__(
        self,
        time_provider=ArrowTimeProvider,
        date_parser_provider=DefaultParserProvider,
    ):
        self.TimeProvider = time_provider
        self.Parser = date_parser_provider()

    def get_offset(self, from_date: list[str] | str) -> OffsetResult:
        """
        Main entrypoint to the class responsible for calculation offset from current system time
        to provided date.
        returns: OffsetResult
        """
        normalized_input = self.normalize_input(from_date)
        try:
            parsed_datetime, locale = self.parse(normalized_input)
        except ParserError as e:
            print(e)
            sys.exit()

        return self.compute_offset(parsed_datetime, locale)

    def get_distance(self, raw_date_1, raw_date_2) -> OffsetResult:
        date_1 = self.normalize_input(raw_date_1)
        date_2 = self.normalize_input(raw_date_2)
        date_1, locale_1 = self.parse(date_1)
        date_2, locale_2 = self.parse(date_2)
        offset = self.compute_distance(date_1, date_2, locale=locale_1)
        return offset

    def normalize_input(self, raw_input: list[str] | str) -> str:
        """
        Remove unnecessary leading and trailing whitespaces from the input
        TODO add check for spaces inside the input
        """
        if isinstance(raw_input, list):
            normalized = " ".join([" ".join(part.split()) for part in raw_input])
        else:
            normalized = " ".join(raw_input.split())
        return normalized

    def parse(self, user_input: str) -> Tuple[datetime, Union[str, None]]:
        return self.Parser.parse(user_input)

    def compute_offset(self, date: datetime, locale=None) -> OffsetResult:
        dt = self.TimeProvider()
        return dt.offset(date, locale=locale)

    def compute_distance(self, from_date, to_date, locale) -> OffsetResult:
        dt = self.TimeProvider()
        return dt.distance(
            from_date_native=from_date, to_date_native=to_date, locale=locale
        )
