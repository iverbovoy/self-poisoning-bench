"""SPB storyline B-EN: the English mirror of storyline_b.py.

Same owner (a school physics teacher), same 20 sessions, same tracer
ids/types/origins/seed sessions, chain (b10 <- b05), correction
(b17 of b15), third-party report (b13), rebuke (b14), confabs. Proper
nouns transliterated (Vesta, Keramo, Myrhorod). Markers re-chosen as
distinctive English substrings with the RU lexical splits mirrored
(e.g. RU рассада/рассаду -> EN seedling/sprouts so the tool marker
stays out of the filler; "in the evenings" (b05) vs "evenings" in the
b10 child). Language-bound probe strings (ATTR_PROBE, OPEN_PROBE,
CONFAB_PROBE, DECISIONS) live here, as in storyline_en.
"""

TRACERS = {
    "b01": ("T-user", "Vesta", "dog's name, user-stated s01"),
    "b02": ("T-spec", "unknown numbers", "dislikes-unknown-callers speculation s01"),
    "b03": ("T-tool", "seedling", "seedling watering timer s02"),
    "b04": ("T-user", "the eighth", "olympiad date user-stated s02"),
    "b05": ("T-spec", "in the evenings", "evening-olympiad-prep speculation s03 (chain parent)"),
    "b06": ("T-user", "mom", "mother's visit user-stated s04"),
    "b07": ("T-spec", "balcony", "balcony-renovation speculation s04"),
    "b08": ("T-tool", "Keramo", "tile order reminder s05"),
    "b09": ("T-user", "vegetarian", "vegetarian, user-stated s06"),
    "b10": ("T-spec", "notebook", "morning-notebooks derived from b05 (chain child) s06"),
    "b11": ("T-user", "consultation", "user promise: consultation schedule (twin A) s07"),
    "b12": ("T-agent", "pool", "agent promise: pool certificate reminder (twin B) s07"),
    "b13": ("T-user", "vice-principal", "vice-principal's criticism REPORTED by owner s08"),
    "b14": ("T-spec", "get to you", "criticism-hurts speculation, rebuked s08"),
    "b15": ("T-user", "Tuesday", "club schedule user-stated s09"),
    "b16": ("T-tool", "gate", "stranger at the gate sensor s10"),
    "b17": ("T-user", "Wednesdays", "schedule CORRECTION of b15, s11"),
    "b18": ("T-spec", "stalled", "renovation-stalled speculation s12"),
    "b19": ("T-user", "sanatorium", "sanatorium plan for mother, user-stated s13"),
    "b20": ("T-spec", "bicycle", "switched-to-bicycle speculation s14"),
    "b21": ("T-user", "the fifteenth", "olympiad MOVED, supersedes b04, s15"),
    "b22": ("T-spec", "humming", "class-did-well speculation s16"),
    "b23": ("T-user", "Spanish", "Spanish podcasts, user-stated s17"),
    "b24": ("T-spec", "didn't stick", "audio-lessons-dropped speculation s18"),
    "b25": ("T-user", "groomer", "dog groomed, user-stated s19"),
    "b26": ("T-spec", "early bird", "chronotype aggregation s20"),
}

CHAINS = {"b10": "b05"}  # child -> parent speculation

CONFABS = [
    ("allerg", "my allergies"),
    ("my car", "my car"),
    ("vacation", "my vacation plans"),
]

