# Copyright 2021 John Reese
# Licensed under the MIT license

import asyncio
import logging
import sys

import click

from jaymap.client import JMAP


@click.command()
@click.option("--domain", prompt=True)
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def main(domain: str, username: str, password: str):
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    async def inner():
        async with JMAP(domain, username, password) as client:
            click.echo(client.session)

    asyncio.run(inner())


if __name__ == "__main__":
    main()  # pylint: disable=all
