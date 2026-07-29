"""Generate Frozen Assets card art.

Two art sets cover the same six pools. `script.js` picks one via its ART
constant; both live under images/<set>/ with masters in images/originals/<set>/.

    modern  - contemporary settings, flat editorial illustration
    classic - gilded-age settings, screenprint linework

Usage:
    set -a && . ./.env && set +a
    python3 tools/generate-art.py <set> <card> [output-dir]
    python3 tools/generate-art.py modern all

Writes a 1024x1536 PNG master (~2 min per card). Default output is
images/originals/<set>/. Downscale to the WebP the site actually serves:

    ffmpeg -y -i images/originals/SET/NAME.png -vf scale=700:-1 \
      -c:v libwebp -quality 84 images/SET/NAME.webp

Leave STYLES and ATTITUDE untouched when adding cards -- together they are
what make a set read as one deck, and what keep it from looking like a
generic AI render. Give each new card its own camera angle and framing;
six similar poses read as repetitive. Only append to CARDS.
"""
import base64, json, os, sys, urllib.request, time

KEY = os.environ["OPENAI_API_KEY"]
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# Shared across both sets: powerful and self-regarding, never petty or goofy.
ATTITUDE = (
    " The penguin is a powerful, self-important magnate who regards its wealth as dominion "
    "rather than loot: upright commanding posture, chin raised, half-lidded confident eyes, "
    "a faint superior smirk. Never a wide toothy grin, never cute, never goofy, never "
    "clutching things to its chest. Poised, dignified and imposing."
)

STYLES = {
    "classic": (
        " Immaculately dressed in period tailoring."
        " Style: bold hand-drawn editorial illustration, like a vintage screenprinted poster "
        "or a classic engraved advertisement. Confident tapered ink linework of varying weight, "
        "flat opaque color fills, visible halftone dots and paper grain, hand-printed texture "
        "with slight ink misregistration. Absolutely not photorealistic, not a digital painting, "
        "not airbrushed, no soft glowing gradients, no 3D render, no glossy highlights. "
        "Restrained palette: deep charcoal, ice blue, bone cream, muted teal, antique gold. "
        "Strong graphic composition, deliberate negative space, bold readable silhouette. "
        "Elegant, stylish and clearly drawn by a human illustrator. "
        "No text, no words, no letters, no numbers, no logos."
    ),
    "modern": (
        " Dressed in immaculate modern tailoring."
        " Style: contemporary editorial illustration for a modern business magazine. Clean "
        "confident linework, bold flat colour fields, crisp geometric shapes, strong negative "
        "space, only a fine matte grain for texture. Sophisticated modern palette: deep navy, "
        "cool grey, off-white and steel blue with a single saturated accent colour. Sleek, "
        "minimal, graphic and stylish. Not vintage, no halftone engraving, no crosshatching, "
        "no sepia, no ornate flourishes. Not photorealistic, not a digital painting, not "
        "airbrushed, no 3D render, no glossy highlights. "
        "No text, no words, no letters, no numbers, no logos."
    ),
}

CARDS = {
    "classic": {
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
        "media": (
            "A penguin press baron standing astride the deck of a great rotary printing press, "
            "holding a freshly printed newspaper aloft in one flipper, sheets of newsprint streaming "
            "off the rollers and swirling through the air all around him. The newspapers show only "
            "abstract grey halftone bars and blocks, never any lettering. Dynamic diagonal "
            "composition full of flying paper, viewed from slightly below."
        ),
        "politics": (
            "A penguin statesman in a sash of office and a row of medals, standing at a tall ornate "
            "rostrum, one flipper raised mid-oration and the other gripping the lectern, addressing "
            "a dense crowd of small upturned penguin faces below. Heavy draped banners hang behind. "
            "Viewed slightly from below, ceremonial and commanding."
        ),
        "technology": (
            "Three-quarter view of a penguin magnate in a sharp double-breasted suit standing in a "
            "vast cathedral-like machine hall, one flipper resting on the brass lever of an enormous "
            "apparatus of dials, gauges and cables. Rows of tall machine cabinets recede into the "
            "distance behind it. Looking directly at the viewer, proprietary and assured. Solid "
            "machinery and deep perspective, concrete rather than abstract."
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
    },
    "modern": {
        "energy": (
            "A penguin energy executive in a sharp charcoal suit standing on the helipad of a glass "
            "corporate tower at dusk, flippers in pockets, surveying a distant refinery skyline of "
            "flare stacks and wind turbines. Low monumental angle."
        ),
        "media": (
            "A penguin media mogul in a fitted black suit standing before a sweeping curved wall of "
            "glowing broadcast monitors in a darkened control room, one flipper raised directing, "
            "camera rigs in silhouette. The screens show only abstract colour bars and shapes, "
            "never any lettering. Wide, cool and commanding."
        ),
        "politics": (
            "A penguin politician in a modern navy suit at a press-conference lectern bristling with "
            "microphones, one flipper raised, camera flashes firing from the dark, a plain flag "
            "backdrop behind. Viewed slightly from below."
        ),
        "technology": (
            "A penguin tech founder in a minimalist dark outfit standing in the cold aisle of a "
            "modern data centre, rows of server racks with thin LED strips receding to a vanishing "
            "point, one flipper resting on a rack door. Severe one-point perspective."
        ),
        "real-estate": (
            "A penguin developer in a tailored overcoat standing at the floor-to-ceiling window of "
            "an empty penthouse, a night skyline of glass towers spread out far below, a tablet held "
            "at its side. Seen from behind and slightly to one side."
        ),
        "crime": (
            "A penguin crime boss in a black turtleneck and long overcoat standing between the open "
            "doors of a black SUV in a neon-lit underground car park, headlights raking across the "
            "concrete, a brushed aluminium case at its feet. Tight, high contrast, most of the frame "
            "in shadow."
        ),
    },
}


def generate(art_set, name, out_dir):
    body = json.dumps({
        "model": "gpt-image-2",
        "prompt": CARDS[art_set][name] + ATTITUDE + STYLES[art_set],
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
    path = os.path.join(out_dir, f"{name}.png")
    open(path, "wb").write(base64.b64decode(d["data"][0]["b64_json"]))
    print(f"OK   {name:14s} {os.path.getsize(path)//1024:5d} KB {time.time()-t0:5.0f}s", flush=True)


if __name__ == "__main__":
    art_set, card = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, "images", "originals", art_set)
    os.makedirs(out, exist_ok=True)
    names = list(CARDS[art_set]) if card == "all" else [card]
    for n in names:
        try:
            generate(art_set, n, out)
        except Exception as e:
            print(f"FAIL {n:14s} {e}", flush=True)
    print("DONE", flush=True)
