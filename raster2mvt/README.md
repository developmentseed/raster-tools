# raster2mvt.py

a Rasterio based CLI to create **per pixels** polygon MVT from a COG.


### Conda
```
conda env create -f environment.yml
```
### Pip
```
pip install -r requirements.txt
```

```
python -m raster2mvt --help
Usage: python -m raster2mvt [OPTIONS] INPUT

  Create Per pixels polygon MVT from a COG.

Options:
  --output TEXT       output file prefix.  [required]
  --tilesize INTEGER
  --name TEXT
  --workers INTEGER
  -q, --quiet         Remove progressbar and other non-error output.
  --help              Show this message and exit.
```

##### requirements
- `rasterio`
- `rio-tiler`
- `rio-tiler-mvt`

