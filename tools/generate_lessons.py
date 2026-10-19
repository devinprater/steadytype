
"""Generate the SteadyType course. Every task character must be taught already."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / "content" / "lessons"

KEY_TIPS = {
 "a": "A is under your left little finger, on the home row.",
 "s": "S is under your left ring finger.",
 "d": "D is under your left middle finger.",
 "f": "F is under your left index finger. It has a small bump.",
 "j": "J is under your right index finger. It has a bump too, so your hands can find home without looking.",
 "k": "K is under your right middle finger.",
 "l": "L is under your right ring finger.",
 ";": "The semicolon is at the right end of the home row, under your right little finger.",
 "e": "E sits on the top row, above D. Reach up with your left middle finger and come straight back.",
 "i": "I sits above K. Reach up with your right middle finger.",
 "r": "R is above F. Your left index finger reaches up and slightly left.",
 "u": "U is above J. Your right index finger reaches up and slightly left.",
 "t": "T is above F and G. The left index finger moves up and right.",
 "y": "Y is above J and H. The right index finger moves up and left.",
 "w": "W is above S. Reach up with the left ring finger.",
 "o": "O is above L. Reach up with the right ring finger.",
 "q": "Q is at the far left of the top row, above A. The left little finger reaches up.",
 "p": "P is at the far right of the top row, above the semicolon. The right little finger reaches up.",
 "v": "V is below F. Curl the left index finger down.",
 "m": "M is below J. Curl the right index finger down.",
 "c": "C is below D. The left middle finger drops down.",
 "n": "N is below J. The right index finger reaches down and left.",
 "x": "X is below S. Drop the left ring finger down.",
 "z": "Z is at the bottom left, below A. The left little finger curls down.",
 "b": "B is below F and G. The left index finger reaches down and right.",
 "g": "G is on the home row between F and H. The left index finger slides right.",
 "h": "H is between G and J. The right index finger slides left.",
 ",": "The comma is to the right of M. Press it with the right middle finger.",
 ".": "The period is to the right of the comma. The right ring finger presses it.",
 "?": "The question mark is Shift and the slash key, at the bottom right.",
 "!": "The exclamation mark is Shift and the 1 key.",
 "'": "The apostrophe is to the right of the semicolon, under the right little finger.",
 '"': "The quotation mark is Shift and the apostrophe key.",
 ":": "The colon is Shift and the semicolon.",
 "-": "The hyphen is to the right of the 0 key.",
 "(": "The open parenthesis is Shift and 9.",
 ")": "The close parenthesis is Shift and 0.",
 "shift": "Shift is held with the little finger on the side opposite the letter.",
}
for digit in "0123456789":
    KEY_TIPS[digit] = f"{digit} is on the number row. Reach with the finger that owns the key below it, then come home."

for symbol in "@#$%^&*_=+[]{}|/\\":
    KEY_TIPS.setdefault(symbol, f"{symbol} uses Shift. Learn where it sits, then press it without looking down.")

MODE_TIPS = {
 "keys": "Press it, say its name in your head, and return to the home row.",
 "words": "Now use it inside real words. Keep your eyes on the screen, not your hands.",
 "phrases": "Two words at a time. Let the space bar carry you between them.",
 "sentences": "Whole sentences now. Read a little ahead while your fingers follow.",
 "punctuated": "Punctuation belongs to the sentence. Type it without breaking your rhythm.",
 "capitals": "Hold Shift with the little finger opposite the letter, press, then let go.",
 "names": "Names start with a capital. Shift, letter, release.",
 "numbers": "Reach from the home row and come straight back.",
 "symbols": "Symbols mean Shift. Learn the pair, then use it in a line.",
}

ENCOURAGEMENT = [
 "Slow and even beats fast and jumpy.",
 "If you miss a key, keep going. The next one matters more than the last.",
 "Only the finger that reaches should move. The rest of your hand stays home.",
 "Accuracy first. Speed arrives on its own.",
 "A short pause and a shake of the hands every few minutes keeps them loose.",
]

UNITS = {
 1: "Keep your fingers on the home row and come back to it after every reach.",
 2: "Reach up with one finger, then return to the home row.",
 3: "The top row is a short reach. Do not lift the whole hand.",
 4: "The bottom row curls your fingers down. Keep your wrists still.",
 5: "Hold Shift with the little finger opposite the letter.",
 6: "Punctuation is a normal key press. Say the mark to yourself as you type.",
 7: "Numbers come from the top row. Reach, press, and return.",
 8: "Symbols use Shift. Learn one pair at a time.",
 9: "Now put it together at a steady pace you can keep.",
}

WORDS = ["a", "an", "as", "at", "is", "it", "in", "if", "of", "on", "or", "to", "up", "us", "do", "go", "so", "no", "my", "by", "be", "we", "he", "me", "am", "and", "the", "you", "are", "for", "not", "but", "all", "can", "had", "has", "her", "his", "how", "its", "may", "new", "now", "old", "one", "our", "out", "see", "she", "two", "was", "who", "why", "will", "with", "this", "that", "from", "have", "they", "what", "when", "your", "them", "then", "than", "some", "time", "like", "make", "made", "come", "came", "more", "most", "over", "only", "also", "back", "after", "work", "first", "well", "even", "want", "because", "these", "think", "where", "being", "under", "never", "other", "right", "still", "found", "every", "great", "might", "shall", "those", "while", "again", "place", "small", "large", "house", "world", "hand", "land", "kind", "mind", "find", "line", "life", "live", "give", "gave", "take", "took", "look", "book", "good", "food", "room", "soon", "door", "side", "city", "near", "year", "day", "way", "say", "said", "part", "keep", "help", "must", "such", "much", "very", "name", "same", "home", "long", "last", "left", "just", "know", "into", "down", "done", "open", "read", "word", "turn", "move", "play", "run", "stop", "start", "learn", "write", "type", "key", "row", "fast", "cold", "hot", "map", "car", "sun", "water", "desk", "page", "team", "class", "quiet", "whole", "note", "list", "short"]

SENTENCES = [
 "the cat sat on the mat.", "we can see the sun.", "she has a red hat.",
 "he is at home.", "they can read and write.", "the dog ran to the door.",
 "i can type this now.", "you know the home row.", "we will work as a team.",
 "the sun is hot.", "this is a good day.", "keep your hands on the keys.",
 "look at the screen.", "the text is on the line.", "we must take our time.",
 "the room is quiet.", "she said hello to me.", "he will come with us.",
 "they are in the same class.", "the man has a map.", "the boy can run fast.",
 "i saw the red car.", "we need more time.", "the water is cold.",
 "she can help you.", "the book is on the desk.", "he read the whole page.",
 "they went out the door.", "the day was long.", "my hand is on the key.",
 "the line is not long.", "we can start at once.", "the first task is done.",
 "keep the pace you can hold.", "the world is large.", "the city is near.",
]

PUNCTUATED = [
 "well, that is done.", "it's a good day.", '"come in," she said.',
 "where is the key?", "stop!", 'he said: "wait."',
 "the list is short; the day is long.", "(see the note.)",
 "a well-known name.", "the first day, the best day.",
 "she asked, \"can you type this?\"", "yes, i can!",
]

CAPITAL = [
 "The cat sat on the mat.", "We can see the sun.", "She has a red hat.",
 "He is at home.", "They can read and write.", "Devin can type this now.",
 "Ann and Sam are in the same class.", "My name is Devin.",
 "The dog ran to the door.", "We will work as a team.",
]

# (unit, title, teaches, mode)
PLAN = [
 (1,"Home row review",[";"],"words"),
 (1,"Home row short phrases",[";"],"phrases"),
 (1,"Home row check",[";"],"words"),
 (2,"The letter E",["e"],"keys"),
 (2,"The letter I",["i"],"keys"),
 (2,"The letter R",["r"],"keys"),
 (2,"The letter U",["u"],"keys"),
 (2,"E and I words",["e","i"],"words"),
 (2,"R and U words",["r","u"],"words"),
 (2,"Top row mix",["e","i","r","u"],"words"),
 (2,"Top row phrases",["e","i","r","u"],"phrases"),
 (3,"The letter T",["t"],"keys"),
 (3,"The letter Y",["y"],"keys"),
 (3,"The letter W",["w"],"keys"),
 (3,"The letter O",["o"],"keys"),
 (3,"The letter Q",["q"],"keys"),
 (3,"The letter P",["p"],"keys"),
 (3,"Top row words",["t","y","w","o","q","p"],"words"),
 (3,"Top row sentences",["t","y","w","o","q","p"],"sentences"),
 (4,"The letter V",["v"],"keys"),
 (4,"The letter M",["m"],"keys"),
 (4,"The letter C",["c"],"keys"),
 (4,"The letter N",["n"],"keys"),
 (4,"The letter X",["x"],"keys"),
 (4,"The letter Z",["z"],"keys"),
 (4,"The letter B",["b"],"keys"),
 (4,"The letters G and H",["g","h"],"keys"),
 (5,"Shift and capitals A to D",["shift","A","B","C","D"],"capitals"),
 (5,"Capitals E to H",["E","F","G","H"],"capitals"),
 (5,"Capitals I to L",["I","J","K","L"],"capitals"),
 (5,"Capitals M to P",["M","N","O","P"],"capitals"),
 (5,"Capitals Q to U",["Q","R","S","T","U"],"capitals"),
 (5,"Capitals V to Z",["V","W","X","Y","Z"],"capitals"),
 (5,"Names",["A","B","C","D","E","F","G","H","I","J","K","L","M"],"names"),
 (5,"Starting a sentence",["."],"capitals"),
 (6,"The comma and period",[",","."],"punctuated"),
 (6,"The question mark",["?"],"punctuated"),
 (6,"The exclamation mark",["!"],"punctuated"),
 (6,"The apostrophe",["'"],"punctuated"),
 (6,"Quotation marks",['"'],"punctuated"),
 (6,"Colon and semicolon",[":",";"],"punctuated"),
 (6,"Hyphen and parentheses",["-","(",")"],"punctuated"),
 (6,"Punctuation review",["?","!"],"punctuated"),
 (7,"Four and five",["4","5"],"numbers"),
 (7,"Six and seven",["6","7"],"numbers"),
 (7,"Three and eight",["3","8"],"numbers"),
 (7,"Two and nine",["2","9"],"numbers"),
 (7,"One and zero",["1","0"],"numbers"),
 (7,"Number rows",["0","9"],"numbers"),
 (7,"Dates and times",["1","2"],"numbers"),
 (7,"Number review",["5","6"],"numbers"),
 (8,"Exclamation and question",["!","?"],"symbols"),
 (8,"At and hash",["@","#"],"symbols"),
 (8,"Dollar and percent",["$","%"],"symbols"),
 (8,"Caret and ampersand",["^","&"],"symbols"),
 (8,"Asterisk and open parenthesis",["*","("],"symbols"),
 (8,"Close parenthesis and hyphen",[")","-"],"symbols"),
 (8,"Underscore, equals, plus",["_","=","+"],"symbols"),
 (8,"Brackets and slashes",["[","]","{","}","/","|"],"symbols"),
 (9,"Common words",["space"],"words"),
 (9,"Sentences",["space"],"sentences"),
 (9,"Punctuation in sentences",[","],"punctuated"),
 (9,"Numbers and symbols",["7"],"numbers"),
 (9,"A steady pace",["space"],"sentences"),
 (9,"Longer sentences",["space"],"sentences"),
 (9,"Certification practice",["space"],"sentences"),
 (9,"Final review",["space"],"sentences"),
]

NUMBERS = ["45 54 44 55","67 76 66 77","38 83 33 88","29 92 22 99","10 01 11 00",
           "123 456 789 0","2026 10 19","3:45 10:30","555 0142","12 34 56 78"]
SYMBOLS = ["!! ?? !? ?!","@@ ## @# #@","$$ %% $% %$","^^ && ^& &^",
           "* * ( ( ) )","_ _ = = + +","[ ] { } ( )","/ \\ | / \\ |"]

def allowed_text(chars, limit, words=None, sentences=None):
    out = []
    for item in (words if words is not None else []) + (sentences if sentences is not None else []):
        if set(item) <= chars and item not in out:
            out.append(item)
        if len(out) >= limit:
            break
    return out

def safe_fallback(chars, new):
    words = allowed_text(chars, 10, words=WORDS)
    out = [{"text": f"{words[i]} {words[i+1]}"} for i in range(0, len(words) - 1, 2)]
    while len(out) < 3:
        out.append({"text": (new[0] if new else "a") * 2})
    return out[:4]


def tasks_for(mode, teaches, chars, unit):
    new = [k for k in teaches if len(k) == 1 or k in ("escape","tab","enter")]
    if mode == "keys":
        out = []
        for key in new:
            out += [{"text": key}, {"text": key * 2}]
        pairs = [a + b for a in new for b in "asdfjkl" if set(a + b) <= chars]
        out += [{"text": p} for p in pairs[:4]]
        out += [{"text": w} for w in allowed_text(chars, 8, words=WORDS)]
        return out[:14]
    if mode == "words":
        pool = sorted(allowed_text(chars, 400, words=WORDS), key=lambda w: (-len(w), w))
        return [{"text": w} for w in pool[:12]] or [{"text": "as"}]
    if mode == "phrases":
        words = allowed_text(chars, 30, words=WORDS)
        out = []
        for i in range(0, max(0, min(len(words), 12) - 1), 2):
            out.append({"text": f"{words[i]} {words[i+1]}"})
        return out[:8] or [{"text": "as as"}]
    if mode == "sentences":
        out = [{"text": s} for s in allowed_text(chars, 8, sentences=SENTENCES)]
        return out or safe_fallback(chars, new)
    if mode == "punctuated":
        out = [{"text": s} for s in allowed_text(chars, 8, sentences=PUNCTUATED)]
        return out or safe_fallback(chars, new)
    if mode == "capitals":
        letters = sorted(c for c in chars if len(c) == 1 and c.isupper())
        out = [{"text": letter} for letter in letters]
        if letters:
            out.append({"text": " ".join(letters)})
        words = [w for w in ("Dad", "Ada", "Cab", "Bad", "Babe", "Face", "Head",
                             "Feed", "Add", "Bed", "Deaf", "Cafe", "Dead", "Fade")
                 if set(w) <= chars]
        out += [{"text": word} for word in words[:6]]
        return out or safe_fallback(chars, new)
    if mode == "names":
        names = [n for n in ("Devin", "Ann", "Sam", "Lee", "Mia", "Nia", "Ida",
                             "Abe", "Moe", "Lou", "Ned", "Ada", "Cal") if set(n) <= chars]
        return [{"text": n} for n in names] or safe_fallback(chars, new)
    if mode == "numbers":
        lit = [t for t in NUMBERS if set(t) <= chars]
        return [{"text": t} for t in lit] or [{"text": "4 5"}]
    if mode == "symbols":
        lit = [t for t in SYMBOLS if set(t) <= chars]
        return [{"text": t} for t in lit] or [{"text": "!!"}]
    raise SystemExit(f"unknown mode {mode}")

def pad_tasks(tasks, teaches, chars):
    """Every lesson needs enough practice, even when a pool runs dry."""
    drills = [k for k in teaches if len(k) == 1] or [
        c for c in sorted(chars) if c != " "][:2]
    i = 0
    while len(tasks) < 8 and drills:
        key = drills[i % len(drills)]
        tasks.append({"text": key * (2 + (i // len(drills)) % 3)})
        i += 1
    return tasks


def build_intro(id_, unit, teaches, mode):
    """A teacher's voice, not a template: where the key is, why, and how to practise."""
    if teaches and all(key.isdigit() for key in teaches):
        tips = [f"{' and '.join(teaches)} are on the number row. Reach with the "
                "fingers that own the keys below them, then come home."]
    else:
        tips = [KEY_TIPS[key] for key in teaches if key in KEY_TIPS][:2]
    body = " ".join(tips) if tips else "You know these keys already."
    intro = f"{body} {MODE_TIPS[mode]} {ENCOURAGEMENT[id_ % len(ENCOURAGEMENT)]}"
    if len(intro) < 240:
        intro = f"{intro} {UNITS[unit]}"
    return intro


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

