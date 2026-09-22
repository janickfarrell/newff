import argparse
from datetime import date
from pathlib import Path
from .scraper import scrape_range,write_csv
from .publish import publish

def day(v):return date.fromisoformat(v)
def main():
 p=argparse.ArgumentParser(prog='barreplay-news');sub=p.add_subparsers(dest='cmd',required=True)
 s=sub.add_parser('scrape');s.add_argument('--start',required=True,type=day);s.add_argument('--end',required=True,type=day);s.add_argument('--output',required=True,type=Path);s.add_argument('--delay',type=float,default=2.0)
 u=sub.add_parser('publish');u.add_argument('--input',required=True,type=Path);u.add_argument('--start',required=True,type=day);u.add_argument('--end',required=True,type=day)
 a=p.parse_args()
 if a.start>a.end:p.error('--start must be on or before --end')
 if a.cmd=='scrape':
  rows=scrape_range(a.start,a.end,a.delay);write_csv(rows,a.output);print(f"Saved {len(rows)} rows to {a.output}")
 else:publish(a.input,a.start,a.end)
