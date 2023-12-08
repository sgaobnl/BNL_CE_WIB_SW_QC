#!/usr/bin/env python3

from hdf5libs import HDF5RawDataFile

import click
import json
from datetime import datetime

@click.command()
@click.argument('filename', type=click.Path(exists=True))

def main(filename):

    h5_file = HDF5RawDataFile(filename)

    attr_name_list = ["operational_environment", "creation_timestamp", "closing_timestamp"]

    attr_dict = {}
    for attr_name in attr_name_list:
        value = h5_file.get_attribute(attr_name)
        if "timestamp" in attr_name:
            attr_dict[attr_name] = datetime.fromtimestamp(float(value)/1000.0).isoformat()
        else:
            attr_dict[attr_name] = value

    attr_json = json.dumps(attr_dict)
    print(attr_json)

if __name__ == '__main__':
    main()
