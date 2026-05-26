#!/usr/bin/env python3
"""
Patch all wild-llama documents in MarkLogic with a full 7-level
llamaverse classification block, assigned deterministically from llamaId.
"""
import requests
from requests.auth import HTTPDigestAuth

ENDPOINT = "http://localhost:8000/v1/eval?database=cleverllamas-content"
AUTH = HTTPDigestAuth("admin", "admin")

# ─────────────────────────────────────────────────────────────────────────────
# Server-side JavaScript that patches every llama document
# ─────────────────────────────────────────────────────────────────────────────
JS = r"""
'use strict';

// ── Llamaverse classification taxonomy ──────────────────────────────────────
// Kingdom: always Llamalia
// Phylum:  based on llamaId hex nibble 0  (3 clades)
// Class:   based on llamaId hex nibble 1  (5 habitat types)
// Order:   based on llamaId hex nibble 2  (6 social roles)
// Family:  based on llamaId hex nibble 3  (8 regional families)
// Genus:   always Lama
// Species: Lama glama + subspecies (derived from phylum+class indices)

const PHYLA = [
  "Lanuda",    // 0–5  woolly-fleeced
  "Suri",      // 6–a  silky long-fibred
  "Vellosa",   // b–f  exceptionally fluffy
];

const CLASSES = [
  "Alpinus",    // 0–3  highland
  "Litoralis",  // 4–5  coastal
  "Aridus",     // 6–8  desert
  "Silvaticus", // 9–b  forest
  "Boreus",     // c–f  tundra
];

const ORDERS = [
  "Scholares",     // 0–2  scholarly / academic
  "Athletici",     // 3–4  athletic / competitive
  "Artifices",     // 5–6  artisans / craftsllamakin
  "Mercatores",    // 7–9  mercantile / trade
  "Pastores",      // a–c  pastoral / agricultural
  "Diplomatici",   // d–f  diplomatic / civic
];

const FAMILIES = [
  "Andesidae",    // 0–1
  "Patagonidae",  // 2–3
  "Pampeidae",    // 4–5
  "Cuscidae",     // 6–7
  "Titicacidae",  // 8–9
  "Arequipidae",  // a–b
  "Huancaidae",   // c–d
  "Pampasidae",   // e–f
];

// 3 phyla × 5 classes = 15 subspecies epithets
const SUBSPECIES = [
  "glama andinus",    // Lanuda  + Alpinus
  "glama litoralis",  // Lanuda  + Litoralis
  "glama deserticola",// Lanuda  + Aridus
  "glama silvestris", // Lanuda  + Silvaticus
  "glama borealis",   // Lanuda  + Boreus
  "glama suriensis",  // Suri    + Alpinus
  "glama suriphilus", // Suri    + Litoralis
  "glama surideserta",// Suri    + Aridus
  "glama suriforest", // Suri    + Silvaticus
  "glama suriborealis",// Suri   + Boreus
  "glama vellifer",   // Vellosa + Alpinus
  "glama vellicosta", // Vellosa + Litoralis
  "glama vellaridus",  // Vellosa + Aridus
  "glama vellasilva",  // Vellosa + Silvaticus
  "glama vellaboreas", // Vellosa + Boreus
];

function hexVal(ch) {
  const v = parseInt(ch, 16);
  return isNaN(v) ? 0 : v;
}

function classifyLlama(llamaId) {
  // Use first 4 meaningful hex characters of the UUID (skip hyphens)
  const hex = llamaId.replace(/-/g, '');
  const n0 = hexVal(hex[0] || '0');
  const n1 = hexVal(hex[1] || '0');
  const n2 = hexVal(hex[2] || '0');
  const n3 = hexVal(hex[3] || '0');

  const phylumIdx   = n0 < 6 ? 0 : n0 < 11 ? 1 : 2;
  const classIdx    = n1 < 4 ? 0 : n1 < 6 ? 1 : n1 < 9 ? 2 : n1 < 12 ? 3 : 4;
  const orderIdx    = n2 < 3 ? 0 : n2 < 5 ? 1 : n2 < 7 ? 2 : n2 < 10 ? 3 : n2 < 13 ? 4 : 5;
  const familyIdx   = Math.floor(n3 / 2);
  const subspeciesIdx = phylumIdx * 5 + classIdx;

  return {
    kingdom: "Llamalia",
    phylum:  PHYLA[phylumIdx],
    class:   CLASSES[classIdx],
    order:   ORDERS[orderIdx],
    family:  FAMILIES[familyIdx],
    genus:   "Lama",
    species: "Lama " + SUBSPECIES[subspeciesIdx],
  };
}

// ── Patch documents ──────────────────────────────────────────────────────────
let count = 0;
let skipped = 0;

for (const uri of fn.collection(xs.string('wild-llamas'))) {
  const uriStr = xdmp.nodeUri(uri);
  if (!uriStr || !uriStr.endsWith('.json')) { skipped++; continue; }

  const doc = uri.toObject ? uri.toObject() : cts.doc(uriStr).toObject();
  if (!doc || !doc.envelope || !doc.envelope.instance || !doc.envelope.instance.llama) {
    skipped++; continue;
  }

  const llamaId = doc.envelope.instance.llama.llamaId;
  if (!llamaId) { skipped++; continue; }

  doc.envelope.instance.llama.classification = classifyLlama(llamaId);

  xdmp.documentInsert(
    uriStr,
    doc,
    { collections: xdmp.documentGetCollections(uriStr) }
  );
  count++;
}

'Patched ' + count + ' llamas, skipped ' + skipped;
"""

print("Sending classification patch to MarkLogic...")
resp = requests.post(
    ENDPOINT,
    auth=AUTH,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={"javascript": JS},
    timeout=300,
)

if resp.status_code == 200:
    # Multipart response — grab the last text/plain part
    text = resp.text
    for part in text.split("--"):
        if "text/plain" in part or "text/javascript" in part:
            lines = [l for l in part.strip().splitlines() if l and not l.startswith("Content")]
            if lines:
                print("Result:", lines[-1])
else:
    print(f"HTTP {resp.status_code}: {resp.text[:500]}")
