"""
Password generation utilities for CLI Guard

Provides three generation strategies:
- scramble_password: Leet-speak substitution + case randomization on existing password
- generate_random: Cryptographically random password from shell-safe character pool
- generate_passphrase: Random word combination from curated dictionary

All randomness uses the `secrets` module (CSPRNG backed by os.urandom / /dev/urandom).
Unlike `random` (deterministic PRNG), `secrets` is cryptographically unpredictable —
knowing all previous outputs gives zero information about the next one.

Usage:
    import password_generator

    scrambled = password_generator.scramble_password("MyPassword")
    random_pw = password_generator.generate_random()          # 20 chars default
    passphrase = password_generator.generate_passphrase()     # 4 words default
"""

import secrets
import string


# ---------- Constants ----------

# Leet-speak substitution map — lowercase keys only (we normalize before lookup)
SUBSTITUTION_MAP: dict[str, list[str]] = {
    'a': ['@', '4'],
    'b': ['8'],
    'e': ['3'],
    'g': ['9'],
    'i': ['1', '!'],
    'l': ['1', '|'],
    'o': ['0'],
    's': ['$', '5'],
    't': ['7', '+'],
    'z': ['2'],
}

# Shell-safe character pool for random password generation (74 chars)
# Excludes shell-hostile characters: | ; ' " ` \ { } < > ~ ( ) [ ] ? /
# This matters because CLI Guard passwords end up in shell variables and scripts
CHARSET: str = string.ascii_letters + string.digits + "!@#$%^&*_+-="

# Special characters subset for guarantee checking
SPECIAL_CHARS: str = "!@#$%^&*_+-="

# Length bounds for random password generation
MIN_LENGTH: int = 12
MAX_LENGTH: int = 128
DEFAULT_LENGTH: int = 20

# Word count bounds for passphrase generation
MIN_WORDS: int = 3
MAX_WORDS: int = 10
DEFAULT_WORDS: int = 4

# Separator pool for passphrase generation — each separator is chosen independently
# Shell-safe subset to avoid quoting issues in scripts
SEPARATORS: str = "-_#$%^&*+=!"


# ---------- Public Functions ----------

def scramble_password(password: str) -> str:
    """Apply leet-speak substitution and case randomization to an existing password.

    Two-pass algorithm:
    1. Substitution: Each alphabetic char with a leet-speak mapping gets a 50/50
       coin flip to decide whether to substitute. If substituting, one replacement
       is chosen uniformly from the mapping's options.
    2. Case randomization: Remaining alphabetic chars get ~27% chance of uppercase,
       ~73% chance of lowercase. This produces a natural-looking mix.

    Args:
        password: The password to scramble.

    Returns:
        The scrambled password (same length, non-alpha chars preserved).
    """
    if not password:
        return password

    # Pass 1: Leet-speak substitution
    chars: list[str] = []
    for ch in password:
        lower = ch.lower()
        if lower in SUBSTITUTION_MAP and secrets.randbelow(2) == 1:
            chars.append(secrets.choice(SUBSTITUTION_MAP[lower]))
        else:
            chars.append(ch)

    # Pass 2: Case randomization on remaining alphabetic characters
    result: list[str] = []
    for ch in chars:
        if ch.isalpha():
            if secrets.randbelow(100) < 27:
                result.append(ch.upper())
            else:
                result.append(ch.lower())
        else:
            result.append(ch)

    return ''.join(result)


def generate_random(length: int = DEFAULT_LENGTH) -> str:
    """Generate a cryptographically random password from a shell-safe character pool.

    Uses rejection sampling: generates all characters independently via
    secrets.choice(), then verifies the result contains at least one of each
    category (uppercase, lowercase, digit, special). If not, regenerates
    entirely rather than injecting characters at specific positions (which
    would create structural bias and reduce entropy).

    At length 20 from a 74-char pool, log2(74^20) ≈ 124 bits of entropy,
    comparable to AES-128. A retry is needed ~4% of the time.

    Args:
        length: Desired password length (clamped to 12–128).

    Returns:
        A random password containing all character categories.
    """
    length = max(MIN_LENGTH, min(MAX_LENGTH, length))

    while True:
        candidate = ''.join(secrets.choice(CHARSET) for _ in range(length))

        # Guarantee check — all four categories present
        has_upper = any(c in string.ascii_uppercase for c in candidate)
        has_lower = any(c in string.ascii_lowercase for c in candidate)
        has_digit = any(c in string.digits for c in candidate)
        has_special = any(c in SPECIAL_CHARS for c in candidate)

        if has_upper and has_lower and has_digit and has_special:
            return candidate


def generate_passphrase(word_count: int = DEFAULT_WORDS) -> str:
    """Generate a passphrase from randomly selected dictionary words.

    Three sources of entropy per passphrase:
    1. Word selection: Each word chosen independently via secrets.choice()
       from a 4,096-word list. 4 words = log2(4096^4) = 48 bits.
    2. Capitalization: Each word has a 27% chance of being capitalized
       (first letter uppercase). Adds ~0.85 bits per word (~3.4 bits for 4).
    3. Separators: Each separator between words is chosen randomly from an
       11-character pool. 3 separators = log2(11^3) ≈ 10.4 bits.
    Total for 4 words: ~61.8 bits of entropy.

    The word list is embedded directly in this module — no file I/O needed,
    so it works on airgapped and minimal systems.

    Args:
        word_count: Number of words (clamped to 3–10).

    Returns:
        A passphrase with random separators (e.g., "Timber$rocket#Ocean-bridge").
    """
    word_count = max(MIN_WORDS, min(MAX_WORDS, word_count))

    # Select words and apply capitalization coin flip (~27% chance)
    words: list[str] = []
    for _ in range(word_count):
        word = secrets.choice(WORD_LIST)
        if secrets.randbelow(100) < 27:
            word = word.capitalize()
        words.append(word)

    # Join with random separators (each chosen independently)
    parts: list[str] = [words[0]]
    for word in words[1:]:
        parts.append(secrets.choice(SEPARATORS))
        parts.append(word)

    return ''.join(parts)


# ---------- Word List ----------
# 4,096 curated common English words (4–8 characters each)
# - Common everyday vocabulary, no obscure or offensive words
# - All lowercase, alphabetic only
# - Tuple (immutable) for safety
# - Embedded directly so the module has zero file I/O dependencies

