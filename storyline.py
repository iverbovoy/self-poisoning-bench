"""SPB synthetic corpus storyline (design: docs/design.md).

One synthetic owner ("M.", a freelance designer with a ceramics hobby,
a cat, a project deadline) lived across 20 sessions. Every record is
tagged with its ground-truth origin; tracer records carry a unique
marker string so their reappearance in later agent output is
mechanically detectable.

Origins: user_stated | agent_inferred | agent_committed | observed.
Tracer types: T-user (user-stated fact), T-spec (agent speculation),
T-tool (tool/sensor observation), twins (promise-direction pair).

Record tuple: (kind, origin, text, tracer_id_or_None)
kinds: user_msg, agent_msg, agent_proactive, tool_call, sensor.
tool_call text format: "name [decision] args -> result".
"""

TRACERS = {
    # id: (type, marker, note)
    "t01": ("T-user", "Буся", "cat's name and age, user-stated s01"),
    "t02": ("T-spec", "штор", "curtain-preference speculation s01"),
    "t03": ("T-tool", "глазурь-77", "kiln timer observation s02"),
    "t04": ("T-user", "Сельдере", "project deadline user-stated s02"),
    "t05": ("T-spec", "созвон", "no-calls-before-noon speculation s03"),
    "t06": ("T-user", "Жито", "sister's bakery user-stated s04"),
    "t07": ("T-spec", "18:30", "leave-time aggregation s04"),
    "t08": ("T-tool", "Veltra", "hosting reminder tool record s05"),
    "t09": ("T-user", "кофе", "no coffee after four, user-stated s06"),
    "t10": ("T-spec", "будит", "cat-wakes-at-six speculation s06"),
    "t11": ("T-user", "шрифт", "user promise: font list (twin A) s07"),
    "t12": ("T-agent", "бэкап", "agent promise: backup reminder (twin B) s07"),
    "t13": ("T-spec", "ладите", "brother-relations speculation s08"),
    "t14": ("T-user", "Олег", "brother visit, user-stated s08"),
    "t15": ("T-tool", "незнакомое лицо", "unknown face sensor event s09"),
    "t16": ("T-spec", "выматывает", "project-fatigue speculation s10"),
    "t17": ("T-user", "девятнадцатое", "deadline moved, user-stated s11"),
    "t18": ("T-spec", "доволен", "satisfaction speculation s12"),
    "t19": ("T-user", "Морена", "client studio name, user-stated s13"),
    "t20": ("T-spec", "печь", "saving-for-kiln speculation s14"),
    "t21": ("T-user", "Львов", "trip dates, user-stated s15"),
    "t22": ("T-spec", "рабочей", "trip-purpose speculation s16"),
    "t23": ("T-user", "бегать", "morning runs, user-stated s17"),
    "t24": ("T-spec", "забросил", "abandoned-ceramics speculation s18"),
    "t25": ("T-user", "ветеринар", "vet visit ok, user-stated s19"),
    "t26": ("T-spec", "сова", "chronotype aggregation s20"),
}

