#!/usr/bin/env python3

from rawdatautils import file_conversion
import click

@click.command()
@click.option('--fromf', type=click.Path(exists=True), help="Full path to file you want to convert from")
@click.option('--tof', type=click.STRING, help="Full path to file you want to convert to")
@click.option('--ftype', type=click.Choice(['wib2','wibeth','tde'], case_sensitive=True), default='wibeth', help="Format to convert to")

def main(fromf, tof, ftype):
    """This script converts ProtoWIB binary files into either WIB2, WIBETH, or TDE format"""

    if ftype == 'wib2':
        file_conversion.wib_binary_to_wib2_binary(fromf, tof)
    elif ftype == 'tde':
        file_conversion.wib_binary_to_tde_binary(fromf, tof)
    else:
        file_conversion.wib_binary_to_wibeth_binary(fromf, tof)


if __name__ == '__main__':
    main()
