# Raster-tools

Tools for raster processing


### raster2csv.py

a Rasterio based CLI to extract pixel values from raster.

```
python raster2csv.py --help
Usage: raster2csv.py [OPTIONS] INPUT

  Translates a raster file into xyz format.

Options:
  --blocksize INTEGER
  -o, --output PATH    Output file name
  --help               Show this message and exit
```

##### requirements
- `rasterio`
