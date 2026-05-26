#!/usr/bin/env python3
"""
Sets up the llamaverse classification ontology and patches llama documents.

Steps:
  1. Write 39 taxonomy-node JSON files to  content/ontology/taxonomy-nodes/
  2. Add classificationSpeciesKey to all ~3300 flat llama source JSON files
  3. Write two TDE templates to  src/main/ml-schemas/tde/
  4. Load the TDE templates directly into the schemas DB via REST

After running this, execute:
  ./gradlew mlLoadData   — to deploy data files
"""
import json, os, glob, requests
from requests.auth import HTTPDigestAuth

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DATA  = os.path.join(BASE_DIR, "src/main/ml-data/cleverllamas/llamaverse")
ML_SCHEMAS_TDE = os.path.join(BASE_DIR, "src/main/ml-schemas/tde")
LLAMA_SRC = os.path.join(ML_DATA, "raw/wild-llamas/llamas")

REST = "http://localhost:8000/v1"
AUTH = HTTPDigestAuth("admin", "admin")
LV   = "http://cleverllamas.com/llamaverse/"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
RDF  = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

# ─────────────────────────────────────────────────────────────────────────────
# TAXONOMY DEFINITION
# ─────────────────────────────────────────────────────────────────────────────
PHYLA = [
    ("Lanuda",   "Woolly-fleeced llamas whose dense, crimped fibre has made WoolWorks International extremely profitable. The majority of the llamaverse population."),
    ("Suri",     "Silky long-fibred llamas whose lustrous locks fall in pencil-thin locks. Prized for luxury textile production and personal shampoo commercials."),
    ("Vellosa",  "Exceptionally fluffy llamas with fibre so dense they appear to be walking clouds. Require specialist grooming every three days and are entirely worth it."),
]
CLASSES = [
    ("Alpinus",    "Highland-dwelling llamas adapted to thin air, cold temperatures, and an attitude of quiet superiority."),
    ("Litoralis",  "Coastal llamas with salt-tolerant hooves and an appreciation for seafood-adjacent cuisine."),
    ("Aridus",     "Desert-adapted llamas able to conserve water for weeks. Notoriously stubborn, which they consider a feature."),
    ("Silvaticus", "Forest-dwelling llamas with exceptional spatial memory and a talent for navigating dense woodland."),
    ("Boreus",     "Tundra llamas whose double-layered coats and philosophical dispositions see them through six-month winters."),
]
ORDERS = [
    ("Scholares",    "Academic and research-oriented llamas who account for 80% of MarkLogic database administrators in the llamaverse."),
    ("Athletici",    "Competitive and energetic llamas drawn to sport, physical challenge, and arguing about optimum race strategy."),
    ("Artifices",    "Creative artisan llamas — weavers, potters, composers, architects. Frequently underestimated and always correct about aesthetics."),
    ("Mercatores",   "Mercantile llamas who have built the llamaverse's trading infrastructure and understand compound interest on an emotional level."),
    ("Pastores",     "Agricultural and pastoral llamas who maintain the hay supply and know more about soil than any academic llama will admit."),
    ("Diplomatici",  "Civic and diplomatic llamas who hold public office, negotiate inter-herd treaties, and write the legislation other llamas complain about."),
]
FAMILIES = [
    ("Andesidae",    "The original highland families. Ancient lineages with complex genealogies tracked across centuries."),
    ("Patagonidae",  "Wind-hardened southern families known for navigational skill and extremely good tent-making."),
    ("Pampeidae",    "Grassland families of the great plains. Historically pastoral; recently increasingly entrepreneurial."),
    ("Cuscidae",     "Urban families centred around the great llamaverse cities. Cosmopolitan, well-connected, and rarely surprised."),
    ("Titicacidae",  "Lake-region families with strong fishing traditions and the most comprehensive knowledge of freshwater ecology."),
    ("Arequipidae",  "Volcanic-plateau families with a reputation for contrarianism and exceptional cheese production."),
    ("Huancaidae",   "Valley families whose agricultural expertise supports a disproportionate share of the llamaverse food supply."),
    ("Pampasidae",   "Eastern lowland families, newer arrivals by llamaverse historical standards, bringing distinct cultural traditions."),
]
SUBSPECIES = [
    ("Lama_glama_andinus",     "Lanuda",  "Alpinus",    "The classic highland woolly llama. Reference population for most llamaverse genomic studies."),
    ("Lama_glama_litoralis",   "Lanuda",  "Litoralis",  "Woolly coastal llamas whose fibre has adapted a slight natural water-resistance."),
    ("Lama_glama_deserticola",  "Lanuda",  "Aridus",     "Desert woolly llamas who produce remarkably fine fibre despite (or because of) arid conditions."),
    ("Lama_glama_silvestris",  "Lanuda",  "Silvaticus", "Forest woolly llamas with slightly darker colouring for camouflage among dappled shade."),
    ("Lama_glama_borealis",    "Lanuda",  "Boreus",     "Arctic woolly llamas whose fleece density reaches extraordinary levels in winter."),
    ("Lama_glama_suriensis",   "Suri",    "Alpinus",    "Highland suri llamas with exceptionally long silky locks that catch the Andean light dramatically."),
    ("Lama_glama_suriphilus",  "Suri",    "Litoralis",  "Coastal suri llamas. Their locks survive sea spray remarkably well and smell faintly of salt."),
    ("Lama_glama_surideserta", "Suri",    "Aridus",     "Desert suri llamas who trap air in their long fibres to provide insulation against temperature extremes."),
    ("Lama_glama_suriforest",  "Suri",    "Silvaticus", "Forest suri llamas who are periodically found with small creatures living contentedly in their locks."),
    ("Lama_glama_suriborealis","Suri",    "Boreus",     "Tundra suri llamas whose locks freeze into impressive icicle formations in winter, which they claim to enjoy."),
    ("Lama_glama_vellifer",    "Vellosa", "Alpinus",    "Highland fluffy llamas. Visible from several kilometres on a clear day."),
    ("Lama_glama_vellicosta",  "Vellosa", "Litoralis",  "Coastal fluffy llamas. Require windbreaks to prevent spontaneous relocation."),
    ("Lama_glama_vellaridus",  "Vellosa", "Aridus",     "Desert fluffy llamas who represent a genuine evolutionary puzzle that remains unresolved."),
    ("Lama_glama_vellasilva",  "Vellosa", "Silvaticus", "Forest fluffy llamas perpetually decorated with leaves, twigs, and small admiring insects."),
    ("Lama_glama_vellaboreas", "Vellosa", "Boreus",     "Tundra fluffy llamas. Completely indistinguishable from snowdrifts in winter. Several are lost annually."),
]

