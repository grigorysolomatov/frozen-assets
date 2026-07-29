"""Generate card art in the Frozen Assets house style.

Usage:
    set -a && . ./.env && set +a && python3 tools/generate-art.py

Writes 1024x1536 PNG masters to images/originals/. To publish, downscale
to the web-sized WebP the site actually loads:

    for f in images/originals/*.png; do
      ffmpeg -y -i "$f" -vf scale=700:-1 -c:v libwebp -quality 82 \
        "images/$(basename "${f%.png}").webp"
    done

Leave STYLE and GREED untouched when adding cards -- they are what makes
the set read as one deck. Only append to CARDS.
"""
import base64, json, os, urllib.request, time

KEY = os.environ["OPENAI_API_KEY"]
OUT = os.path.join(os.path.dirname(__file__), "..", "images", "originals")
os.makedirs(OUT, exist_ok=True)

# Locked style + framing so all six read as one set.
STYLE = (
    " Style: whimsical hand-drawn storybook cartoon illustration. Bold uneven black ink "
    "outlines of varying weight, flat muted color fills with almost no shading or gradient, "
    "simple expressive character with small round dot eyes, charming and a little goofy. "
    "Limited palette: pale icy blue, cream, charcoal, muted teal, one warm amber-gold accent. "
    "Single centered character standing on a simple snow ground line against a flat pale "
    "blue sky, plain minimal background with subtle paper grain. Bold clear silhouette, "
    "generous negative space, iconic and simple like a board-game character card. Folk-art "
    "picture-book quality, naive and playful, not realistic, not painterly, not 3D. "
    "No text, no words, no letters, no numbers, no logos."
)

GREED = (
    " The penguin is consumed by gleeful greed: a wide toothy money-hungry grin, gleaming "
    "wide eyes, grabby flippers clutching its treasure possessively to its chest, gold coins "
    "spilling and tumbling around its feet."
)

CARDS = [
    ("energy",
     "A fat smug penguin tycoon in a tiny black top hat and monocle with a cigar clamped in "
     "its beak, hugging an oil barrel greedily while black oil gushes and gold coins pour out "
     "of it. One simple oil derrick silhouette behind."),
    ("materials",
     "A stout penguin in a small mining helmet, arms crammed full of glittering gemstones and "
     "gold ingots pressed to its chest, a tiny pickaxe tucked under one flipper, sitting on a "
     "heaping mound of ore and jewels."),
    ("consumer-goods",
     "A plump penguin buried under an absurd teetering stack of shopping bags and wrapped gift "
     "boxes, clutching even more to its chest, a tiny shop awning behind it."),
    ("technology",
     "A sleek penguin in a small black turtleneck cradling a single glowing gadget like a "
     "precious egg, one simple floating holographic screen beside it, two small server towers "
     "behind."),
    ("real-estate",
     "A pompous penguin in a fur-collared coat hugging a tiny ice-palace mansion to its chest "
     "like a toy, a rolled deed scroll under one flipper, two simple frozen towers behind."),
    ("crime",
     "A shifty penguin in a small black fedora and pinstripe scarf, cracking open a briefcase "
     "overflowing with cash and gold bars, giving a sly sidelong greedy smirk, a stack of gold "
     "bars at its feet."),
]

for name, subject in CARDS:
    t0 = time.time()
    body = json.dumps({
        "model": "gpt-image-2",
        "prompt": subject + GREED + STYLE,
        "size": "1024x1536",
        "quality": "high",
        "n": 1,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            d = json.load(r)
        p = os.path.join(OUT, f"{name}.png")
        open(p, "wb").write(base64.b64decode(d["data"][0]["b64_json"]))
        print(f"OK   {name:16s} {os.path.getsize(p)//1024:5d} KB  {time.time()-t0:5.1f}s", flush=True)
    except Exception as e:
        print(f"FAIL {name:16s} {e}", flush=True)
print("DONE", flush=True)
