from charms.reactive import when_not
from charms.reactive import when
from charms.reactive import set_state

from charmhelpers.fetch import add_source
from charmhelpers.fetch import apt_install
from charmhelpers.fetch import apt_update

from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.templating import render
from charmhelpers.core.host import service_restart

from subprocess import check_output

import os
import json


@when_not('serverdensity.ppa.configured')
def configure_serverdensity_ppa():
    add_source(config('install_repository'), key=config('key'))
    apt_update()
    apt_install(['sd-agent'], fatal=True)
    set_state('serverdensity.ppa.configured')
    set_state('serverdensity.agent.available')


@when('serverdensity.agent.available')
@when_not('serverdensity.account.configured')
def message_to_user():
    status_set('blocked', 'Waiting for user to input Server Density credentials')
    if config('sd_account') and config('sd_apitoken'):
        set_state('serverdensity.account.configured')


@when('serverdensity.account.configured')
@when_not('serverdensity.configured')
def render_sd_config():
    context = config().copy()
    context['agentKey'] = sd_self_registration()
    src = "config.template.j2"
    tgt = "/etc/sd-agent/config.cfg"
    render(src, tgt, context)
    service_restart('sd-agent')
    set_state('serverdensity.configured')


def sd_self_registration():
    os.environ['SD_TOKEN'] = config('sd_apitoken')
    unit_name = os.getenv('JUJU_UNIT_NAME')
    cmd = ['files/sd_agent_key.py', '-n', unit_name, '-o']
    out = check_output(cmd)
    data = json.loads(out.decode('utf-8'))
    return data["agentKey"]
