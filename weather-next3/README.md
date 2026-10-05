# WeatherNext 3 Vietnam Static WebGIS

Mô-đun bổ sung cho repository này, không thay đổi Earth Engine API lõi.

```text
WeatherNext 3 -> Google Earth Engine Community
 -> cắt Việt Nam / ĐBSCL -> GeoTIFF
 -> prepare_web.py -> PNG + catalog.json
 -> MapLibre WebGIS -> GitHub Pages
```

## Export từ Earth Engine
Mở `weather-next3/gee/export_weathernext3_vietnam.js` trong Earth Engine Code Editor.

Dataset:
`projects/gcp-public-data-weathernext/assets/weathernext_3_0_0_0p1deg`

Chọn `REGION_MODE = 'VIETNAM' | 'MEKONG' | 'BOTH'`.

## Chuẩn bị WebGIS

```bash
pip install -r weather-next3/scripts/requirements.txt
python weather-next3/scripts/prepare_web.py --input input --output docs/data
python -m http.server 8080
```

Mở `http://localhost:8080/docs/`.

Workflow GitHub Pages deploy thư mục `docs/`. Browser không gọi Earth Engine nên người xem bản đồ không tiêu EECU.

> WeatherNext 3 là dữ liệu dự báo thử nghiệm; không thay thế cảnh báo khí tượng chính thức.
