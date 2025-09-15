import re
import math
from bs4 import BeautifulSoup

CURIOSITY = [
    "you won't believe", "what happened next", "what happens next", "shocking",
    "goes viral", "stuns", "mind-blowing", "insane", "unbelievable", "must see",
    "everything you need to know", "the truth about", "finally revealed", "exposed",
    "destroys", "slams", "wrecks", "roasts", "obliterates", "meltdown",
    "no one is talking about"
]

MORAL_EMO = {
    "outrage","corrupt","betrayal","disgusting","shame","traitor","evil",
    "furious","shocking","meltdown","slammed","savage","canceled","woke",
    "snowflake","annihilate","hate","liar","stupid","gaslighting"
}

SENSATIONAL = {
    "epic","ultimate","insane","jaw-dropping","unreal","wild","viral","shocking",
    "crazy","bananas","blazing","explosive","massive","huge","incredible"
}

LISTICLE_PATTERN = re.compile(r"\b(\d{1,2})\b\s+(things|ways|reasons|tips|facts|signs|lessons)\b", re.I)

def strip_html(text: str) -> str:
    if not text:
        return ""
    try:
        return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
    except Exception:
        # fallback: remove tags
        return re.sub(r"<[^>]+>", " ", text)

def ratio_allcaps(s: str) -> float:
    if not s:
        return 0.0
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c.isupper())/len(letters)

def punct_bursts(s: str) -> float:
    bursts = re.findall(r"[!?]{2,}", s or "")
    return math.tanh(len(bursts)/3.0)

def contains_curiosity(s: str) -> float:
    s2 = (s or "").lower()
    hits = sum(1 for phrase in CURIOSITY if phrase in s2)
    return min(1.0, hits / 2.0)

def sensational_ratio(s: str) -> float:
    toks = re.findall(r"[a-zA-Z']+", (s or "").lower())
    if not toks: return 0.0
    hits = sum(1 for t in toks if t in SENSATIONAL)
    return math.tanh(hits / 5.0)

def moral_emotion_hits(s: str) -> float:
    toks = re.findall(r"[a-zA-Z']+", (s or "").lower())
    hits = sum(1 for t in toks if t in MORAL_EMO)
    return math.tanh(hits / 5.0)

def second_person_attack(s: str) -> float:
    return 1.0 if re.search(r"\byou\b.*\b(liar|stupid|evil|idiot)\b", (s or "").lower()) else 0.0

def listicle_signal(s: str) -> float:
    return 1.0 if LISTICLE_PATTERN.search(s or "") else 0.0

def clickbait_score(headline: str, summary: str) -> float:
    """Heuristic 0..1; >0.6 is likely clickbait"""
    h = headline or ""
    sum_txt = strip_html(summary or "")
    score = (
        0.30*contains_curiosity(h) +
        0.15*listicle_signal(h) +
        0.15*ratio_allcaps(h) +
        0.15*punct_bursts(h) +
        0.15*sensational_ratio(h + " " + sum_txt) +
        0.10*(1.0 if re.search(r"\b(click|watch)\b", (h + " " + sum_txt).lower()) else 0.0)
    )
    return max(0.0, min(1.0, score))

def ragebait_score(headline: str, body: str) -> float:
    """Heuristic 0..1; >0.5 is likely rage-bait"""
    h = headline or ""
    score = (
        0.35*ratio_allcaps(h) +
        0.20*punct_bursts(h) +
        0.30*moral_emotion_hits(h + " " + (body or "")) +
        0.15*second_person_attack(h)
    )
    return max(0.0, min(1.0, score))

def truthiness_score(clickbait: float, ragebait: float) -> float:
    """Simple fusion for MVP: 100 is best."""
    bad = 70.0*clickbait + 30.0*ragebait
    return max(0.0, 100.0 - bad)
