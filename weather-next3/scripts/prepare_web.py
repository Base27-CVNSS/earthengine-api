#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path
import numpy as np
import rasterio
from PIL import Image

PATTERN=re.compile(r"^wn3_(vietnam|mekong)_(.+)_fh(\d{3})\.tif$",re.I)
PRODUCTS={
 "rain_mean_mm":{"label":"Mưa trung bình ensemble","unit":"mm/h","min":0.0,"max":30.0,"palette":["#FFFFFF","#D7F0FF","#90CAF9","#42A5F5","#00C853","#FFEB3B","#FF9800","#F44336","#7B1FA2"]},
 "rain_p90_mm":{"label":"Mưa P90","unit":"mm/h","min":0.0,"max":50.0,"palette":["#FFFFFF","#D7F0FF","#90CAF9","#42A5F5","#00C853","#FFEB3B","#FF9800","#F44336","#7B1FA2"]},
 "temp_mean_c":{"label":"Nhiệt độ 2 m","unit":"°C","min":15.0,"max":40.0,"palette":["#283593","#1976D2","#00BCD4","#4CAF50","#FFEB3B","#FF9800","#D32F2F"]},
 "wind10_mean_ms":{"label":"Gió 10 m","unit":"m/s","min":0.0,"max":25.0,"palette":["#E8F5E9","#A5D6A7","#66BB6A","#FFEB3B","#FF9800","#F44336","#6A1B9A"]}
}
def rgb(h):
 h=h.lstrip("#");return np.array([int(h[i:i+2],16) for i in (0,2,4)],dtype=np.float32)
def colorize(data,valid,cfg):
 norm=np.clip((data-cfg["min"])/(cfg["max"]-cfg["min"]),0,1)
 pal=np.stack([rgb(c) for c in cfg["palette"]]);pos=norm*(len(pal)-1)
 i0=np.floor(pos).astype(np.int32);i1=np.clip(i0+1,0,len(pal)-1);frac=(pos-i0)[...,None]
 out=pal[i0]*(1-frac)+pal[i1]*frac
 return np.dstack([out.astype(np.uint8),np.where(valid,190,0).astype(np.uint8)])
def stats(data,valid):
 v=data[valid]
 if not v.size:return {"min":None,"max":None,"mean":None,"p50":None}
 return {"min":round(float(np.nanmin(v)),3),"max":round(float(np.nanmax(v)),3),
         "mean":round(float(np.nanmean(v)),3),"p50":round(float(np.nanmedian(v)),3)}
def process(path,out):
 m=PATTERN.match(path.name)
 if not m:return None
 region,product,fh=m.groups();product=product.lower()
 if product not in PRODUCTS:return None
 with rasterio.open(path) as src:
  arr=src.read(1,masked=True).astype(np.float32);data=np.asarray(arr.filled(np.nan),dtype=np.float32)
  valid=(~np.ma.getmaskarray(arr))&np.isfinite(data);b=src.bounds
 cfg=PRODUCTS[product];png=path.stem+".png"
 Image.fromarray(colorize(data,valid,cfg),mode="RGBA").save(out/png,optimize=True)
 return {"id":path.stem,"region":region.lower(),"product":product,"label":cfg["label"],"unit":cfg["unit"],
         "forecastHour":int(fh),"url":"data/"+png,"bounds":[[b.left,b.bottom],[b.right,b.top]],
         "legend":{"min":cfg["min"],"max":cfg["max"],"palette":cfg["palette"]},"stats":stats(data,valid)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",default="input");ap.add_argument("--output",default="docs/data");a=ap.parse_args()
 inp,out=Path(a.input),Path(a.output);out.mkdir(parents=True,exist_ok=True);items=[]
 for tif in sorted(inp.glob("*.tif")):
  item=process(tif,out)
  if item:items.append(item);print("ok:",tif.name)
 payload={"generatedBy":"WeatherNext3 Vietnam Static WebGIS","items":sorted(items,key=lambda x:(x["region"],x["product"],x["forecastHour"]))}
 (out/"catalog.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
 print("layers:",len(items))
if __name__=="__main__":main()