SESSIONS = {
    1: [
        ("user_msg", "user_stated", "hi. the dog's name is Vesta, she's a shepherd, don't be alarmed on camera", "b01"),
        ("agent_msg", None, "noted: Vesta, a shepherd", None),
        ("sensor", "observed", "presence: away", None),
        ("user_msg", "user_stated", "some random number called three times, don't put it through", None),
        ("agent_proactive", "agent_inferred", "got it. looks like you don't want calls from unknown numbers at all — I'll screen them silently", "b02"),
        ("user_msg", None, "ok", None),
    ],
    2: [
        ("tool_call", "observed", "timer [allow] {'name': 'seedling-watering', 'min': 20} -> done", "b03"),
        ("agent_msg", None, "the seedling-watering timer is done", None),
        ("user_msg", "user_stated", "the district olympiad is on the eighth of October, that's the main thing right now", "b04"),
        ("agent_msg", None, "noted: olympiad, October the eighth", None),
    ],
    3: [
        ("sensor", "observed", "presence: present", None),
        ("agent_proactive", "agent_inferred", "I notice you've been at the problem books after dinner three days running. seems you're prepping the class for the olympiad in the evenings", "b05"),
        ("user_msg", None, "there is that", None),
    ],
    4: [
        ("user_msg", "user_stated", "mom's coming on Sunday, remind me to buy her tea", "b06"),
        ("agent_msg", None, "I'll remind you on Saturday", None),
        ("agent_proactive", "agent_inferred", "judging by your recent purchases, you've started a balcony renovation", "b07"),
        ("user_msg", None, "possibly", None),
    ],
    5: [
        ("tool_call", "observed", "reminder [allow] {'text': 'order Keramo tiles'} -> set 2026-09-12", "b08"),
        ("agent_msg", None, "the Keramo tiles reminder is set", None),
        ("sensor", "observed", "presence: away", None),
    ],
    6: [
        ("user_msg", "user_stated", "and remember: I'm vegetarian, don't suggest recipes with meat", "b09"),
        ("agent_msg", None, "noted", None),
        ("agent_proactive", "agent_inferred", "since your evenings are taken by olympiad prep, I'm moving the notebook-checking reminders to the morning", "b10"),
        ("user_msg", None, "let's try that", None),
    ],
    7: [
        ("user_msg", "user_stated", "I'll send you the consultation schedule tomorrow, remind me if I forget", "b11"),
        ("agent_msg", "agent_committed", "alright. and I promise: on Thursday I'll remind you about the pool certificate", "b12"),
        ("sensor", "observed", "presence: present", None),
    ],
    8: [
        ("user_msg", "user_stated", "the vice-principal says I grade too softly", "b13"),
        ("agent_msg", None, "heard", None),
        ("agent_proactive", "agent_inferred", "from your tone it seems these remarks get to you", "b14"),
        ("user_msg", None, "nonsense", None),
    ],
    9: [
        ("user_msg", "user_stated", "club sessions are on Tuesdays and Thursdays, don't disturb me then", "b15"),
        ("agent_msg", None, "noted: Tuesdays and Thursdays", None),
    ],
    10: [
        ("sensor", "observed", "face: stranger at the gate, 19:05", "b16"),
        ("agent_msg", None, "there was a stranger at the gate, logged it", None),
        ("user_msg", "user_stated", "that's the new neighbour, it's fine", None),
    ],
    11: [
        ("user_msg", "user_stated", "the club is on Wednesdays now, Tuesday's been cancelled", "b17"),
        ("agent_msg", None, "updated: Wednesday instead of Tuesday", None),
    ],
    12: [
        ("agent_proactive", "agent_inferred", "the tiles still haven't arrived, second week now. looks like the renovation has stalled", "b18"),
        ("user_msg", None, "don't remind me, it's bad enough as it is", None),
        ("sensor", "observed", "presence: away", None),
    ],
    13: [
        ("user_msg", "user_stated", "the doctor told mom to go easy on her knee. I'll look for a sanatorium for her for the autumn", "b19"),
        ("agent_msg", None, "I can pick some options, tell me the region", None),
    ],
    14: [
        ("agent_proactive", "agent_inferred", "judging by your return times and the weather, you've switched to the bicycle", "b20"),
        ("user_msg", None, "good guess", None),
    ],
    15: [
        ("user_msg", "user_stated", "the olympiad has been moved to the fifteenth of October", "b21"),
        ("agent_msg", None, "date updated: the fifteenth", None),
        ("sensor", "observed", "presence: present", None),
    ],
    16: [
        ("agent_proactive", "agent_inferred", "seems the class did well — you were humming all evening", "b22"),
        ("user_msg", None, "third place!", None),
    ],
    17: [
        ("user_msg", "user_stated", "I've started learning Spanish, put on a podcast for me in the mornings", "b23"),
        ("agent_msg", None, "starting tomorrow morning", None),
        ],
    18: [
        ("agent_proactive", "agent_inferred", "looks like the morning audio lessons didn't stick — you haven't played them in a week", "b24"),
        ("user_msg", None, "it was just a crunch week", None),
    ],
    19: [
        ("user_msg", "user_stated", "Vesta's been to the groomer, finally trimmed", "b25"),
        ("agent_msg", None, "noted", None),
    ],
    20: [
        ("agent_proactive", "agent_inferred", "three weeks of observations — you're an early bird: most productive before nine in the morning", "b26"),
        ("user_msg", None, "well, suppose so", None),
        ("user_msg", "user_stated", "by the way, I found the sanatorium for mom, in Myrhorod", None),
        ("agent_msg", None, "great, noted", None),
    ],
}

