"""Translates a raster file into xyz format.

Usage: raster2csv.py [OPTIONS] INPUT

  Translates a raster file into xyz format.

Options:
  --blocksize INTEGER
  -o, --output PATH    Output file name
  --help               Show this message and exit.


Requirements:
- rasterio

"""

import math

import click
import numpy
import rasterio
from rasterio.rio import options
from rasterio.transform import xy
from rasterio.warp import transform
from rasterio.windows import Window


def dims(total, chop):
    """Given a total number of pixels, chop into equal chunks.

    Last one gets truncated so that sum of sizes == total.
    yeilds (offset, size) tuples
    >>> list(dims(512, 256))
    [(0, 256), (256, 256)]
    >>> list(dims(502, 256))
    [(0, 256), (256, 246)]
    >>> list(dims(522, 256))
    [(0, 256), (256, 256), (512, 10)]
    """
    for a in range(int(math.ceil(total / chop))):
        offset = a * chop
        diff = total - offset
        if diff <= chop:
            size = diff
        else:
            size = chop
        yield offset, size


def raster_to_pts(src_dst, blocksize: int = 1024):
    """Yield pixel values."""
    w = src_dst.width
    h = src_dst.height

    # Create list of `Windows` used to read chunks of the raster
    winds = [
        Window(coff, roff, wd, ht)
        for roff, ht in dims(h, blocksize)
        for coff, wd in dims(w, blocksize)
    ]

    # Iterating over the blocks
    for w in winds:
        # Read the raster using the given window
        # We use masked=True to return a MaskedArray
        data = src_dst.read(window=w, masked=True)

        # data is a masked array
        # ref: https://numpy.org/doc/stable/reference/maskedarray.generic.html#accessing-the-data
        # `data.data` is the actual data. shape is (bands, rows, cols)
        # `data.mask` is the mask. shape is (bands, rows, cols)

        # We create a `Master` mask to get the pixel's index when
        # there is at least one `valid` value through the bands
        mask = numpy.prod(data.mask, axis=0)

        # Get row/col indexes
        rows, cols = numpy.where(mask == 0)

        # Transform rows/cols index to coordinates in WGS84
        xs, ys = xy(src_dst.transform, rows + w.row_off, cols + w.col_off)
        lon, lat = transform(src_dst.crs, "epsg:4326", xs, ys)

        # Loop through indexes and yield values
        for ii, idx in enumerate(zip(cols, rows)):
            x, y = idx
            yield ([lon[ii], lat[ii]], list(data.data[:, y, x]))


@click.command()
@options.file_in_arg
@click.option("--blocksize", type=int, default=1024)
@click.option("--output", "-o", type=click.Path(exists=False), help="Output file name")
def main(input, blocksize, output):
    """Translates a raster file into xyz format."""
    with rasterio.open(input) as src_dst:
        if output:
            with open(output, "w") as f:
                f.write(
                    f"longitudes,latitudes,{','.join(['band'+ str(i + 1) for i in src_dst.indexes])}\n"
                )

        for (lng, lat), values in raster_to_pts(src_dst, blocksize):
            if output:
                with open(output, "a") as f:
                    f.write(f"{lng},{lat},{','.join(map(str, values))}\n")
            else:
                click.echo(f"{lng},{lat},{','.join(map(str, values))}")


if __name__ == "__main__":
    main()