PHYLA_KEYS   = [p[0] for p in PHYLA]
CLASSES_KEYS = [c[0] for c in CLASSES]
ORDERS_KEYS  = [o[0] for o in ORDERS]
FAMILIES_KEYS= [f[0] for f in FAMILIES]
SUBSPECIES_KEYS = [s[0] for s in SUBSPECIES]

# ─────────────────────────────────────────────────────────────────────────────
# 1. GENERATE TAXONOMY NODE DOCUMENTS
# ─────────────────────────────────────────────────────────────────────────────
print("Step 1: Writing taxonomy node documents...")
node_dir = os.path.join(ML_DATA, "content/ontology/taxonomy-nodes")
os.makedirs(node_dir, exist_ok=True)

with open(os.path.join(node_dir, "collections.properties"), "w") as f:
    f.write("*=llamaverse,content,ontology\n")

def node_doc(uri, node_type, label, parent_uri, description, extra=None):
    doc = {"uri": uri, "type": node_type, "label": label, "description": description}
    if parent_uri:
        doc["parentUri"] = parent_uri
    if extra:
        doc.update(extra)
    return doc

def write_node(doc):
    slug = doc["uri"].split("/")[-1]
    path = os.path.join(node_dir, f"{slug}.json")
    with open(path, "w") as f:
        json.dump(doc, f, indent=2)

# Kingdom
write_node(node_doc(
    f"{LV}kingdom/Llamalia", "Kingdom", "Llamalia", None,
    "The kingdom of all llamas. Apex species of the llamaverse, builders of civilisations, "
    "keepers of hay, and the primary operators of MarkLogic databases at scale."
))

# Phyla
for label, desc in PHYLA:
    write_node(node_doc(
        f"{LV}phylum/{label}", "Phylum", label,
        f"{LV}kingdom/Llamalia", desc
    ))

# Classes
for label, desc in CLASSES:
    write_node(node_doc(
        f"{LV}class/{label}", "Class", label,
        f"{LV}kingdom/Llamalia", desc
    ))

# Orders
for label, desc in ORDERS:
    write_node(node_doc(
        f"{LV}order/{label}", "Order", label,
        f"{LV}kingdom/Llamalia", desc
    ))

# Families
for label, desc in FAMILIES:
    write_node(node_doc(
        f"{LV}family/{label}", "Family", label,
        f"{LV}kingdom/Llamalia", desc
    ))

# Genus
write_node(node_doc(
    f"{LV}genus/Lama", "Genus", "Lama",
    f"{LV}kingdom/Llamalia",
    "The single genus of the llamaverse. All known llamas belong here. "
    "There was briefly a second genus proposed in 2019 but the paper was retracted."
))

# Species
for key, phylum, cls, desc in SUBSPECIES:
    species_label = key.replace("_", " ").replace("Lama ", "Lama ")
    write_node(node_doc(
        f"{LV}species/{key}", "Species", species_label,
        f"{LV}genus/Lama", desc,
        extra={"phylumKey": phylum, "classKey": cls,
               "speciesKey": key}
    ))