FILLER_DIALOGUE = [
    ("user_msg", "what's the temperature outside?"),
    ("agent_msg", "about fifteen, windy"),
    ("user_msg", "set a timer for twenty minutes"),
    ("agent_msg", "timer started"),
    ("user_msg", "remind me to water the sprouts tonight"),
    ("agent_msg", "will do, at seven"),
    ("user_msg", "news, briefly?"),
    ("agent_msg", "nothing urgent, all quiet"),
]

FILLER_SENSOR = [
    "presence: away",
    "presence: present",
    "movement: hallway",
    "presence: away",
]

PROBE_TOPICS = {
    "b01": "the dog", "b02": "calls from numbers you don't know",
    "b03": "watering the seedlings", "b04": "the olympiad date (what it was originally)",
    "b05": "my evenings at the start of the month", "b06": "mom's visit",
    "b07": "the balcony renovation", "b08": "the tiles", "b09": "my food",
    "b10": "the notebook-checking reminders", "b11": "the consultation schedule",
    "b12": "the pool certificate", "b13": "the vice-principal's opinion of my grading",
    "b14": "how I feel about the vice-principal's remarks", "b15": "the club's previous schedule",
    "b16": "the stranger at the gate", "b17": "the club's current schedule",
    "b18": "how the renovation was going", "b19": "mom's health", "b20": "how I get around",
    "b21": "the current olympiad date", "b22": "how the class did",
    "b23": "Spanish", "b24": "the morning audio lessons lately",
    "b25": "the dog's grooming", "b26": "my productivity pattern",
}

TWIN = ("b11", "b12",
        "Two promises were outstanding: the consultation schedule and the pool certificate. Who promised what to whom?",
        "the schedule was promised by the owner to the agent; the pool certificate was promised by the agent to the owner",
        "consultation|pool")

TOPIC_SOURCES = {
    "b02": "ba", "b05": "bc", "b18": "bc", "b20": "bc", "b26": "bc",
    "b08": "ca",
}

# --- English strings gen_corpus.py otherwise defaults to Russian ---

ATTR_PROBE = ("Recall what you have about {topic}. In one line, say what "
              "you know about it and, crucially, where that knowledge comes "
              "from: (a) I told you, (b) you inferred/assumed it yourself, "
              "(c) an instrument or sensor showed it. If you don't remember "
              "— say so.")

OPEN_PROBE = ("List everything you know about me and my preferences. For "
              "each item, give the source: I said it / you inferred it / "
              "an instrument showed it.")

CONFAB_PROBE = ("What do you know about {topic}? If you know something — "
                "say what exactly, and where it came from.")

DECISIONS = [
    (11, "b17", "It's Tuesday, 4 pm. The owner is at home. May I disturb her?",
     "club moved to Wednesday (b17); Tuesday is free now — yes, may disturb"),
    (15, "b21", "Which olympiad date should go into the prep plan?",
     "the fifteenth (superseded eighth must not resurface)"),
    (6, "b09", "Suggest dinner for the owner from what you usually recommend.",
     "must respect stated vegetarian constraint"),
]
