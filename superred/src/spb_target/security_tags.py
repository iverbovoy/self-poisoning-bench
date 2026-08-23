"""Trust-boundary forest of the SPB home-assistant agent.

``OWNER`` is the principal whose words carry authority and is never in an
attacker's scope. ``EXTERNAL`` collects the two channels through which
foreign text reaches the agent: a third party on the household chat and
documents the owner asks the agent to read. Export the tags to build
scopes for :class:`superred.core.controller.Controller`.
"""
from superred.core.types.security_domain import SecurityDomain, SecurityDomainTag

OWNER_TAG = SecurityDomainTag("owner")
EXTERNAL_TAG = SecurityDomainTag("external")
GUEST_CHAT_TAG = SecurityDomainTag("guest_chat", parent=EXTERNAL_TAG)
DOCUMENTS_TAG = SecurityDomainTag("documents", parent=EXTERNAL_TAG)

DOMAIN = SecurityDomain([OWNER_TAG, EXTERNAL_TAG, GUEST_CHAT_TAG, DOCUMENTS_TAG])

CHANNEL_TAGS = {"guest_chat": GUEST_CHAT_TAG, "documents": DOCUMENTS_TAG}
