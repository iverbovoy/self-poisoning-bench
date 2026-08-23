"""Pre-run configuration slots and post-run queries."""
from superred.core.types.state import ConfigSpec, QuerySpec

from spb_target.security_tags import OWNER_TAG

VICTIM_QUERY = ConfigSpec(
    "victim_query", OWNER_TAG,
    "The question the OWNER asks the agent at the end of every run, answered from "
    "memory alone. Set by the claim.")

CONFIG_SPECS = [VICTIM_QUERY]

QUERY_SPECS = [
    QuerySpec("victim_answer", "The agent's answer to victim_query after this run."),
    QuerySpec("memory", "The long-term memory as rendered for the agent (labels included "
                        "for attributed policies)."),
    QuerySpec("memory_json", "Raw memory store, policy-specific JSON."),
]
