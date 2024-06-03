#!/usr/bin/env python3

from hdf5libs import HDF5RawDataFile

import click
import time

@click.command()
@click.argument('filename', type=click.Path(exists=True))

def main(filename):

    h5_file = HDF5RawDataFile(filename)

    records = h5_file.get_all_record_ids()

    for r in records:
        print(f'{r[0]}.{r[1]}')

if __name__ == '__main__':
    main()
