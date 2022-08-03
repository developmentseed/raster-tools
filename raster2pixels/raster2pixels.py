"""Create low-resolution version of an image.

Usage: python -m raster2pixels [OPTIONS] INPUT

  Create low-resolution version of an image.

Options:
  --max-size INTEGER
  -o, --output PATH   Output file name  [required]
  --help              Show this message and exit.

"""

import math

import click
from rasterio.rio import options
from rio_tiler.io import COGReader
from rio_tiler.models import ImageData
from rio_tiler.utils import resize_array


@click.command()
@options.file_in_arg
@click.option("--max-size", type=int, default=1024)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False),
    help="Output file name",
    required=True,
)
def main(input, max_size, output):
    """Create pixelated version of one image."""
    with COGReader(input) as src_dst:
        data = src_dst.preview(max_size=64, resampling_method="average")

    ratio = data.height / data.width
    if ratio > 1:
        height = max_size
        width = math.ceil(height / ratio)
    else:
        width = max_size
        height = math.ceil(width * ratio)

    im = resize_array(data.data, height, width)
    mask = resize_array(data.mask, height, width)

    data = ImageData(im, mask)
    with open(output, "wb") as f:
        f.write(data.render(img_format="png"))


if __name__ == "__main__":
    main()
