# Copyright 2021 John Reese
# Licensed under the MIT license

import asyncio
import logging
import sys

import click

from jaymap.client import JMAP
from jaymap.types.core import Request, Invocation, Capabilities
from jaymap.types.mail import Email, MailboxCondition


@click.group()
@click.pass_context
@click.option("--domain", prompt=True)
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def main(ctx: click.Context, domain: str, username: str, password: str):
    ctx.obj = (domain, username, password)

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


@main.command()
@click.pass_context
def subscribe(ctx: click.Context):
    async def callback(*args, **kwargs):
        print(f"callback({args=}, {kwargs=})")

    async def inner():
        async with JMAP(*ctx.obj) as client:
            await client.subscribe(callback=callback)

    asyncio.run(inner())


@main.command()
@click.pass_context
def multiquery(ctx: click.Context):
    async def inner():
        async with JMAP(*ctx.obj) as client:
            click.echo(client.session)
            account_id = client.session.primary_accounts[Capabilities.MAIL]
            methods = [
                (
                    "Mailbox/query",
                    {"accountId": account_id, "filter": {"role": "inbox"}},
                    "c1",
                ),
                (
                    "Mailbox/get",
                    {
                        "accountId": account_id,
                        "#ids": {
                            "resultOf": "c1",
                            "name": "Mailbox/query",
                            "path": "/ids",
                        },
                    },
                    "c2",
                ),
                (
                    "Email/query",
                    {
                        "accountId": account_id,
                        "filter": {
                            "inMailbox": "d00b1aa9-ce5c-4775-ba79-e8a8d1a042fd",
                        },
                        "limit": 2,
                    },
                    "c3",
                ),
                (
                    "Email/get",
                    {
                        "accountId": account_id,
                        "#ids": {
                            "resultOf": "c3",
                            "name": "Email/query",
                            "path": "/ids",
                        },
                    },
                    "c3",
                ),
            ]
            req = Request(
                using=client.capabilities,
                method_calls=methods,
            )
            res = await client.request(req)
            emails = res.method_responses[-1][1]["list"]
            emails = Email.from_list(emails)
            click.secho(f"{emails!r}")

    asyncio.run(inner())


@main.command()
@click.pass_context
def mailbox(ctx: click.Context):
    async def inner():
        async with JMAP(*ctx.obj) as client:
            result = await client.mailbox.get()
            mailboxes = result.list
            for mailbox in mailboxes:
                click.secho(f"{mailbox!r}", fg="red")

            result = await client.mailbox.query(filter=MailboxCondition(role="inbox"))
            result = await client.mailbox.get(ids=result.ids)
            mailboxes = result.list
            for mailbox in mailboxes:
                click.secho(f"{mailbox!r}", fg="yellow")

    asyncio.run(inner())


if __name__ == "__main__":
    main()  # pylint: disable=all
