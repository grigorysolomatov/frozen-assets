"""Generate Frozen Assets card art in the house style.

Usage:
    set -a && . ./.env && set +a
    python3 tools/generate-art.py <card-name> [output-dir]

Writes a 1024x1536 PNG master (~2 min per card). Default output is
images/originals/. Downscale to the WebP the site actually serves:

    ffmpeg -y -i images/originals/NAME.png -vf scale=700:-1 \
      -c:v libwebp -quality 84 images/NAME.webp

Leave STYLE and ATTITUDE untouched when adding cards -- together they are
what make the set read as one deck, and what keep it from looking like a
generic AI render. Give each new card its own camera angle and framing;
six similar poses read as repetitive. Only append to CARDS.
"""
import base64, json, os, sys, urllib.request, time

KEY = os.environ["OPENAI_API_KEY"]
_DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images", "originals")
OUT = sys.argv[2] if len(sys.argv) > 2 else _DEFAULT_OUT
os.makedirs(OUT, exist_ok=True)

# Hand-drawn and graphic, deliberately NOT the glossy AI-render look.
STYLE = (
    " Style: bold hand-drawn editorial illustration, like a vintage screenprinted poster "
    "or a classic engraved advertisement. Confident tapered ink linework of varying weight, "
    "flat opaque color fills, visible halftone dots and paper grain, hand-printed texture "
    "with slight ink misregistration. Absolutely not photorealistic, not a digital painting, "
    "not airbrushed, no soft glowing gradients, no 3D render, no glossy highlights. "
    "Restrained palette: deep charcoal, ice blue, bone cream, muted teal, antique gold. "
    "Strong graphic composition, deliberate negative space, bold readable silhouette. "
    "Elegant, stylish and clearly drawn by a human illustrator. "
    "No text, no words, no letters, no numbers, no logos."
)

# Powerful and self-regarding, not petty or goofy.
ATTITUDE = (
    " The penguin is a powerful, self-important magnate who regards its wealth as dominion "
    "rather than loot: upright commanding posture, chin raised, half-lidded confident eyes, "
    "a faint superior smirk. Never a wide toothy grin, never cute, never goofy, never "
    "clutching things to its chest. Immaculately dressed, poised, dignified and imposing."
)

CARDS = {
    "energy": (
        "Low heroic angle looking up at a heavyset penguin oil baron in a black frock coat and "
        "top hat, one webbed foot planted on an oil barrel, a cigar in its beak, surveying the "
        "viewer with disdain. Behind and below, the iron lattice of a derrick and a distant "
        "flare. Composition tall and monumental."
    ),
    "materials": (
        "Three-quarter view of a broad penguin industrialist seated on a throne hewn from raw "
        "ore and crystal, one flipper resting on the haft of a pickaxe held upright like a "
        "sceptre, a heavy fur mantle over its shoulders. Cut quarry walls step away behind it. "
        "Composition wide, seated and regal."
    ),
    "consumer-goods": (
        "A dapper penguin merchant prince in a waistcoat standing behind a polished counter, "
        "flippers spread wide in a proprietary gesture presenting tall shelves of identical "
        "boxed goods receding behind it. Frontal, symmetrical, shopkeeper-emperor composition."
    ),
    "technology": (
        "Profile view of a lean penguin financier in a high-collared coat, flippers clasped "
        "behind its back, gazing up at one large floating schematic diagram of fine geometric "
        "linework. Cool, detached, visionary. Sparse composition with a great deal of empty space."
    ),
    "real-estate": (
        "Seen from below, a penguin magnate in a long fur-collared greatcoat stands at the stone "
        "parapet of a high tower, one flipper on the railing, coat caught by the wind, looking "
        "out over a city of frozen spires far below. Sweeping and territorial."
    ),
    "crime": (
        "A penguin crime patriarch sunk deep in a buttoned leather armchair in near darkness, "
        "flipper-tips steepled, lit from one side by a single lamp, utterly calm. Heavy shadow, "
        "tight intimate framing, most of the frame in shadow."
    ),
}

name = sys.argv[1]
subject = CARDS[name]
body = json.dumps({
    "model": "gpt-image-2",
    "prompt": subject + ATTITUDE + STYLE,
    "size": "1024x1536",
    "quality": "high",
    "n": 1,
}).encode()
req = urllib.request.Request(
    "https://api.openai.com/v1/images/generations", data=body,
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
)
t0 = time.time()
with urllib.request.urlopen(req, timeout=600) as r:
    d = json.load(r)
p = os.path.join(OUT, f"{name}.png")
open(p, "wb").write(base64.b64decode(d["data"][0]["b64_json"]))
print(f"OK {name} {os.path.getsize(p)//1024} KB {time.time()-t0:.0f}s", flush=True)
