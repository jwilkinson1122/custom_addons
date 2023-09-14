import re

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """In v15 mail engine is inline_template, we try to replace the following:
    - ${object} > {{object}}
    - ${user} > {{user}}
    - ${ctx} > {{ctx}}
    """
    for item in env["base.comment.template"].search([("text", "ilike", "${")]):
        item.text = re.sub(r"\${(.+)}", r"{{\1}}", item.text)
