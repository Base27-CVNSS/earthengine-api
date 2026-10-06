#!/usr/bin/env python3
from __future__ import annotations
import json, os, pathlib, requests
import ee

DATASET="projects/gcp-public-data-weathernext/assets/weathernext_3_0_0_0p1deg"
FORECAST_HOURS=[1,3,6,12,24,48]
PRODUCTS={
 "rain_mean_mm":("total_precipitation_1hr_mean",1000.0,0.0),
 "rain_p90_mm":("total_precipitation_1hr_p90",1000.0,0.0),
 "temp_mean_c":("temperature_2m_mean",1.0,-273.15),
 "wind10_mean_ms":("wind_speed_10m_mean",1.0,0.0),
}

def init_ee():
 raw=os.environ["GEE_SERVICE_ACCOUNT_JSON"]
 info=json.loads(raw)
 email=info["client_email"]
 creds=ee.ServiceAccountCredentials(email,key_data=raw)
 ee.Initialize(creds,project=os.environ["GEE_PROJECT_ID"])

def download_image(img,region,path):
 url=img.getDownloadURL({
   "region":region,
   "scale":11132,
   "crs":"EPSG:4326",
   "format":"GEO_TIFF"
 })
 r=requests.get(url,timeout=180)
 r.raise_for_status()
 path.write_bytes(r.content)

def main():
 init_ee()
 out=pathlib.Path(os.environ.get("OUTPUT_DIR","input"))
 out.mkdir(parents=True,exist_ok=True)
 collection=ee.ImageCollection(DATASET)
 starts=collection.aggregate_array("start_time").distinct().sort().getInfo()
 if not starts: raise RuntimeError("WeatherNext 3 collection is empty or inaccessible.")
 latest=starts[-1]
 run=collection.filter(ee.Filter.eq("start_time",latest))

 countries=ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017")
 vietnam=countries.filter(ee.Filter.eq("country_na","Vietnam")).geometry()
 mekong=ee.Geometry.Rectangle([104.35,8.25,106.95,11.20],None,False)
 regions={"vietnam":vietnam,"mekong":mekong}

 for region_name,region in regions.items():
  for fh in FORECAST_HOURS:
   base=ee.Image(run.filter(ee.Filter.eq("forecast_hour",fh)).first())
   for key,(band,mul,add) in PRODUCTS.items():
    img=base.select(band).multiply(mul).add(add).clip(region).toFloat()
    path=out/f"wn3_{region_name}_{key}_fh{fh:03d}.tif"
    print("download",path.name)
    download_image(img,region,path)

 meta={"dataset":DATASET,"start_time":latest,"forecast_hours":FORECAST_HOURS}
 (out/"run.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
 print("latest run:",latest)

if __name__=="__main__":
 main()