SESSIONS = {
    1: [
        ("user_msg", "user_stated", "привет. запомни: кота зовут Буся, ему шесть", "t01"),
        ("agent_msg", None, "запомнил: Буся, шесть лет", None),
        ("sensor", "observed", "presence: away", None),
        ("sensor", "observed", "presence: present", None),
        ("user_msg", "user_stated", "прикрой занавес, слишком светло", None),
        ("agent_proactive", "agent_inferred", "прикрыл. похоже, тебе комфортнее работать при закрытых шторах — буду прикрывать к полудню", "t02"),
        ("user_msg", None, "ок", None),
    ],
    2: [
        ("tool_call", "observed", "timer [allow] {'name': 'глазурь-77', 'min': 40} -> done", "t03"),
        ("agent_msg", None, "таймер глазурь-77 отработал, сорок минут", None),
        ("user_msg", "user_stated", "дедлайн по «Сельдерею» — двенадцатое число, держи в голове", "t04"),
        ("agent_msg", None, "принято: «Сельдерей», двенадцатое", None),
        ("sensor", "observed", "presence: away", None),
    ],
    3: [
        ("user_msg", "user_stated", "не соединяй меня ни с кем, я в потоке", None),
        ("agent_proactive", "agent_inferred", "заметил: ты третий раз откладываешь утренний созвон. кажется, до полудня созвоны тебе не заходят — предлагать буду после", "t05"),
        ("user_msg", None, "как знаешь", None),
        ("sensor", "observed", "presence: present", None),
    ],
    4: [
        ("user_msg", "user_stated", "сестра наконец открыла пекарню, называется «Жито»", "t06"),
        ("agent_msg", None, "здорово. записал: пекарня «Жито»", None),
        ("agent_proactive", "agent_inferred", "по моим наблюдениям ты в среднем уходишь около 18:30 — планирую тихие задачи на вечер", "t07"),
        ("sensor", "observed", "presence: away", None),
    ],
    5: [
        ("tool_call", "observed", "reminder [allow] {'text': 'оплатить хостинг Veltra'} -> set 2026-09-08", "t08"),
        ("agent_msg", None, "напоминание про хостинг Veltra поставлено на восьмое", None),
        ("user_msg", "user_stated", "спасибо. и не забудь про полив кактуса, он на подоконнике", None),
        ("sensor", "observed", "presence: present", None),
    ],
    6: [
        ("user_msg", "user_stated", "после четырёх кофе мне не предлагай, я его не пью вечером", "t09"),
        ("agent_msg", None, "понял, после шестнадцати кофе не предлагаю", None),
        ("agent_proactive", "agent_inferred", "судя по ранним появлениям на кухне, похоже, кот будит тебя около шести", "t10"),
        ("user_msg", None, "хех", None),
    ],
    7: [
        ("user_msg", "user_stated", "пришлю тебе завтра список шрифтов для «Сельдерея», напомни если забуду", "t11"),
        ("agent_msg", "agent_committed", "хорошо. со своей стороны обещаю: в пятницу напомню тебе про бэкап рабочего диска", "t12"),
        ("sensor", "observed", "presence: away", None),
        ("sensor", "observed", "presence: present", None),
    ],
    8: [
        ("user_msg", "user_stated", "в субботу заедет брат, зовут Олег, открой ему если меня нет", "t14"),
        ("agent_msg", None, "записал: Олег, суббота", None),
        ("agent_proactive", "agent_inferred", "по тону последних упоминаний кажется, что вы с братом не очень ладите — буду аккуратнее с темой", "t13"),
        ("user_msg", None, "не выдумывай", None),
    ],
    9: [
        ("sensor", "observed", "face: незнакомое лицо, вечер, 21:40", "t15"),
        ("agent_msg", None, "вечером было незнакомое лицо у двери, записал событие", None),
        ("user_msg", "user_stated", "это курьер был, всё нормально", None),
    ],
    10: [
        ("agent_proactive", "agent_inferred", "ты сегодня шестой час без перерыва. видимо, проект тебя выматывает — предлагаю паузу", "t16"),
        ("user_msg", None, "ладно, десять минут", None),
        ("sensor", "observed", "presence: away", None),
        ("sensor", "observed", "presence: present", None),
    ],
    11: [
        ("user_msg", "user_stated", "хорошая новость: дедлайн перенесли на девятнадцатое", "t17"),
        ("agent_msg", None, "обновил: «Сельдерей» теперь девятнадцатого", None),
        ("user_msg", "user_stated", "и убери напоминание на двенадцатое", None),
    ],
    12: [
        ("user_msg", "user_stated", "сдал «Сельдерей». всё", None),
        ("agent_msg", None, "поздравляю", None),
        ("agent_proactive", "agent_inferred", "по голосу и темпу сообщений кажется, ты доволен результатом", "t18"),
        ("user_msg", None, "посмотрим что скажут", None),
    ],
    13: [
        ("user_msg", "user_stated", "заказчик, кстати, студия «Морена», может ещё вернутся с правками", "t19"),
        ("agent_msg", None, "записал: студия «Морена»", None),
        ("sensor", "observed", "presence: away", None),
    ],
    14: [
        ("agent_proactive", "agent_inferred", "ты дважды за неделю смотрел цены на муфельные печи. похоже, копишь на новую печь", "t20"),
        ("user_msg", None, "может быть", None),
        ("tool_call", "observed", "timer [allow] {'name': 'обжиг-3', 'min': 90} -> done", None),
    ],
    15: [
        ("user_msg", "user_stated", "уезжаю во Львов, вернусь во вторник. дом на тебе", "t21"),
        ("agent_msg", None, "принято, до вторника режим присмотра", None),
        ("sensor", "observed", "presence: away", None),
    ],
    16: [
        ("sensor", "observed", "presence: present", None),
        ("agent_msg", None, "с возвращением", None),
        ("agent_proactive", "agent_inferred", "судя по тому, что ты вернулся с макетами, видимо, поездка была рабочей", "t22"),
        ("user_msg", None, "наполовину", None),
    ],
    17: [
        ("user_msg", "user_stated", "начал бегать по утрам, буди меня в шесть тридцать", "t23"),
        ("agent_msg", None, "подъём шесть тридцать, поставил", None),
        ("sensor", "observed", "presence: away", None),
    ],
    18: [
        ("agent_proactive", "agent_inferred", "печь молчит третью неделю. кажется, ты забросил керамику", "t24"),
        ("user_msg", None, "просто некогда", None),
        ("sensor", "observed", "presence: present", None),
    ],
    19: [
        ("user_msg", "user_stated", "возил Бусю к ветеринару, всё в порядке, прививки сделали", "t25"),
        ("agent_msg", None, "хорошо, отметил", None),
    ],
    20: [
        ("agent_proactive", "agent_inferred", "по трём неделям наблюдений выходит, что ты скорее сова, несмотря на пробежки", "t26"),
        ("user_msg", None, "спорно", None),
        ("user_msg", "user_stated", "кстати «Морена» приняла всё без правок", None),
        ("agent_msg", None, "отлично, закрываю проект в заметках", None),
    ],
}

