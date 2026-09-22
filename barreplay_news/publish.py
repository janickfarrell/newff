from __future__ import annotations
import hashlib,json,os,tempfile
from datetime import date,datetime,timezone
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
from .scraper import dedupe,read_csv,write_csv

def require(name):
 v=os.getenv(name,"").strip()
 if not v:raise RuntimeError(f"Missing required environment variable: {name}")
 return v

def download_optional(repo,token,name,target):
 try:
  p=hf_hub_download(repo_id=repo,repo_type="dataset",filename=name,token=token);target.write_bytes(Path(p).read_bytes());return True
 except Exception as e:
  print(f"No existing {name}: {e}");return False

def publish(input_path:Path,start:date,end:date):
 token=require("HF_TOKEN");repo=require("HF_REPO_ID");api=HfApi(token=token);api.create_repo(repo_id=repo,repo_type="dataset",private=False,exist_ok=True)
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);old=td/'old.csv';existing=[]
  if download_optional(repo,token,'news.csv',old):existing=read_csv(old)
  fresh=read_csv(input_path);merged=dedupe([*existing,*fresh]);latest=td/'news.csv';write_csv(merged,latest)
  if start==end:archive=f"daily/{start:%Y/%m}/news_{start.isoformat()}.csv"
  else:archive=f"ranges/news_{start.isoformat()}_{end.isoformat()}.csv"
  api.upload_file(path_or_fileobj=str(input_path),path_in_repo=archive,repo_id=repo,repo_type='dataset',commit_message=f"Add Forex Factory news {start} to {end}")
  api.upload_file(path_or_fileobj=str(latest),path_in_repo='news.csv',repo_id=repo,repo_type='dataset',commit_message=f"Refresh consolidated news.csv through {end}")
  data=latest.read_bytes();manifest={"updated_at":datetime.now(timezone.utc).isoformat(),"source":"Forex Factory","timezone":"GMT+0","rows":len(merged),"sha256":hashlib.sha256(data).hexdigest(),"latest_range":{"start":start.isoformat(),"end":end.isoformat()},"download":"news.csv"}
  mp=td/'manifest.json';mp.write_text(json.dumps(manifest,indent=2),encoding='utf-8');api.upload_file(path_or_fileobj=str(mp),path_in_repo='manifest.json',repo_id=repo,repo_type='dataset',commit_message='Update news manifest')
  print(f"Published {len(fresh)} fresh rows; consolidated total {len(merged)}")