def main():
    # Lessons 1 to 5 teach the home row letters.
    taught = {" "} | set("asdfjkl")
    existing = {1: "lessons/001-function-keys.yaml",
                2: "lessons/002-home-row-position.yaml",
                3: "lessons/003-home-row-letters.yaml",
                4: "lessons/004-home-row-words.yaml",
                5: "lessons/005-home-row-phrases.yaml"}
    ids = {i: p for i, p in existing.items()}
    for id_, (unit, title, teaches, mode) in zip(range(6, 73), PLAN):
        taught.update(teaches)
        chars = taught
        for t in teaches:
            if len(t) == 1 and t not in chars:
                chars = chars | {t}
        tasks = pad_tasks(tasks_for(mode, teaches, chars, unit), teaches, chars)
        for task in tasks:
            unknown = set(task["text"]) - chars
            if unknown:
                raise SystemExit(f"lesson {id_}: {sorted(unknown)} in {task['text']!r}")
        body = {
            "schema": 1, "id": id_, "unit": unit, "ordinal": id_, "title": title,
            "teaches": teaches, "kind": "keyboarding", "end_key": "space",
            "repeat": 4,
            "intro": build_intro(id_, unit, teaches, mode),
            "tasks": tasks,
        }
        name = f"{id_:03d}-{slug(title)}.yaml"
        lines = ["schema: 1", f"id: {id_}", f"unit: {unit}", f"ordinal: {id_}",
                 f"title: {json.dumps(title)}",
                 "teaches: [" + ", ".join(json.dumps(t) for t in teaches) + "]",
                 "kind: keyboarding", "end_key: space", "repeat: 4",
                 "intro: >-", f"  {body['intro']}", "tasks:"]
        for task in tasks:
            lines.append(f"  - text: {json.dumps(task['text'])}")
        (LESSONS / name).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        ids[id_] = f"lessons/{name}"
    # course.yaml
    course = ["schema: 1", 'version: "1.0.0"', "lessons:"]
    for i in range(1, 73):
        course.append(f"  - {ids[i]}")
    (ROOT / "content" / "course.yaml").write_text("\n".join(course) + "\n", encoding="utf-8", newline="\n")
    print("wrote", len(ids), "lessons; total tasks", sum(len(t["text"]) for t in []))

main()
