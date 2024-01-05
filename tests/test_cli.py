# Tests for the most basic use cases with predefined datetime formats
# Usage examples
# hmt since June 23 2014
# hmt to January/22/20
# hmt 12/03/2019


import pytest
import arrow
import datetime
from datetime import timedelta
from typer.testing import CliRunner
from hmt.cli import app
from hmt.core import SECS_MAP





class TestCliBasicUsage:
    runner = CliRunner()
    def test_basic_usage(self):
        one_year_shift = datetime.date.today() + timedelta(days=365, minutes=1)
        result = self.runner.invoke(app, [str(one_year_shift)])
        assert result.exit_code == 0
        

    def test_future_dates_with_default_EN_locale(self):
        now = datetime.datetime.now()
        one_hour_shift = now+timedelta(hours=1)
        one_day_shift = now + timedelta(hours=24)
        one_week_shift = now + timedelta(days=7)
        one_month_shift = now +timedelta(days=31)
        one_year_shift = now + timedelta(days=365)
        assert self.runner.invoke(app,[str(one_hour_shift),"-g","hour"]).output == "in an hour\n"
        assert self.runner.invoke(app,[str(one_day_shift),"-g","day"]).output == "in a day\n"
        assert self.runner.invoke(app,[str(one_week_shift),"-g","week"]).output == "in a week\n"
        assert self.runner.invoke(app,[str(one_month_shift),"-g","month"]).output == "in a month\n"
        assert self.runner.invoke(app,[str(one_year_shift),"-g","year"]).output == "in a year\n"

    def test_future_date_with_default_EN_local_full_output(self):
        now = datetime.datetime.now()
        shift = now + timedelta(days=366,hours=1,seconds=1)
        result = self.runner.invoke(app,[str(shift),"-l"])
        assert len(result.output.splitlines())==len(SECS_MAP)

        
        
        
   
