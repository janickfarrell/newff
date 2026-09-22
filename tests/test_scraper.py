from datetime import date
from barreplay_news.scraper import dedupe,month_url,months_between,parse_ff_date

def test_months_cross_year():
 assert list(months_between(date(2025,12,1),date(2026,2,1)))==[(2025,12),(2026,1),(2026,2)]
def test_month_url():assert month_url(2026,9)=="https://www.forexfactory.com/calendar?month=sep.2026"
def test_parse_date():assert parse_ff_date("Tue Sep 22 2026")==date(2026,9,22)
def test_dedupe():
 row={"date":"Tue Sep 22 2026","time":"10:00","currency":"USD","impact":"High","event":"CPI","actual":"","forecast":"","previous":""}
 assert len(dedupe([row,row]))==1
