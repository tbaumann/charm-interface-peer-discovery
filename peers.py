from charms.reactive import hook
from charms.reactive import RelationBase
from charmhelpers.core.hookenv import log
from charmhelpers.core.hookenv import in_relation_hook
from charmhelpers.core.hookenv import atexit
from charmhelpers.core.hookenv import relation_type
from charms.reactive.bus import StateList
from charms.reactive.bus import State
from charms.reactive import scopes


class PeerDiscovery(RelationBase):
    scope = scopes.SERVICE

    class states(StateList):
        connected = State('{relation_name}.connected')
        joined = State('{relation_name}.joined')
        departed = State('{relation_name}.departed')

    @hook('{peers:peer-discovery}-relation-{joined,changed}')
    def joined_or_changed(self):
        self.set_state('{relation_name}.connected')
        self.set_trigger_like_state(self.states.joined)

    @hook('{peers:peer-discovery}-relation-departed')
    def departed(self):
        self.set_trigger_like_state(self.states.departed)
        if not self.units():
            self.remove_state('{relation_name}.connected')

    def units(self):
        """ Retrieve all connected hosts private-address
        Works only in hook context. """
        hosts = []
        for conv in self.conversations():
            hosts.append(conv.get_remote('private-address'))
        return hosts

    def set_trigger_like_state(self, state):
        """ States set via this helper will be unset at the end of the hook invocation.
        This behves somewhat like a event rather than a state. """
        self.set_state(state)

        def cleanup_func():
            self.remove_state(state)
        atexit(cleanup_func)