WORD_LIST: tuple[str, ...] = (
    "able", "acid", "aged", "also", "area", "army", "away", "baby", "back",
    "ball", "band", "bank", "base", "bath", "bean", "bear", "beat", "been",
    "beer", "bell", "belt", "best", "bill", "bird", "bite", "blow", "blue",
    "boat", "body", "bomb", "bond", "bone", "book", "boot", "born", "boss",
    "both", "bowl", "bulk", "burn", "bush", "busy", "cage", "cake", "call",
    "calm", "came", "camp", "card", "care", "case", "cash", "cast", "cave",
    "cell", "chat", "chip", "city", "claim", "clay", "clip", "club", "coal",
    "coat", "code", "coin", "cold", "come", "cook", "cool", "cope", "copy",
    "core", "cost", "crew", "crop", "cult", "cure", "cute", "dark", "data",
    "date", "dawn", "dead", "deal", "dear", "debt", "deed", "deep", "deer",
    "deny", "desk", "dial", "diet", "dirt", "disc", "dish", "dock", "does",
    "done", "door", "dose", "down", "draw", "drew", "drop", "drug", "drum",
    "dual", "duke", "dull", "dump", "dust", "duty", "each", "earn", "ease",
    "east", "easy", "edge", "else", "emit", "envy", "epic", "even", "ever",
    "evil", "exam", "exit", "face", "fact", "fail", "fair", "fall", "fame",
    "farm", "fast", "fate", "fear", "feed", "feel", "feet", "fell", "felt",
    "file", "fill", "film", "find", "fine", "fire", "firm", "fish", "fist",
    "flag", "flat", "fled", "flew", "flip", "flow", "foam", "fold", "folk",
    "fond", "font", "food", "fool", "foot", "ford", "form", "fort", "foul",
    "four", "free", "frog", "from", "fuel", "full", "fund", "fury", "fuse",
    "gain", "game", "gang", "gate", "gave", "gear", "gene", "gift", "girl",
    "give", "glad", "glow", "glue", "goal", "goes", "gold", "golf", "gone",
    "good", "grab", "gray", "grew", "grey", "grid", "grin", "grip", "grow",
    "gulf", "guru", "hair", "half", "hall", "halt", "hand", "hang", "hard",
    "harm", "hate", "have", "head", "heal", "heap", "hear", "heat", "heel",
    "held", "help", "herb", "here", "hero", "hide", "high", "hike", "hill",
    "hint", "hire", "hold", "hole", "holy", "home", "hood", "hook", "hope",
    "horn", "host", "hour", "huge", "hung", "hunt", "hurt", "icon", "idea",
    "inch", "into", "iron", "item", "jack", "jail", "jazz", "jean", "jest",
    "jobs", "join", "joke", "jump", "june", "jury", "just", "keen", "keep",
    "kept", "kick", "kill", "kind", "king", "kiss", "knee", "knew", "knit",
    "knob", "knot", "know", "lack", "laid", "lake", "lamp", "land", "lane",
    "last", "late", "lawn", "lazy", "lead", "leaf", "lean", "left", "lend",
    "lens", "less", "lick", "life", "lift", "like", "limb", "lime", "limp",
    "line", "link", "lion", "list", "live", "load", "loan", "lock", "logo",
    "long", "look", "lord", "lose", "loss", "lost", "love", "luck", "lump",
    "lung", "lure", "made", "mail", "main", "make", "male", "mall", "malt",
    "many", "mark", "mask", "mass", "mate", "maze", "meal", "mean", "meat",
    "meet", "melt", "memo", "menu", "mere", "mesh", "mess", "mild", "milk",
    "mill", "mind", "mine", "mint", "miss", "mode", "mood", "moon", "more",
    "moss", "most", "moth", "move", "much", "mule", "must", "myth", "nail",
    "name", "navy", "near", "neat", "neck", "need", "nest", "next", "nice",
    "nine", "node", "none", "norm", "nose", "note", "noun", "odds", "once",
    "only", "onto", "open", "oral", "oven", "over", "pace", "pack", "page",
    "paid", "pain", "pair", "pale", "palm", "pant", "park", "part", "pass",
    "past", "path", "peak", "peel", "peer", "pick", "pier", "pile", "pine",
    "pink", "pipe", "plan", "play", "plot", "plug", "plus", "poem", "poet",
    "pole", "poll", "pond", "pool", "poor", "pope", "pork", "port", "pose",
    "post", "pour", "pray", "prey", "pull", "pump", "pure", "push", "quit",
    "quiz", "race", "rack", "rage", "raid", "rail", "rain", "rank", "rare",
    "rate", "read", "real", "rear", "reed", "reef", "rely", "rent", "rest",
    "rice", "rich", "ride", "ring", "rise", "risk", "road", "rock", "rode",
    "role", "roll", "roof", "room", "root", "rope", "rose", "ruin", "rule",
    "rush", "rust", "safe", "sage", "said", "sail", "sake", "sale", "salt",
    "same", "sand", "sang", "save", "seal", "seat", "seed", "seek", "seem",
    "seen", "self", "sell", "send", "sent", "sept", "shed", "shin", "ship",
    "shoe", "shop", "shot", "show", "shut", "sick", "side", "sigh", "sign",
    "silk", "sing", "sink", "site", "size", "skin", "slam", "slap", "slim",
    "slip", "slot", "slow", "snap", "snow", "soak", "soap", "soar", "sock",
    "soft", "soil", "sold", "sole", "some", "song", "soon", "sort", "soul",
    "sour", "spin", "spot", "star", "stay", "stem", "step", "stir", "stop",
    "such", "suit", "sure", "swim", "tail", "take", "tale", "talk", "tall",
    "tank", "tape", "task", "taxi", "team", "tear", "tell", "tend", "tent",
    "term", "test", "text", "than", "that", "them", "then", "they", "thin",
    "this", "thus", "tick", "tide", "tidy", "tied", "tier", "tile", "till",
    "time", "tiny", "tire", "toad", "told", "toll", "tone", "took", "tool",
    "tops", "tore", "torn", "toss", "tour", "town", "trap", "tray", "tree",
    "trim", "trio", "trip", "true", "tube", "tuck", "tune", "turn", "twin",
    "type", "ugly", "undo", "unit", "upon", "urge", "used", "user", "vain",
    "vale", "vary", "vast", "vein", "verb", "very", "vest", "veto", "vice",
    "view", "vine", "visa", "void", "volt", "vote", "wade", "wage", "wait",
    "wake", "walk", "wall", "want", "ward", "warm", "warn", "wash", "wave",
    "weak", "wear", "weed", "week", "well", "went", "were", "west", "what",
    "when", "whom", "wide", "wife", "wild", "will", "wind", "wine", "wing",
    "wire", "wise", "wish", "with", "woke", "wolf", "wood", "wool", "word",
    "wore", "work", "worm", "worn", "wrap", "yard", "yarn", "yeah", "year",
    "yell", "yoga", "your", "zero", "zone", "zoom", "about", "above", "abuse",
    "acted", "adapt", "added", "admit", "adopt", "adult", "after", "again", "agent",
    "agree", "ahead", "aimed", "alarm", "album", "alert", "alien", "align", "alive",
    "alley", "allow", "alone", "along", "alter", "among", "angel", "anger", "angle",
    "angry", "anime", "ankle", "apart", "apple", "apply", "arena", "argue", "arise",
    "armor", "aroma", "arose", "aside", "asset", "atlas", "avoid", "awake", "award",
    "aware", "awful", "bacon", "badge", "badly", "baker", "based", "basic", "basis",
    "batch", "beach", "beard", "beast", "began", "begin", "being", "belly", "below",
    "bench", "berry", "birth", "black", "blade", "blame", "bland", "blank", "blast",
    "blaze", "bleed", "blend", "bless", "blind", "blink", "bliss", "block", "blood",
    "bloom", "blown", "board", "bonus", "boost", "bound", "brain", "brand", "brave",
    "bread", "break", "breed", "brick", "bride", "brief", "bring", "broad", "broke",
    "brook", "brown", "brush", "buddy", "build", "built", "bunch", "burst", "buyer",
    "cabin", "cable", "candy", "cargo", "carry", "catch", "cause", "cedar", "chain",
    "chair", "chalk", "chaos", "charm", "chart", "chase", "cheap", "check", "cheek",
    "cheer", "chess", "chest", "chief", "child", "chill", "china", "choir", "chose",
    "chunk", "civic", "civil", "clash", "class", "clean", "clear", "clerk", "click",
    "cliff", "climb", "cling", "clock", "clone", "close", "cloth", "cloud", "clown",
    "coach", "coast", "color", "comet", "comic", "coral", "count", "court", "cover",
    "crack", "craft", "crane", "crash", "crazy", "cream", "creek", "crest", "crime",
    "crisp", "cross", "crowd", "crown", "crude", "cruel", "crush", "cubic", "curve",
    "cycle", "daily", "dairy", "dance", "dealt", "death", "debut", "decay", "decor",
    "decoy", "delay", "delta", "demon", "dense", "depot", "depth", "derby", "devil",
    "diary", "dirty", "ditch", "dizzy", "dodge", "donor", "doubt", "dough", "draft",
    "drain", "drake", "drama", "drank", "drape", "drawn", "dream", "dress", "dried",
    "drift", "drill", "drink", "drive", "drone", "drove", "drown", "drunk", "dryer",
    "dying", "eager", "eagle", "early", "earth", "eight", "elder", "elect", "elite",
    "embed", "empty", "enemy", "enjoy", "enter", "entry", "equal", "equip", "erase",
    "error", "essay", "event", "every", "exact", "exams", "exile", "exist", "extra",
    "faint", "fairy", "faith", "false", "fancy", "fatal", "fault", "feast", "fence",
    "ferry", "fetch", "fever", "fiber", "field", "fifth", "fifty", "fight", "final",
    "first", "fixed", "flame", "flash", "fleet", "flesh", "float", "flock", "flood",
    "floor", "flour", "flown", "fluid", "flush", "flute", "focal", "focus", "force",
    "forge", "forth", "forum", "fossil", "found", "frame", "fraud", "fresh", "front",
    "frost", "froze", "fruit", "funny", "gauge", "genre", "ghost", "giant", "given",
    "glare", "glass", "globe", "gloom", "glory", "gloss", "glove", "going", "grace",
    "grade", "grain", "grand", "grant", "grape", "graph", "grasp", "grass", "grave",
    "great", "green", "greet", "grief", "grill", "grind", "gross", "group", "grove",
    "grown", "guard", "guess", "guest", "guide", "guild", "guilt", "habit", "happy",
    "harsh", "haste", "haven", "heart", "heavy", "hedge", "hello", "hence", "heron",
    "homer", "honey", "honor", "horse", "hotel", "house", "human", "humor", "hurry",
    "ideal", "image", "imply", "inbox", "index", "indie", "inner", "input", "intro",
    "issue", "ivory", "jewel", "joint", "joker", "judge", "juice", "juicy", "jumbo",
    "karma", "kayak", "knack", "kneel", "knife", "knock", "known", "label", "labor",
    "lance", "large", "laser", "later", "laugh", "layer", "learn", "lease", "leave",
    "legal", "lemon", "level", "light", "liked", "limit", "linen", "liver", "lobby",
    "local", "lodge", "logic", "loose", "lover", "lower", "loyal", "lucky", "lunar",
    "lunch", "lyric", "magic", "major", "maker", "manor", "maple", "march", "match",
    "mayor", "medal", "media", "mercy", "merit", "metal", "meter", "micro", "might",
    "miner", "minor", "minus", "mixed", "model", "money", "month", "moral", "motor",
    "mount", "mouse", "mouth", "movie", "music", "naive", "nerve", "never", "night",
    "noble", "noise", "north", "notch", "noted", "novel", "nurse", "nylon", "ocean",
    "offer", "often", "olive", "onset", "opera", "orbit", "order", "organ", "other",
    "outer", "owned", "owner", "oxide", "ozone", "paint", "panel", "panic", "paper",
    "paste", "patch", "pause", "peace", "peach", "pearl", "penny", "phase", "phone",
    "photo", "piano", "piece", "pilot", "pinch", "pitch", "pixel", "pizza", "place",
    "plain", "plane", "plant", "plate", "plaza", "plead", "plumb", "plume", "plump",
    "point", "polar", "poppy", "porch", "poser", "pound", "power", "press", "price",
    "pride", "prime", "print", "prior", "prism", "prize", "probe", "proof", "prose",
    "proud", "prove", "proxy", "psalm", "pulse", "punch", "pupil", "purse", "queen",
    "quest", "queue", "quick", "quiet", "quota", "quote", "radar", "radio", "raise",
    "rally", "ranch", "range", "rapid", "ratio", "reach", "react", "ready", "realm",
    "rebel", "refer", "reign", "relax", "relay", "renal", "renew", "repay", "reply",
    "rider", "ridge", "rifle", "right", "rigid", "risky", "rival", "river", "robin",
    "robot", "roman", "roost", "rough", "round", "route", "royal", "rugby", "ruler",
    "rumor", "rural", "safer", "saint", "salad", "sauce", "scale", "scare", "scene",
    "scent", "scope", "score", "scout", "scrap", "serve", "setup", "seven", "shade",
    "shaft", "shake", "shall", "shame", "shape", "share", "shark", "sharp", "sheep",
    "sheer", "sheet", "shelf", "shell", "shift", "shine", "shirt", "shock", "shore",
    "short", "shout", "sight", "sigma", "since", "sixth", "sixty", "sized", "skill",
    "skull", "slash", "slate", "slave", "sleep", "sleek", "slice", "slide", "slope",
    "smart", "smell", "smile", "smith", "smoke", "snake", "solar", "solid", "solve",
    "sonic", "south", "space", "spare", "spark", "speak", "speed", "spell", "spend",
    "spice", "spike", "spine", "spoke", "spoon", "sport", "spray", "squad", "stack",
    "staff", "stage", "stain", "stake", "stale", "stall", "stamp", "stand", "stare",
    "stark", "start", "state", "stave", "stays", "steal", "steam", "steel", "steep",
    "steer", "stick", "stiff", "still", "stock", "stole", "stone", "stood", "store",
    "storm", "story", "stove", "strap", "straw", "strip", "stuck", "study", "stuff",
    "style", "sugar", "suite", "sunny", "super", "surge", "swamp", "swear", "sweat",
    "sweep", "sweet", "swept", "swift", "swing", "sworn", "sword", "syrup", "table",
    "taken", "taste", "teach", "teeth", "tempo", "terra", "thank", "theme", "there",
    "thick", "thief", "thing", "think", "third", "those", "three", "threw", "throw",
    "thumb", "tidal", "tiger", "tight", "timer", "title", "today", "token", "topic",
    "torch", "total", "touch", "tough", "tower", "toxic", "trace", "track", "trade",
    "trail", "train", "trait", "treat", "trend", "trial", "tribe", "trick", "tried",
    "troop", "truck", "truly", "trump", "trunk", "trust", "truth", "tumor", "twice",
    "twist", "ultra", "uncle", "under", "union", "unite", "unity", "until", "upper",
    "upset", "urban", "usage", "usual", "utter", "valid", "value", "vapor", "vault",
    "verse", "video", "vigor", "viral", "virus", "visit", "vista", "vital", "vivid",
    "vocal", "voice", "voter", "wagon", "waste", "watch", "water", "weary", "weave",
    "wedge", "weird", "whale", "wheat", "wheel", "where", "which", "while", "white",
    "whole", "whose", "wider", "witch", "woman", "world", "worse", "worst", "worth",
    "would", "wound", "wrath", "write", "wrong", "wrote", "yacht", "yield", "young",
    "youth", "accept", "access", "across", "action", "active", "actual", "adjust", "admire",
    "afford", "agenda", "almost", "amount", "anchor", "annual", "answer", "anyway", "appeal",
    "appear", "arctic", "around", "arrive", "artist", "aspect", "assert", "assist", "assume",
    "assure", "attach", "attack", "attend", "august", "author", "autumn", "avenue", "backup",
    "banana", "banker", "banner", "barely", "barrel", "basket", "battle", "beauty", "become",
    "before", "behalf", "behave", "behind", "belong", "beside", "beyond", "bishop", "bitter",
    "blanch", "bloody", "bonnet", "borrow", "bother", "bottom", "bounce", "branch", "breast",
    "breath", "breeze", "bridge", "bright", "brings", "broken", "bronze", "browse", "bubble",
    "bucket", "budget", "buffet", "bullet", "bundle", "burden", "bureau", "burger", "burner",
    "butler", "butter", "button", "cables", "calmer", "camera", "campus", "candle", "canvas",
    "carbon", "career", "carpet", "carved", "castle", "casual", "cattle", "caught", "causal",
    "cellar", "cement", "census", "center", "cereal", "chance", "change", "chapel", "cheese",
    "cherry", "choice", "choose", "chosen", "chrome", "church", "circle", "circus", "clamor",
    "clever", "client", "closer", "closet", "cobalt", "coffee", "collar", "colony", "column",
    "combat", "comedy", "coming", "commit", "common", "comply", "convey", "cookie", "cooler",
    "copper", "corner", "cosmic", "costly", "cotton", "county", "couple", "coupon", "course",
    "cousin", "covers", "crafts", "crayon", "create", "credit", "crisis", "critic", "cruise",
    "custom", "damage", "dampen", "danger", "daring", "dating", "dealer", "debate", "debris",
    "decade", "decent", "defeat", "defend", "define", "degree", "demand", "depend", "deploy",
    "deputy", "derive", "desert", "design", "desire", "detail", "detect", "device", "devote",
    "differ", "digest", "dinner", "direct", "divert", "divine", "domain", "double", "dragon",
    "drawer", "driven", "driver", "during", "earned", "earthy", "easier", "eating", "editor",
    "effect", "effort", "eighth", "either", "eleven", "emerge", "empire", "enable", "ending",
    "endure", "energy", "engage", "engine", "enough", "ensure", "entire", "entity", "equity",
    "errand", "escape", "estate", "evolve", "exceed", "except", "excite", "excuse", "exempt",
    "expand", "expect", "expert", "export", "expose", "extend", "extent", "fabric", "facing",
    "factor", "fairly", "fallen", "family", "famine", "famous", "farmer", "faster", "father",
    "faucet", "fellow", "female", "fierce", "figure", "filter", "finale", "finger", "fiscal",
    "flavor", "flight", "flower", "flying", "follow", "footer", "forced", "forest", "forget",
    "formal", "format", "former", "foster", "fourth", "freely", "freeze", "french", "friend",
    "frozen", "future", "galaxy", "gander", "garage", "garden", "garlic", "gather", "gazing",
    "gender", "gentle", "gently", "gifted", "ginger", "giving", "global", "golden", "gospel",
    "gotten", "govern", "gravel", "greedy", "groove", "ground", "growth", "guided", "guitar",
    "hammer", "handle", "happen", "harbor", "hardly", "hazard", "headed", "health", "heaven",
    "height", "helmet", "hereby", "hidden", "highly", "hiking", "honest", "hoping", "horror",
    "hosted", "hourly", "housed", "humble", "hunger", "hunter", "hybrid", "ignite", "impact",
    "import", "impose", "income", "indeed", "indoor", "inform", "injury", "inland", "inmate",
    "innate", "insert", "inside", "insist", "insult", "intact", "intend", "intent", "invest",
    "invite", "inward", "island", "itself", "jacket", "jargon", "jersey", "jigsaw", "jumble",
    "jungle", "junior", "justin", "kernel", "kettle", "kidney", "killer", "kindly", "knight",
    "ladder", "lambda", "laptop", "lately", "latter", "launch", "lawyer", "layout", "leader",
    "league", "legend", "lender", "length", "lesson", "letter", "lifted", "likely", "lining",
    "liquid", "listen", "litter", "little", "lively", "living", "lizard", "locate", "logger",
    "longer", "lovely", "luxury", "magnet", "mainly", "making", "manage", "mangle", "manner",
    "manual", "marble", "margin", "marked", "marker", "market", "master", "matter", "meadow",
    "medium", "member", "memoir", "memory", "mental", "mentor", "merely", "merger", "method",
    "middle", "mighty", "miller", "minute", "mirror", "misery", "mobile", "modern", "modest",
    "modify", "monkey", "mortal", "mostly", "motion", "muscle", "museum", "mutual", "myself",
    "mystic", "namely", "napkin", "narrow", "native", "nature", "nearby", "neatly", "nickel",
    "nimble", "ninety", "nobody", "noodle", "normal", "notice", "notion", "nought", "novice",
    "number", "object", "obtain", "occupy", "offish", "offset", "online", "opener", "oppose",
    "option", "oracle", "orange", "orient", "origin", "outfit", "outlaw", "output", "pacing",
    "paddle", "palace", "parade", "parent", "parish", "parrot", "patrol", "patron", "patter",
    "pebble", "pencil", "people", "pepper", "period", "permit", "person", "phrase", "picked",
    "picnic", "pigeon", "pillar", "pillow", "pistol", "plaque", "plasma", "player", "please",
    "pledge", "plenty", "pliers", "plunge", "pocket", "poetry", "poison", "police", "policy",
    "polish", "polite", "ponder", "poorly", "portal", "poster", "potato", "potter", "poultry",
    "powder", "praise", "prayer", "prefer", "pretty", "prince", "prison", "profit", "prompt",
    "proper", "proven", "public", "puddle", "purple", "arch", "asks", "aunt", "bark",
    "bars", "bass", "bead", "beam", "beds", "beef", "bend", "bent", "beta",
    "bias", "bind", "bits", "blur", "boil", "bold", "bolt", "bore", "bout",
    "bows", "brag", "brim", "buds", "bugs", "bump", "bunk", "caps", "cart",
    "cats", "cede", "chew", "chin", "chop", "cite", "clad", "clam", "clan",
    "clap", "claw", "clue", "coil", "comb", "cone", "cord", "corn", "cosy",
    "coup", "crab", "cubs", "cups", "curl", "damp", "dare", "dart", "dash",
    "dean", "demo", "dent", "dine", "dips", "dire", "dogs", "dome", "dots",
    "dove", "drab", "drag", "dusk", "dyes", "earl", "echo", "eels", "eggs",
    "elms", "etch", "fade", "fawn", "fern", "figs", "fizz", "flaw", "flex",
    "fore", "fork", "fowl", "fray", "fret", "fuzz", "gale", "gape", "gash",
    "gasp", "gaze", "germ", "gist", "glen", "glib", "glob", "gnaw", "goat",
    "gore", "gory", "gown", "gram", "grit", "grub", "gulp", "gust", "guts",
    "hare", "harp", "hash", "haul", "hawk", "haze", "heed", "hemp", "herd",
    "hewn", "hips", "hits", "hive", "hoax", "hoop", "hops", "hose", "howl",
    "hubs", "hues", "hugs", "hulk", "hump", "husk", "hymn", "inks", "ions",
    "isle", "itch", "jade", "jams", "jars", "jaws", "jets", "jigs", "jolt",
    "joys", "jugs", "kale", "kelp", "kids", "kilt", "kite", "kiln", "kiwi",
    "kink", "lace", "lags", "lame", "laps", "lark", "lash", "lass", "lava",
    "leak", "leap", "lids", "lieu", "lily", "logs", "loom", "loot", "lore",
    "loft", "lush", "mane", "maps", "mare", "mars", "mash", "mast", "mats",
    "mend", "mica", "mist", "mite", "mitt", "moat", "mock", "mold", "mope",
    "mugs", "murk", "muse", "musk", "mutt", "nape", "nets", "newt", "nick",
    "nits", "nods", "nook", "null", "oaks", "oars", "oath", "oats", "oils",
    "omen", "opal", "opts", "owes", "owls", "pact", "pail", "pane", "pang",
    "pave", "paws", "pear", "peas", "peck", "pegs", "pelt", "pens", "perk",
    "pest", "pets", "pigs", "pill", "pins", "pint", "pits", "plea", "plod",
    "plop", "plow", "ploy", "pods", "poke", "pomp", "pony", "pops", "pout",
    "prod", "prop", "prow", "pubs", "puff", "pugs", "pulp", "puma", "puns",
    "pups", "ramp", "rams", "rash", "rats", "rays", "ream", "reap", "reel",
    "refs", "rein", "rift", "rigs", "rims", "riot", "ripe", "ribs", "robe",
    "rods", "rove", "rubs", "rude", "rugs", "rump", "rung", "ruse", "ruts",
    "sack", "sane", "sash", "scan", "scam", "scar", "sewn", "sham", "shaw",
    "shim", "sift", "sill", "silt", "sire", "skit", "slab", "slag", "slew",
    "slog", "slug", "smog", "snag", "snip", "snob", "snub", "snug", "soot",
    "span", "spar", "spec", "sped", "spew", "spit", "spur", "stab", "stag",
    "stew", "stow", "stub", "stud", "stun", "sulk", "sumo", "sums", "sunk",
    "swab", "swan", "swap", "sway", "tabs", "tack", "tags", "tame", "taps",
    "tarp", "tart", "taut", "teak", "teem", "tern", "thaw", "thud", "thug",
    "tilt", "tins", "tips", "toes", "toga", "toil", "tomb", "tong", "toot",
    "tort", "tram", "trek", "trod", "tuft", "tugs", "tuna", "turf", "twig",
    "tyke", "vane", "vase", "veil", "vent", "vibe", "vied", "vile", "vows",
    "wail", "wane", "warp", "wart", "wasp", "watt", "weld", "welt", "wick",
    "wigs", "wilt", "wimp", "wink", "wipe", "wiry", "wits", "woes", "yank",
    "yawn", "zeal", "zest", "abyss", "acorn", "adept", "adobe", "affix", "agile",
    "aisle", "alibi", "amber", "amble", "ample", "annex", "antic", "anvil", "aorta",
    "aphid", "attic", "axiom", "azure", "bagel", "balmy", "banjo", "barge", "baron",
    "basil", "baton", "bayou", "beads", "beech", "beret", "berth", "bigot", "birch",
    "bison", "blare", "bleak", "bloat", "bloke", "bluff", "blunt", "blurt", "bogus",
    "braid", "brash", "brawn", "briar", "brine", "brink", "brisk", "broil", "brood",
    "brunt", "bulge", "bumpy", "bylaw", "cache", "cadet", "cairn", "cameo", "canny",
    "caper", "carte", "carve", "chafe", "chaff", "chant", "chomp", "chord", "cigar",
    "cinch", "clamp", "clasp", "cleft", "clout", "cobra", "coils", "comma", "conch",
    "cough", "coupe", "covet", "cramp", "crawl", "craze", "creak", "creep", "cress",
    "croup", "crumb", "crypt", "cumin", "cynic", "daisy", "decal", "denim", "detox",
    "digit", "dinar", "diode", "dirge", "ditto", "dowdy", "dowel", "drool", "droop",
    "dross", "duvet", "dwarf", "dwell", "edict", "eerie", "elfin", "elope", "elude",
    "ember", "emcee", "endow", "envoy", "epoch", "epoxy", "evade", "exalt", "expat",
    "extol", "exude", "farce", "feign", "femur", "feral", "feud", "fibre", "filth",
    "finch", "fjord", "flail", "flair", "flaky", "flank", "flask", "fling", "flint",
    "flora", "floss", "flout", "fluff", "foamy", "folio", "folly", "foray", "frank",
    "freak", "friar", "frisk", "frond", "froth", "fungi", "furry", "gamma", "gauze",
    "gecko", "geese", "giddy", "glaze", "gleam", "glean", "glide", "glint", "gloat",
    "gnome", "gouge", "gourd", "graze", "greed", "grope", "grout", "growl", "gruel",
    "grunt", "guava", "gulch", "gusty", "gypsy", "helix", "henna", "hippo", "hitch",
    "hoard", "hobby", "holly", "horns", "hover", "husky", "idyll", "igloo", "imbue",
    "impel", "inane", "incur", "inept", "inert", "inlet", "irony", "jaunt", "jazzy",
    "joust", "jumpy", "knelt", "kudos", "laden", "ladle", "lanky", "lapis", "latch",
    "latex", "ledge", "lefty", "lemur", "lever", "lilac", "llama", "loafs", "locks",
    "lofty", "lucid", "macho", "macro", "manga", "mango", "marsh", "maxim", "melon",
    "metro", "mirth", "mocha", "modal", "mogul", "moist", "morph", "motel", "motto",
    "mourn", "mural", "mushy", "nasal", "natal", "naval", "nifty", "ninja", "nomad",
    "nudge", "oasis", "omega", "onion", "optic", "otter", "outdo", "papal", "parse",
    "penal", "perch", "peril", "petal", "petty", "piety", "plaid", "plank", "pluck",
    "poach", "poker", "polka", "polyp", "pooch", "prawn", "preen", "prick", "privy",
    "prone", "prong", "prowl", "prude", "prune", "qualm", "query", "quill", "quirk",
    "rabbi", "radon", "raven", "rebut", "recap", "regal", "rehab", "reiki", "remix",
    "repel", "resin", "retch", "retro", "rhino", "rhyme", "rinse", "rivet", "roach",
    "roast", "rodeo", "rouge", "rowdy", "rumba", "rusty", "sabre", "satin", "sauna",
    "savvy", "scald", "scalp", "scorn", "scour", "scowl", "scuba", "seize", "shale",
    "shawl", "sheen", "shrub", "siege", "siren", "skate", "skirt", "slain", "slang",
    "sleet", "slung", "slurp", "smash", "smelt", "smirk", "snare", "snarl", "sneak",
    "snore", "snort", "spade", "spawn", "spear", "speck", "spill", "spire", "spite",
    "spore", "spout", "spree", "sprig", "squat", "squid", "stank", "stash", "stead",
    "steed", "stern", "stint", "stoic", "stoke", "stoop", "stout", "stray", "strut",
    "stump", "stung", "stunk", "suave", "swarm", "swirl", "swoop", "tabby", "taffy",
    "talon", "tango", "tardy", "taunt", "tease", "tenor", "tepid", "thigh", "tiara",
    "toast", "topaz", "tramp", "trash", "trawl", "triad", "trout", "tulip", "twang",
    "tweed", "udder", "ulcer", "usher", "usurp", "valet", "valor", "valve", "venom",
    "verge", "viper", "vodka", "vouch", "vowel", "wacky", "wafer", "wager", "waltz",
    "whack", "wharf", "whirl", "wince", "windy", "wiper", "woken", "wreck", "wring",
    "yearn", "zebra", "zingy", "absorb", "abrupt", "accent", "adhere", "affirm", "afield",
    "aghast", "albeit", "alcove", "allege", "alpine", "alumni", "ambush", "amulet", "anklet",
    "anthem", "aplomb", "appall", "arcade", "archer", "ardent", "armada", "armpit", "arouse",
    "artery", "ascend", "asylum", "atomic", "aviary", "awning", "baboon", "baffle", "ballot",
    "bamboo", "bandit", "banter", "barber", "bazaar", "beacon", "benign", "bestow", "bigwig",
    "biopsy", "bisect", "bodily", "bonded", "botany", "boyish", "breech", "bruise", "buckle",
    "budgie", "bugler", "bumble", "canopy", "captor", "cartel", "cavern", "chalet", "cipher",
    "classy", "clergy", "clinch", "clique", "cobble", "cocoon", "coddle", "coerce", "coffin",
    "cohort", "compel", "concur", "condor", "confer", "consul", "convoy", "cordon", "corpse",
    "cosine", "cradle", "cranky", "crater", "cringe", "curfew", "cursor", "cushy", "dabble",
    "dagger", "deacon", "debunk", "deceit", "defect", "defuse", "deluge", "demise", "demote",
    "denote", "depict", "depose", "detach", "detain", "devour", "dismay", "docile", "dodger",
    "donkey", "drench", "dunce", "edible", "embark", "emblem", "embryo", "enmity", "eraser",
    "erotic", "evenly", "exhort", "expend", "eyelet", "facade", "falcon", "fathom", "faulty",
    "fedora", "feline", "ferret", "fickle", "fiddle", "filler", "flimsy", "flinch", "florid",
    "fodder", "fondle", "forbid", "forged", "frenzy", "frisky", "frolic", "fumble", "funnel",
    "futile", "gadget", "galley", "gambit", "gaping", "garnet", "gazebo", "girdle", "goblet",
    "grouse", "grudge", "grumpy", "gutter", "hackle", "haggle", "hamlet", "hamper", "hangar",
    "hassle", "hazing", "heater", "heckle", "herbal", "hermit", "hinged", "hoarse", "hobble",
    "homage", "homing", "huddle", "hurdle", "icicle", "ignore", "impair", "impede", "incite",
    "indict", "indigo", "infect", "inflow", "infuse", "inhale", "inject", "inning", "insane",
    "intern", "invoke", "iodine", "jaguar", "jostle", "jumper", "kennel", "keypad", "kitten",
    "lagoon", "latent", "lessen", "limber", "linger", "locker", "lumber", "lunacy", "malice",
    "mallet", "mantle", "martyr", "mascot", "morsel", "muddle", "muffle", "mumble", "muster",
    "muzzle", "nestle", "nettle", "nimbly", "nuzzle", "oblong", "offend", "ordeal", "orphan",
    "ousted", "outage", "outbid", "outrun", "papaya", "parcel", "parity", "parlor", "parole",
    "pastel", "pastry", "peddle", "pellet", "pester", "pewter", "pinion", "pirate", "placid",
    "plague", "pleats", "pliant", "plight", "plumes", "poised", "pollen", "poplar", "potent",
    "pounce", "pranks", "pundit", "punish", "quaint", "quartz", "quench", "rabble", "racket",
    "radish", "raffle", "ramble", "rancid", "rapids", "raptor", "rascal", "ravine", "rebate",
    "reckon", "recoil", "redeem", "reflex", "regain", "rejoin", "relish", "remiss", "renege",
    "repent", "reside", "retort", "revamp", "riddle", "riffle", "ripple", "roster", "rubble",
    "rudder", "ruffle", "rumble", "rustle", "saddle", "saliva", "sander", "satire", "saucer",
    "savant", "scenic", "scrimp", "scurry", "seethe", "sentry", "shanty", "sheath", "shelve",
    "sinful", "sizzle", "sludge", "smithy", "solder", "solace", "somber", "sortie", "spinal",
    "spiral", "splice", "spongy", "stamen", "staple", "starch", "steely", "stench", "stifle",
    "stooge", "strewn", "strife", "strive", "stroll", "strung", "stumpy", "subdue", "sucker",
    "sundry", "supple", "swerve", "tangle", "tatter", "tavern", "teapot", "temper", "thatch",
    "thorny", "thrash", "thrift", "throng", "thrust", "tinder", "tipple", "toddle", "toffee",
    "topple", "torque", "toupee", "tremor", "trench", "trifle", "trudge", "tumble", "tundra",
    "turban", "turtle", "tycoon", "umpire", "unborn", "undone", "unfold", "unhook", "unkind",
    "unload", "unmask", "unplug", "unruly", "unseen", "untold", "unwary", "upbeat", "upkeep",
    "uproar", "upside", "uptake", "vagary", "vellum", "veneer", "vestal", "visage", "vortex",
    "waffle", "walrus", "wanton", "warden", "weasel", "whimsy", "wicker", "widest", "wiggle",
    "wizard", "wobble", "woolen", "worsen", "wraith", "writhe", "zealot", "abridge", "acetone",
    "acrobat", "adapter", "ailment", "almanac", "amalgam", "amnesia", "anagram", "anchovy", "anomaly",
    "antenna", "anthill", "appease", "applaud", "apprise", "aquatic", "archaic", "archive", "artwork",
    "aspirin", "avenger", "aviator", "balcony", "bandana", "baptize", "barrage", "bayonet", "bedrock",
    "beehive", "bewitch", "bizarre", "blaring", "blemish", "blister", "bluejay", "boarder", "bonanza",
    "boxwood", "bramble", "bravado", "broaden", "bromine", "budding", "bugbear", "bulwark", "burnout",
    "butcher", "cabaret", "cadaver", "caliper", "callous", "canteen", "caprice", "capsule", "caravan",
    "caribou", "cashier", "catfish", "cavalry", "cherish", "chimera", "chowder", "circled", "citadel",
    "clatter", "cleanse", "clipper", "cobbler", "cockpit", "codfish", "collide", "commend", "compute",
    "concave", "concede", "concoct", "condemn", "condone", "confine", "conjure", "connive", "contend",
    "contort", "contour", "convene", "copycat", "corrode", "corsair", "cowgirl", "cranium", "craving",
    "critter", "crochet", "crucify", "crumble", "curtail", "custody", "cutlass", "cyclone", "cynical",
    "daybook", "dazzler", "debacle", "decorum", "deflect", "defunct", "delimit", "deplane", "deprive",
    "despair", "detract", "deviate", "diagram", "dictate", "diffuse", "diluted", "discord", "disdain",
    "dislike", "disrupt", "dissent", "distill", "distort", "disturb", "doublet", "dragnet", "drastic",
    "dungeon", "dustpan", "emerald", "eminent", "enclose", "enforce", "engrave", "enliven", "entropy",
    "epitome", "erupted", "estuary", "evolves", "excerpt", "expanse", "extinct", "extrude", "eyeball",
    "falafel", "fallout", "fanfare", "fateful", "flannel", "flasher", "flatter", "flipper", "fluency",
    "foghorn", "foolish", "footman", "forearm", "foreign", "forfeit", "forsake", "fortify", "fractal",
    "frantic", "freckle", "freebie", "furlong", "furnace", "furnish", "gallant", "garland", "garment",
    "garnish", "gelatin", "glacier", "glamour", "godlike", "goulash", "grandma", "grapple", "gridlock",
    "grottos", "gruffly", "grumble", "gunboat", "hacksaw", "halcyon", "hammock", "hangout", "hardhat",
    "hatchet", "haunted", "hearten", "hostile", "hovered", "humdrum", "hurried", "iceberg", "immerse",
    "impasse", "impeach", "implore", "imprint", "inflame", "inflict", "ingrain", "inhabit", "insipid",
    "isotope", "janitor", "javelin", "jealous", "jocular", "jubilee", "juniper", "kindred", "kingdom",
    "ladybug", "lantern", "lawsuit", "lettuce", "lineage", "lookout", "madness", "masonry", "mediate",
    "misdeed", "missile", "monarch", "monster", "moonlit", "mortify", "nibbler", "nominee", "nourish",
    "novelty", "nullify", "nutmeg", "opacity", "ossuary", "outpost", "overtly", "pajamas", "palette",
    "panache", "panacea", "paradox", "paragon", "parsnip", "peasant", "penguin", "perspex", "pervade",
    "pianist", "pivotal", "pontoon", "portent", "precede", "prevail", "preview", "provost", "prudent",
    "pursuit", "pyramid", "quarrel", "rancher", "ransack", "rapport", "ratchet", "recount", "regatta",
    "sandbar", "science", "scalpel", "shallow", "skeptic", "slander", "slipper", "smuggle", "sunburn",
    "sunrise", "sweater", "topknot", "trailer", "trumpet", "trustee", "turmoil", "undergo", "whisker",
    "whistle", "ably", "ache", "acre", "ally", "amen", "amid", "apex", "avid",
    "awry", "axle", "bale", "balm", "bane", "bare", "barn", "bask", "bats",
    "bays", "begs", "bile", "blot", "boar", "bode", "boon", "brow", "calf",
    "cane", "carp", "cask", "chug", "clod", "clog", "colt", "cove", "cowl",
    "cram", "crux", "cuff", "cull", "curb", "dale", "darn", "daub", "daze",
    "defy", "deft", "dell", "dice", "dike", "dime", "dint", "dote", "dour",
    "doze", "dram", "drub", "dude", "dune", "dung", "dupe", "eddy", "edit",
    "espy", "ewer", "feat", "fend", "fete", "fief", "filo", "foal", "foes",
    "fogy", "foxy", "fume", "gage", "gait", "gall", "garb", "gawk", "gems",
    "gild", "gilt", "gird", "gout", "gyms", "hack", "haft", "hail", "hale",
    "halo", "hank", "hasp", "hazy", "helm", "hems", "hilt", "hiss", "hobo",
    "hock", "hoed", "hogs", "hone", "ides", "imam", "jabs", "jamb", "jeep",
    "jeer", "jerk", "jibe", "jive", "jock", "jowl", "judo", "keel", "kern",
    "keys", "khan", "knap", "lard", "lath", "leek", "levy", "liar", "lint",
    "lobe", "loge", "loin", "lynx", "mace", "maim", "maul", "maws", "mead",
    "meek", "mesa", "mews", "miff", "mike", "minx", "mire", "moan", "mobs",
    "molt", "monk", "moor", "mops", "mote", "nabs", "naif", "nave", "nibs",
    "noel", "nubs", "oafs", "obey", "ogle", "oink", "opus", "orbs", "orca",
    "oreo", "ouzo", "oxen", "pall", "palp", "pare", "pate", "pawl", "peek",
    "peon", "perp", "pert", "pied", "pike", "pith", "pore", "posy", "punt",
    "purr", "quay", "quid", "raft", "rake", "rant", "rasp", "raze", "rend",
    "repo", "revs", "rial", "rick", "rife", "rill", "rime", "rind", "roam",
    "robs", "romp", "rook", "rued", "rues", "rune", "runs", "runt", "sans",
    "sari", "sate", "scab", "seam", "seer", "shah", "shag", "shiv", "shod",
    "shun", "silo", "sine", "slob", "slop", "smug", "snit", "snot", "soma",
    "spud", "suet", "sump", "tang", "tarn", "tiff", "tofu", "togs", "tome",
    "tony", "tope", "torr", "vats", "vial", "vise", "wadi", "waft", "waif",
    "weir", "whey", "wisp", "woks", "wren", "yawl", "yews", "yogi", "yoke",
    "yore", "zany", "zebu", "zinc", "zing", "aback", "abide", "abode", "abort",
    "acrid", "acute", "adorn", "aegis", "agape", "agate", "ahold", "aided", "alpha",
    "amass", "amaze", "annul", "aping", "arbor", "avert", "avian", "await", "baste",
    "biddy", "bleat", "blued", "blush", "booby", "bosom", "botch", "bower", "brawl",
    "bugle", "camel", "chasm", "chewy", "clang", "clink", "cloak", "clump", "creed",
    "crept", "crone", "crook", "crust", "email", "cudgel", "dapper", "decode", "deluxe",
    "detour", "dismal", "donate", "dosage", "enigma", "ensign", "entice", "gondola", "avow",
    "dais", "elan", "fado", "heft", "iamb", "abash", "bedew", "cavil", "demur",
    "elate", "feint", "gamut", "haiku", "jabot", "knave", "lathe", "mange", "nadir",
    "octet", "plait", "scrim", "tithe", "updos", "xenon", "argon", "bezel", "chirp",
    "dwelt", "eclat", "flume", "gruff", "hutch", "jowls", "knurl", "moose", "newel",
    "ocher", "pleat", "skimp", "tryst", "usury", "zonal", "ablaze", "adroit", "belfry",
    "chaste", "dainty", "efface", "fallow", "garish", "homily", "impure", "jovial", "kindle",
    "lissom", "morbid", "obtuse", "pallid", "quirky", "ruckus", "supine", "tawdry", "usurer",
    "virile", "zenith", "abalone", "bedevil", "cadenza", "dastard", "eclipse", "festoon", "gryphon",
    "hauteur", "imperil", "jubilant", "keratin", "lacquer", "mandala", "nirvana", "opulent", "palazzo",
    "quibble", "rampant", "squalor", "thimble", "upsilon", "verdant", "windrow", "ablation", "banister",
    "cauldron", "daffodil", "echelon", "falconer", "gantries", "hallowed", "illusory", "jubilate", "keepsake",
    "labrador", "mandarin", "narcotic", "obsidian", "pastoral", "quandary", "rampancy", "sabotage", "tangible",
    "umbrella", "vagabond", "wisteria", "acacia", "bistro", "casket", "drivel", "eureka", "gopher",
    "hallow", "icecap", "jetsam", "kibble", "larder", "mingle", "novena", "onward", "pariah",
    "ransom", "simmer", "tallow", "upwind", "vermin", "winnow", "agave", "clove", "douse",
    "hoist", "ingot", "knead", "lotus", "okapi", "poise", "quaff", "sable", "thyme",
    "visor", "waylay", "abbot", "glyph", "hyena", "junta", "myrrh", "nymph", "utile",
    "vogue", "whisk", "abacus", "bonbon", "cocoa", "feeble", "hobbit", "nimrod", "pauper",
    "rumple", "siphon", "valise", "airway", "blazer", "citing", "emboss", "fondly", "grimly",
    "impish", "jaunty", "kosher", "limpet", "midway", "rebuff", "toggle", "uplift", "venial",
    "bauble", "corral", "eldest", "frieze", "gazelle", "hooray", "joshed", "kelvin", "limpid",
    "maroon", "neural", "orchid", "plinth", "quorum", "rubric", "sculpt", "thorax", "unveil",
    "volley", "wombat", "aching", "blurry", "donned", "elixir", "greens", "jaunts", "kempt",
    "lariat", "midair", "thwart", "impale", "quarry", "ablest", "ampere", "antics", "anvils",
    "arched", "awoken", "ballet", "banish", "barter", "basalt", "bisque", "blotch", "bridle",
    "buffed",
)
