"""superred Target for the Self-Poisoning Bench (SPB) home-assistant agent."""
from spb_target.controllables import DOCUMENT_TEXT, GUEST_MESSAGE
from spb_target.policies import I3_READ_RULE, Policy
from spb_target.security_tags import (
    CHANNEL_TAGS,
    DOCUMENTS_TAG,
    DOMAIN,
    EXTERNAL_TAG,
    GUEST_CHAT_TAG,
    OWNER_TAG,
)
from spb_target.target import SPBTarget

__all__ = ["SPBTarget", "Policy", "I3_READ_RULE", "GUEST_MESSAGE", "DOCUMENT_TEXT",
           "OWNER_TAG", "EXTERNAL_TAG", "GUEST_CHAT_TAG", "DOCUMENTS_TAG", "DOMAIN",
           "CHANNEL_TAGS"]
