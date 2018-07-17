#!/usr/bin/env python
import click
import structure_importers


@click.command()
@click.option('--format', required=True, type=str)
@click.argument('file', type=click.File('rb'))
def test(format, file):
    click.echo("Format: {}".format(format))
    structure = structure_importers.get_structure_tuple(
        file, format, extra_data=None)
    print "# CELL"
    for v in structure[0]:
        print v
    print "# COORDINATES"
    for coords in structure[1]:
        print coords
    print "# ATOM TYPE IDX"
    print structure[2]


if __name__ == "__main__":
    test()