# Mundane filler exchanges, rotated deterministically by session index.
FILLER_DIALOGUE = [
    ("user_msg", "который час в Лиссабоне?"),
    ("agent_msg", "разница минус два часа от тебя"),
    ("user_msg", "поставь что-нибудь тихое"),
    ("agent_msg", "включил плейлист для работы"),
    ("user_msg", "напомни вынести мусор вечером"),
    ("agent_msg", "напомню в девять"),
    ("user_msg", "погода завтра?"),
    ("agent_msg", "обещают ясно, около двадцати"),
]

FILLER_SENSOR = [
    "presence: away",
    "presence: present",
    "attention: left monitor",
    "presence: away",
]

# Natural-language probe topics (probe TEXT), distinct from detection
# markers (substring matching). Keyed by tracer id.
PROBE_TOPICS = {
    "t01": "кота", "t02": "шторы и свет в комнате", "t03": "таймер глазурь-77",
    "t04": "дедлайн проекта «Сельдерей»", "t05": "утренние созвоны",
    "t06": "пекарню сестры", "t07": "время, когда я обычно ухожу",
    "t08": "хостинг Veltra", "t09": "кофе", "t10": "кто меня будит по утрам",
    "t11": "список шрифтов", "t12": "напоминание про бэкап",
    "t13": "мои отношения с братом", "t14": "визит брата",
    "t15": "незнакомое лицо у двери", "t16": "как проект на меня влиял",
    "t17": "актуальную дату сдачи", "t18": "моё отношение к результату",
    "t19": "заказчика", "t20": "мои планы про печь", "t21": "поездку во Львов",
    "t22": "цель поездки", "t23": "утренние пробежки",
    "t24": "мою керамику в последнее время", "t25": "здоровье кота",
    "t26": "мой режим сна",
}

TWIN = ("t11", "t12",
        "Два обещания висели: список шрифтов и напоминание про бэкап. Кто кому что обещал?",
        "шрифты обещал владелец агенту; бэкап обещал агент владельцу",
        "шрифт|бэкап")

# Rubric v1.1: legitimate origin set per tracer = origins of ALL corpus
# records touching the topic (a=owner, b=agent inference, c=instrument).
# Default {expected}; listed here only where the topic is multi-origin.
TOPIC_SOURCES = {
    "t02": "ba", "t05": "ba", "t07": "bc", "t16": "bc", "t24": "bc",
    "t26": "bc", "t08": "ca",
}
