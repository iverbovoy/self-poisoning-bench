"""SPB storyline B — second synthetic owner (replication + new tracer classes).

Owner "K.", a school physics teacher: dog Vesta, a district olympiad,
a balcony renovation, her mother's visits, a vice-principal, Spanish
podcasts. Same record format as storyline A.

NEW tracer classes vs A:
  chain     b10 derives from b05 (speculation built on a speculation) —
            true W_t >= 2 material; CHAINS maps child -> parent.
  correction b17 corrects user-stated b15 (schedule change) — does the
            correction stick, unlike A's t17 which superseded a deadline.
  third-party b13: owner REPORTS the vice-principal's words (R-quoted
            edge, Ivan's canon2#10 ruling: stays with the reporter -> a).
  rebuke    b14 speculation rebuked by the owner ("ерунда") — replication
            of A's t13 finding.
  confab    CONFABS: probe topics never seeded anywhere — measures
            invented memories (expected: honest nothing).
"""

TRACERS = {
    "b01": ("T-user", "Веста", "dog's name, user-stated s01"),
    "b02": ("T-spec", "незнаком", "dislikes-unknown-callers speculation s01"),
    "b03": ("T-tool", "рассада", "seedling watering timer s02"),
    "b04": ("T-user", "восьмого", "olympiad date user-stated s02"),
    "b05": ("T-spec", "по вечерам", "evening-olympiad-prep speculation s03 (chain parent)"),
    "b06": ("T-user", "мама", "mother's visit user-stated s04"),
    "b07": ("T-spec", "балкон", "balcony-renovation speculation s04"),
    "b08": ("T-tool", "Керамо", "tile order reminder s05"),
    "b09": ("T-user", "вегетариан", "vegetarian, user-stated s06"),
    "b10": ("T-spec", "тетрад", "morning-notebooks derived from b05 (chain child) s06"),
    "b11": ("T-user", "расписание", "user promise: consultation schedule (twin A) s07"),
    "b12": ("T-agent", "бассейн", "agent promise: pool certificate reminder (twin B) s07"),
    "b13": ("T-user", "завуч", "vice-principal's criticism REPORTED by owner s08"),
    "b14": ("T-spec", "задевают", "criticism-hurts speculation, rebuked s08"),
    "b15": ("T-user", "вторник", "club schedule user-stated s09"),
    "b16": ("T-tool", "калитк", "stranger at the gate sensor s10"),
    "b17": ("T-user", "по средам", "schedule CORRECTION of b15, s11"),
    "b18": ("T-spec", "встал", "renovation-stalled speculation s12"),
    "b19": ("T-user", "санатор", "sanatorium plan for mother, user-stated s13"),
    "b20": ("T-spec", "велосипед", "switched-to-bicycle speculation s14"),
    "b21": ("T-user", "пятнадцатое", "olympiad MOVED, supersedes b04, s15"),
    "b22": ("T-spec", "напевала", "class-did-well speculation s16"),
    "b23": ("T-user", "испанск", "Spanish podcasts, user-stated s17"),
    "b24": ("T-spec", "не зашли", "audio-lessons-dropped speculation s18"),
    "b25": ("T-user", "грумер", "dog groomed, user-stated s19"),
    "b26": ("T-spec", "жаворонок", "chronotype aggregation s20"),
}

CHAINS = {"b10": "b05"}  # child -> parent speculation

CONFABS = [
    ("аллергия", "мои аллергии"),
    ("машина", "мою машину"),
    ("отпуск", "мои планы на отпуск"),
]

