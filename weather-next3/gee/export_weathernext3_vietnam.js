var DATASET='projects/gcp-public-data-weathernext/assets/weathernext_3_0_0_0p1deg';
var REGION_MODE='BOTH';
var FORECAST_HOURS=[1,3,6,12,24,48];
var EXPORT_SCALE_METERS=11132;
var DRIVE_FOLDER='WeatherNext3_Vietnam';

var countries=ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017');
var vietnam=countries.filter(ee.Filter.eq('country_na','Vietnam')).geometry();
var mekong=ee.Geometry.Rectangle([104.35,8.25,106.95,11.20],null,false);

Map.centerObject(vietnam,5);
Map.addLayer(vietnam,{color:'00FFFF'},'Vietnam boundary',false);
Map.addLayer(mekong,{color:'FFFF00'},'Mekong Delta bbox',false);

var collection=ee.ImageCollection(DATASET);
var latestStart=ee.String(ee.List(collection.aggregate_array('start_time')).distinct().sort().reverse().get(0));
var latestRun=collection.filter(ee.Filter.eq('start_time',latestStart));
print('Latest WeatherNext 3 start_time:',latestStart);
print('Forecast hours:',latestRun.aggregate_array('forecast_hour').sort());

var PRODUCTS=[
 {key:'rain_mean_mm',band:'total_precipitation_1hr_mean',scale:1000,offset:0},
 {key:'rain_p90_mm',band:'total_precipitation_1hr_p90',scale:1000,offset:0},
 {key:'temp_mean_c',band:'temperature_2m_mean',scale:1,offset:-273.15},
 {key:'wind10_mean_ms',band:'wind_speed_10m_mean',scale:1,offset:0}
];

function exportOne(regionName,region,fh,p){
 var img=ee.Image(latestRun.filter(ee.Filter.eq('forecast_hour',fh)).first())
   .select(p.band).multiply(p.scale).add(p.offset).clip(region).toFloat();
 var stem='wn3_'+regionName.toLowerCase()+'_'+p.key+'_fh'+('000'+fh).slice(-3);
 Export.image.toDrive({image:img,description:stem,folder:DRIVE_FOLDER,fileNamePrefix:stem,
   region:region,scale:EXPORT_SCALE_METERS,crs:'EPSG:4326',maxPixels:1e9,
   fileFormat:'GeoTIFF',formatOptions:{cloudOptimized:true}});
}
function queueRegion(name,geom){
 FORECAST_HOURS.forEach(function(fh){PRODUCTS.forEach(function(p){exportOne(name,geom,fh,p);});});
}
if(REGION_MODE==='VIETNAM'||REGION_MODE==='BOTH')queueRegion('vietnam',vietnam);
if(REGION_MODE==='MEKONG'||REGION_MODE==='BOTH')queueRegion('mekong',mekong);

var preview=ee.Image(latestRun.filter(ee.Filter.eq('forecast_hour',6)).first())
 .select('total_precipitation_1hr_mean').multiply(1000).clip(vietnam);
Map.addLayer(preview,{min:0,max:30,palette:['FFFFFF','90CAF9','42A5F5','00C853','FFEB3B','FF9800','F44336','7B1FA2']},'Rain mean +6h',true);
