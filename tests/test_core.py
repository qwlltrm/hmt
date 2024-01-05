import pytest
import arrow
from datetime import datetime, timedelta
from hmt.core import ArrowTimeProvider, OffsetResult, SECS_MAP, HMT,TimeFrame,DefaultParserProvider



class TestOffsetResult:
    def test_add_timeframe_to_offset(self):
        offset = OffsetResult()

        test_timeframe = TimeFrame("day",1,"1 day ago") # type: ignore
        offset.add_timeframe("day",1,"1 day ago")
        result = offset.get_timeframe("day")
        assert result==test_timeframe

    def test_get_timeframe(self):
        offset = OffsetResult()
        test_timeframe = TimeFrame('hour',24,"24 hours ago") #type: ignore
        offset.add_timeframe("day",1,"1 day ago")
        offset.add_timeframe("hour",24,"24 hours ago")
        result = offset.get_timeframe("hour")
        assert result == test_timeframe
    
    def test_get_timeframes(self):
        "Values in the list supposed to be ordered"
        offset = OffsetResult()
        test_timeframe = TimeFrame("day",1,"1 day ago") # type: ignore
        test_timeframe_2 = TimeFrame('hour',24,"24 hours ago") #type: ignore
        offset.add_timeframe("day",1,"1 day ago")
        offset.add_timeframe("hour",24,"24 hours ago")
        result = offset.get_timeframes()
        assert len(result)==2
        assert result[0]==test_timeframe
        assert result[1]==test_timeframe_2
        


class TestHMTCore:
    def test_HMT_core_offset_with_default_arrow_provider(self):
        hmt = HMT()
        now = datetime.now()
        offset_from_now= now+timedelta(days=1)
        
    def test_get_distance(self):
        hmt = HMT()
        timepoint_1 = datetime(year=2000,month=1,day=1)
        timepoint_2 = datetime(year=2001,month=2,day=2)
        offset = hmt.get_distance("2000.01.01","2001.02.02")
        total_sec = abs((timepoint_1-timepoint_2).total_seconds())
        assert total_sec==offset.get_timeframe("second").numeric_value #type: ignore

    def test_input_noramlization(self):
        hmt=HMT()
        input_1 = [" 01"," 02 "," 2000 "]
        assert hmt.normalize_input(input_1) == "01 02 2000"
        input_2 = ["01 ","02 "," 2000 "]
        assert hmt.normalize_input(input_2) == "01 02 2000"
        input_3 = " 01.02.2000 "
        assert hmt.normalize_input(input_3) == "01.02.2000"

        

class TestDefaultParserProvider:

    parser = DefaultParserProvider()
    
    # TODO
        