total_nodes = 1 + len(PHYLA) + len(CLASSES) + len(ORDERS) + len(FAMILIES) + 1 + len(SUBSPECIES)
print(f"  {total_nodes} taxonomy node docs -> {node_dir}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. PATCH LLAMA SOURCE JSON FILES
# ─────────────────────────────────────────────────────────────────────────────
print("Step 2: Adding classificationSpeciesKey to llama source files...")

def classify_llama(llama_id):
    hex_id = llama_id.replace("-", "")
    def hv(c): return int(c, 16) if c else 0
    n0, n1, n2, n3 = hv(hex_id[0]), hv(hex_id[1]), hv(hex_id[2]), hv(hex_id[3])
    pi = 0 if n0 < 6 else 1 if n0 < 11 else 2
    ci = 0 if n1 < 4 else 1 if n1 < 6 else 2 if n1 < 9 else 3 if n1 < 12 else 4
    return SUBSPECIES_KEYS[pi * 5 + ci]

patched = 0
for path in glob.glob(os.path.join(LLAMA_SRC, "*.json")):
    with open(path) as f:
        doc = json.load(f)
    if "id" not in doc:
        continue
    key = classify_llama(doc["id"])
    if doc.get("classificationSpeciesKey") == key:
        continue  # already patched, skip
    doc["classificationSpeciesKey"] = key
    with open(path, "w") as f:
        json.dump(doc, f, indent=2)
    patched += 1

print(f"  {patched} llama source files patched -> {LLAMA_SRC}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. WRITE TDE TEMPLATES
# ─────────────────────────────────────────────────────────────────────────────
print("Step 3: Writing TDE templates...")
os.makedirs(ML_SCHEMAS_TDE, exist_ok=True)

# TDE 1: taxonomy-node-triples — projects hierarchy triples from ontology node docs
taxonomy_tde = {
    "template": {
        "description": "Projects llamaverse classification hierarchy as RDF triples from ontology node documents.",
        "context": "/uri",
        "collections": ["ontology"],
        "triples": [
            {
                "subject":   {"val": "sem:iri(.)"},
                "predicate": {"val": f"sem:iri('{RDF}type')"},
                "object":    {"val": f"sem:iri(concat('{LV}type/', ../type))"}
            },
            {
                "subject":   {"val": "sem:iri(.)"},
                "predicate": {"val": f"sem:iri('{RDFS}label')"},
                "object":    {"val": "../label"}
            },
            {
                "subject":   {"val": "sem:iri(.)"},
                "predicate": {"val": f"sem:iri('{RDFS}comment')"},
                "object":    {"val": "../description"}
            },
            {
                "subject":      {"val": "sem:iri(.)"},
                "predicate":    {"val": f"sem:iri('{LV}subClassOf')"},
                "object":       {"val": "sem:iri(../parentUri)"},
                "invalidValues": "ignore"
            },
        ]
    }
}

tde1_path = os.path.join(ML_SCHEMAS_TDE, "taxonomy-node-triples.tde")
with open(tde1_path, "w") as f:
    json.dump(taxonomy_tde, f, indent=2)
print(f"  TDE -> {tde1_path}")

# TDE 2: llama-species-triples — projects lv:hasSpecies from flat llama docs
llama_triples_tde = {
    "template": {
        "description": "Projects lv:hasSpecies triple from each wild-llama document to its species node in the ontology.",
        "context": "/id",
        "collections": ["wild-llamas"],
        "triples": [
            {
                "subject":      {"val": f"sem:iri(concat('{LV}llama/', .))"},
                "predicate":    {"val": f"sem:iri('{LV}hasSpecies')"},
                "object":       {"val": f"sem:iri(concat('{LV}species/', ../classificationSpeciesKey))"},
                "invalidValues": "ignore"
            }
        ]
    }
}

tde2_path = os.path.join(ML_SCHEMAS_TDE, "llama-species-triples.tde")
with open(tde2_path, "w") as f:
    json.dump(llama_triples_tde, f, indent=2)
print(f"  TDE -> {tde2_path}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. LOAD TDE TEMPLATES INTO SCHEMAS DB
# ─────────────────────────────────────────────────────────────────────────────
print("Step 4: Loading TDE templates into cleverllamas-schemas database...")

tde_files = [
    ("/tde/taxonomy-node-triples.tde", tde1_path),
    ("/tde/llama-species-triples.tde", tde2_path),
]

for db_uri, local_path in tde_files:
    with open(local_path) as f:
        content = f.read()
    r = requests.put(
        f"{REST}/documents",
        auth=AUTH,
        params={"uri": db_uri, "database": "cleverllamas-schemas"},
        headers={"Content-Type": "application/json"},
        data=content,
        timeout=30,
    )
    if r.status_code in (200, 201, 204):
        print(f"  Loaded {db_uri} [{r.status_code}]")
    else:
        print(f"  FAILED {db_uri}: HTTP {r.status_code} — {r.text[:200]}")

print()
print("Done. Now run:  ./gradlew mlLoadData")
print("This will deploy the taxonomy node docs and re-deploy the patched llama docs.")
