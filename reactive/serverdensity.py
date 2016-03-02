from charms.reactive import when_not
from charms.reactive import when
from charms.reactive import set_state

from charmhelpers.fetch import add_source
from charmhelpers.fetch import apt_install
from charmhelpers.fetch import apt_update

from charmhelpers.core.hookenv import config


@when_not('serverdensity.ppa.configured')
def configure_serverdensity_ppa():
    add_source(config('install_repository'), key=config('key'))
    apt_update()
    apt_install(['sd-agent'], fatal=True)
    set_state('serverdensity.ppa.configured')
    set_state('serverdensity.agent.available')
