# raster2pixels.py

a Rasterio based CLI to create low-resolution version of an image..


### Conda
```
conda env create -f environment.yml
```
### Pip
```
pip install -r requirements.txt
```

```
python -m raster2pixels --help
Usage: python -m raster2pixels [OPTIONS] INPUT

  Create low-resolution version of an image.

Options:
  --max-size INTEGER
  -o, --output PATH   Output file name  [required]
  --help              Show this message and exit.
```

##### requirements
- `rio-tiler`
