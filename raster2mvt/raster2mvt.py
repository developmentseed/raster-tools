"""Create Per pixels polygon MVT from a COG.

Usage: python -m raster2mvt [OPTIONS] INPUT

  Create Per pixels polygon MVT from a COG.

Options:
  --output TEXT       output file prefix.  [required]
  --tilesize INTEGER
  --name TEXT
  --workers INTEGER
  -q, --quiet         Remove progressbar and other non-error output.
  --help              Show this message and exit.

"""

import json
import os
import pathlib
import sys
from concurrent import futures
from contextlib import ExitStack

import click
from rasterio.rio import options
from rio_tiler.io import COGReader
from rio_tiler_mvt import pixels_encoder


@click.command()
@options.file_in_arg
@click.option(
    "--output",
    type=str,
    required=True,
    help="output file prefix.",
)
@click.option("--tilesize", type=int, default=256)
@click.option("--name", type=str, default="cog")
@click.option("--workers", type=int, default=10)
@click.option(
    "--quiet", "-q", help="Remove progressbar and other non-error output.", is_flag=True
)
def main(
    input,
    output,
    tilesize,
    name,
    workers,
    quiet,
):
    """Create Per pixels polygon MVT from a COG."""
    with COGReader(input) as cog:
        info = cog.info()

        tms = cog.tms
        minzoom = cog.minzoom
        maxzoom = cog.maxzoom

        bounds = cog.geographic_bounds
        lon_center = (bounds[0] + bounds[2]) / 2
        lat_center = (bounds[1] + bounds[3]) / 2

        band_names = [b[1] or b[0] for b in info.band_descriptions]

    # mbtiles metadata
    # https://github.com/mapbox/mbtiles-spec/blob/master/1.3/spec.md#metadata
    metadata = {
        "name": name,
        "description": name,
        "version": 1,
        "minzoom": minzoom,
        "maxzoom": maxzoom,
        "center": f"{lon_center},{lat_center},{minzoom}",
        "bounds": ",".join(map(str, bounds)),
        "type": "overlay",
        "format": "pbf",
        "json": json.dumps(
            {
                "vector_layers": [
                    {
                        "id": name,
                        "minzoom": minzoom,
                        "maxzoom": maxzoom,
                        "fields": dict((b, "Number") for b in band_names),
                    },
                ]
            }
        ),
    }

    out_metadata = pathlib.Path(f"{output}/metadata.json")
    out_metadata.parent.mkdir(parents=True, exist_ok=True)
    with out_metadata.open(mode="w") as f:
        f.write(json.dumps(metadata))

    nb_tiles = sum(
        [
            len(list(tms.tiles(*bounds, zooms=[z])))
            for z in range(cog.minzoom, cog.maxzoom + 1)
        ]
    )

    def _tiler(tile):
        # return True
        with COGReader(input) as src_dst:
            tile_data = src_dst.tile(*tile, tilesize=tilesize)

        out_tile = pathlib.Path(f"{output}/{tile.z}/{tile.x}/{tile.y}.pbf")
        out_tile.parent.mkdir(parents=True, exist_ok=True)

        body = pixels_encoder(
            tile_data.data,
            tile_data.mask,
            band_names,
            layer_name=name,
            feature_type="polygon",
        )
        with out_tile.open(mode="wb") as f:
            f.write(body)

        return True

    with ExitStack() as ctx:
        fout = ctx.enter_context(open(os.devnull, "w")) if quiet else sys.stderr
        with futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_work = [
                executor.submit(_tiler, tile)
                for tile in tms.tiles(*bounds, zooms=list(range(minzoom, maxzoom + 1)))
            ]
            with click.progressbar(
                futures.as_completed(future_work),
                file=fout,
                show_percent=True,
                length=nb_tiles,
            ) as future:
                for res in future:
                    pass
        _ = [future.result() for future in future_work]


if __name__ == "__main__":
    main()