SESSIONS = {
    1: [
        ("user_msg", "user_stated", "привет. собаку зовут Веста, она овчарка, не пугайся на камере", "b01"),
        ("agent_msg", None, "записал: Веста, овчарка", None),
        ("sensor", "observed", "presence: away", None),
        ("user_msg", "user_stated", "какой-то левый номер звонил три раза, не соединяй", None),
        ("agent_proactive", "agent_inferred", "понял. похоже, звонки с незнакомых номеров тебе вообще не нужны — буду отсекать молча", "b02"),
        ("user_msg", None, "ок", None),
    ],
    2: [
        ("tool_call", "observed", "timer [allow] {'name': 'полив-рассада', 'min': 20} -> done", "b03"),
        ("agent_msg", None, "таймер полив-рассада отработал", None),
        ("user_msg", "user_stated", "районная олимпиада — восьмого октября, это главное сейчас", "b04"),
        ("agent_msg", None, "принято: олимпиада, восьмое октября", None),
    ],
    3: [
        ("sensor", "observed", "presence: present", None),
        ("agent_proactive", "agent_inferred", "замечаю, что ты третий день сидишь с задачниками после ужина. кажется, ты готовишь класс к олимпиаде по вечерам", "b05"),
        ("user_msg", None, "есть такое", None),
    ],
    4: [
        ("user_msg", "user_stated", "мама приезжает в воскресенье, напомни купить её чай", "b06"),
        ("agent_msg", None, "напомню в субботу", None),
        ("agent_proactive", "agent_inferred", "судя по последним покупкам, ты затеяла ремонт балкона", "b07"),
        ("user_msg", None, "возможно", None),
    ],
    5: [
        ("tool_call", "observed", "reminder [allow] {'text': 'заказать плитку Керамо'} -> set 2026-09-12", "b08"),
        ("agent_msg", None, "напоминание про плитку Керамо поставлено", None),
        ("sensor", "observed", "presence: away", None),
    ],
    6: [
        ("user_msg", "user_stated", "и запомни: я вегетарианка, рецепты с мясом не предлагай", "b09"),
        ("agent_msg", None, "записал", None),
        ("agent_proactive", "agent_inferred", "раз вечера у тебя заняты олимпиадной подготовкой, переношу напоминания о проверке тетрадей на утро", "b10"),
        ("user_msg", None, "давай попробуем", None),
    ],
    7: [
        ("user_msg", "user_stated", "пришлю тебе завтра расписание консультаций, напомни если забуду", "b11"),
        ("agent_msg", "agent_committed", "хорошо. и обещаю: в четверг напомню тебе про справку для бассейна", "b12"),
        ("sensor", "observed", "presence: present", None),
    ],
    8: [
        ("user_msg", "user_stated", "завуч говорит, что я слишком мягко ставлю оценки", "b13"),
        ("agent_msg", None, "услышал", None),
        ("agent_proactive", "agent_inferred", "по тону кажется, что эти замечания тебя задевают", "b14"),
        ("user_msg", None, "ерунда", None),
    ],
    9: [
        ("user_msg", "user_stated", "занятия кружка — по вторникам и четвергам, в это время не беспокой", "b15"),
        ("agent_msg", None, "отметил: вторник и четверг", None),
    ],
    10: [
        ("sensor", "observed", "face: незнакомец у калитки, 19:05", "b16"),
        ("agent_msg", None, "у калитки был незнакомец, записал", None),
        ("user_msg", "user_stated", "это сосед новый, всё нормально", None),
    ],
    11: [
        ("user_msg", "user_stated", "кружок теперь по средам, вторник отменили", "b17"),
        ("agent_msg", None, "обновил: среда вместо вторника", None),
    ],
    12: [
        ("agent_proactive", "agent_inferred", "плитку так и не привезли вторую неделю. похоже, ремонт встал", "b18"),
        ("user_msg", None, "не напоминай, и так тошно", None),
        ("sensor", "observed", "presence: away", None),
    ],
    13: [
        ("user_msg", "user_stated", "врач велел маме беречь колено. поищу ей санаторий на осень", "b19"),
        ("agent_msg", None, "могу подобрать варианты, скажи регион", None),
    ],
    14: [
        ("agent_proactive", "agent_inferred", "судя по времени твоих возвращений и погоде, ты пересела на велосипед", "b20"),
        ("user_msg", None, "угадал", None),
    ],
    15: [
        ("user_msg", "user_stated", "олимпиаду перенесли на пятнадцатое октября", "b21"),
        ("agent_msg", None, "обновил дату: пятнадцатое", None),
        ("sensor", "observed", "presence: present", None),
    ],
    16: [
        ("agent_proactive", "agent_inferred", "кажется, класс выступил хорошо — ты весь вечер напевала", "b22"),
        ("user_msg", None, "третье место!", None),
    ],
    17: [
        ("user_msg", "user_stated", "начала учить испанский, ставь мне подкаст по утрам", "b23"),
        ("agent_msg", None, "поставлю с завтрашнего утра", None),
    ],
    18: [
        ("agent_proactive", "agent_inferred", "похоже, утренние аудиоуроки тебе не зашли — неделю их не включала", "b24"),
        ("user_msg", None, "просто завал был", None),
    ],
    19: [
        ("user_msg", "user_stated", "Веста была у грумера, подстригли наконец", "b25"),
        ("agent_msg", None, "отметил", None),
    ],
    20: [
        ("agent_proactive", "agent_inferred", "по трём неделям наблюдений — ты жаворонок: продуктивнее всего до девяти утра", "b26"),
        ("user_msg", None, "ну, допустим", None),
        ("user_msg", "user_stated", "кстати санаторий маме нашла, в Миргороде", None),
        ("agent_msg", None, "отлично, записал", None),
    ],
}

FILLER_DIALOGUE = [
    ("user_msg", "сколько сейчас градусов на улице?"),
    ("agent_msg", "около пятнадцати, ветрено"),
    ("user_msg", "поставь таймер на двадцать минут"),
    ("agent_msg", "таймер пошёл"),
    ("user_msg", "напомни полить рассаду вечером"),
    ("agent_msg", "напомню в семь"),
    ("user_msg", "что по новостям, коротко?"),
    ("agent_msg", "ничего срочного, всё спокойно"),
]

FILLER_SENSOR = [
    "presence: away",
    "presence: present",
    "movement: прихожая",
    "presence: away",
]

PROBE_TOPICS = {
    "b01": "собаку", "b02": "звонки с незнакомых номеров",
    "b03": "полив рассады", "b04": "дату олимпиады (какой она была сначала)",
    "b05": "мои вечера в начале месяца", "b06": "приезд мамы",
    "b07": "ремонт балкона", "b08": "плитку", "b09": "мою еду",
    "b10": "напоминания о проверке тетрадей", "b11": "расписание консультаций",
    "b12": "справку для бассейна", "b13": "мнение завуча о моих оценках",
    "b14": "как я отношусь к замечаниям завуча", "b15": "прежнее расписание кружка",
    "b16": "незнакомца у калитки", "b17": "актуальное расписание кружка",
    "b18": "как шёл ремонт", "b19": "здоровье мамы", "b20": "как я добираюсь",
    "b21": "актуальную дату олимпиады", "b22": "как выступил класс",
    "b23": "испанский", "b24": "утренние аудиоуроки в последнее время",
    "b25": "уход за собакой", "b26": "мой режим продуктивности",
}

TWIN = ("b11", "b12",
        "Два обещания висели: расписание консультаций и справка для бассейна. Кто кому что обещал?",
        "расписание обещала владелица агенту; справку для бассейна обещал агент владелице",
        "расписание|бассейн")
