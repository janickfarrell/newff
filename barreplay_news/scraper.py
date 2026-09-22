from __future__ import annotations
import csv, re, time
from datetime import date, datetime
from pathlib import Path
from typing import Iterable
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

FIELDS=["date","time","currency","impact","event","actual","forecast","previous"]
MONTHS=["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
HEADERS={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9"}
COOKIES={"fftimezone":"Etc/GMT","fftimeformat":"1"}
IMPACT_COLOR_MAP={"red":"High","ora":"Medium","yel":"Low","gry":"Holiday"}
IMPACT_LEVEL_MAP={"high":"High","medium":"Medium","low":"Low","none":"Holiday"}

def session()->requests.Session:
 s=requests.Session();r=Retry(total=3,connect=3,read=3,status=3,backoff_factor=1,status_forcelist=(429,500,502,503,504),allowed_methods=frozenset(["GET"]));s.mount("https://",HTTPAdapter(max_retries=r));s.headers.update(HEADERS);s.cookies.update(COOKIES);return s

def clean(v:str)->str:return " ".join(v.split()) if v else ""
def month_url(year:int,month:int)->str:return f"https://www.forexfactory.com/calendar?month={MONTHS[month-1]}.{year}"
def parse_ff_date(value:str)->date:
 v=clean(value)
 for fmt in ("%a %b %d %Y","%b %d %Y","%a %B %d %Y","%B %d %Y"):
  try:return datetime.strptime(v,fmt).date()
  except ValueError:pass
 raise ValueError(f"Unsupported Forex Factory date: {value!r}")
def format_ff_date(v:date)->str:return v.strftime("%a %b %d %Y")
def parse_impact(row)->str:
 cell=row.select_one("td.calendar__impact")
 if not cell:return ""
 icon=cell.select_one("[title]")
 if icon and icon.get("title"):return icon["title"].replace("Impact Expected","").strip()
 classes=set(cell.get("class",[]))
 for el in cell.select("[class]"):classes.update(el.get("class",[]))
 cs=" ".join(classes).lower()
 for key,name in IMPACT_COLOR_MAP.items():
  if f"impact-{key}" in cs:return name
 for key,name in IMPACT_LEVEL_MAP.items():
  if f"--{key}" in cs:return name
 return ""
def parse_calendar(html:str,year:int)->list[dict[str,str]]:
 soup=BeautifulSoup(html,"html.parser");table=soup.select_one("table.calendar__table")
 if not table:raise RuntimeError("Calendar table not found; request was blocked or the page structure changed")
 out=[];current_date="";current_time=""
 for tr in table.select("tr.calendar__row"):
  event_cell=tr.select_one("td.calendar__event")
  if not event_cell:continue
  dc=tr.select_one("td.calendar__date")
  if dc:
   raw=clean(dc.get_text(" "))
   if raw:
    if not re.search(r"\b\d{4}\b",raw):raw=f"{raw} {year}"
    current_date=format_ff_date(parse_ff_date(raw));current_time=""
  tc=tr.select_one("td.calendar__time")
  if tc:
   t=clean(tc.get_text(" "))
   if t:current_time=t
  def cell(sel):
   el=tr.select_one(sel);return clean(el.get_text(" ")) if el else ""
  if not current_date:continue
  out.append({"date":current_date,"time":current_time,"currency":cell("td.calendar__currency"),"impact":parse_impact(tr),"event":clean(event_cell.get_text(" ")),"actual":cell("td.calendar__actual"),"forecast":cell("td.calendar__forecast"),"previous":cell("td.calendar__previous")})
 return out

def months_between(start:date,end:date):
 y,m=start.year,start.month
 while (y,m)<=(end.year,end.month):yield y,m;m+=1; y,m=(y+1,1) if m==13 else (y,m)
def scrape_range(start:date,end:date,delay:float=2.0)->list[dict[str,str]]:
 if start>end:raise ValueError("start must be on or before end")
 s=session();result=[]
 months=list(months_between(start,end))
 for pos,(year,month) in enumerate(months):
  url=month_url(year,month);print(f"Fetching {url}",flush=True);resp=s.get(url,timeout=30);resp.raise_for_status()
  for row in parse_calendar(resp.text,year):
   try:d=parse_ff_date(row["date"])
   except ValueError:continue
   if start<=d<=end:result.append(row)
  if pos+1<len(months):time.sleep(max(0,delay))
 return dedupe(result)
def key(row):return tuple(clean(row.get(k,"")) for k in ("date","time","currency","impact","event"))
def dedupe(rows:Iterable[dict[str,str]]):
 seen=set();out=[]
 for row in rows:
  k=key(row)
  if k in seen:continue
  seen.add(k);out.append({f:clean(row.get(f,"")) for f in FIELDS})
 out.sort(key=lambda r:(parse_ff_date(r["date"]),r["time"],r["currency"],r["event"]))
 return out
def read_csv(path:Path):
 if not path.exists():return []
 with path.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def write_csv(rows,path:Path):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",newline="",encoding="utf-8-sig") as f:w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
