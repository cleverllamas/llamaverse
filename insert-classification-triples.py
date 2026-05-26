#!/usr/bin/env python3
"""
Inserts llamaverse classification triples via the MarkLogic /v1/graphs REST endpoint.
Generates two named graphs:
  lv:graph/ontology      — taxonomy hierarchy
  lv:graph/llama-species — lv:hasSpecies triples for all llama docs
Also writes N-Triples files for source control.
"""
import json, glob, os, requests
from requests.auth import HTTPDigestAuth

BASE   = os.path.dirname(os.path.abspath(__file__))
LLAMAS = os.path.join(BASE, "src/main/ml-data/cleverllamas/llamaverse/raw/wild-llamas/llamas")
# Use port 8010 (the cleverllamas app server) with basic auth
REST_GRAPHS = "http://localhost:8010/v1/graphs"
AUTH        = ("admin","admin")  # Basic auth

LV   = "http://cleverllamas.com/llamaverse/"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
RDF  = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
ONTO_GRAPH  = f"{LV}graph/ontology"
LLAMA_GRAPH = f"{LV}graph/llama-species"

PHYLA   = ["Lanuda","Suri","Vellosa"]
CLASSES = ["Alpinus","Litoralis","Aridus","Silvaticus","Boreus"]
ORDERS  = ["Scholares","Athletici","Artifices","Mercatores","Pastores","Diplomatici"]
FAMILIES= ["Andesidae","Patagonidae","Pampeidae","Cuscidae","Titicacidae",
           "Arequipidae","Huancaidae","Pampasidae"]
SUBSPECIES_KEYS = [
    "Lama_glama_andinus","Lama_glama_litoralis","Lama_glama_deserticola",
    "Lama_glama_silvestris","Lama_glama_borealis",
    "Lama_glama_suriensis","Lama_glama_suriphilus","Lama_glama_surideserta",
    "Lama_glama_suriforest","Lama_glama_suriborealis",
    "Lama_glama_vellifer","Lama_glama_vellicosta","Lama_glama_vellaridus",
    "Lama_glama_vellasilva","Lama_glama_vellaboreas",
]

def iri(s): return f"<{s}>"
def t(s,p,o): return f"{iri(s)} {iri(p)} {iri(o)} ."
def tl(s,p,o): return f'{iri(s)} {iri(p)} "{o}"@en .'

def classify_llama(llama_id):
    h = llama_id.replace("-","")
    n0,n1 = int(h[0],16),int(h[1],16)
    pi = 0 if n0<6 else 1 if n0<11 else 2
    ci = 0 if n1<4 else 1 if n1<6 else 2 if n1<9 else 3 if n1<12 else 4
    return SUBSPECIES_KEYS[pi*5+ci]

# ─── Ontology triples ─────────────────────────────────────────────────────────
print("Building ontology triples...")
lines = []
sub_of  = f"{LV}subClassOf"
type_p  = f"{RDF}type"
label_p = f"{RDFS}label"
KINGDOM = f"{LV}kingdom/Llamalia"

lines.extend([t(KINGDOM, type_p, f"{LV}type/Kingdom"), tl(KINGDOM, label_p, "Llamalia")])
for ph in PHYLA:
    n = f"{LV}phylum/{ph}"
    lines += [t(n,type_p,f"{LV}type/Phylum"), tl(n,label_p,ph), t(n,sub_of,KINGDOM)]
for cl in CLASSES:
    n = f"{LV}class/{cl}"
    lines += [t(n,type_p,f"{LV}type/Class"), tl(n,label_p,cl), t(n,sub_of,KINGDOM)]
for o in ORDERS:
    n = f"{LV}order/{o}"
    lines += [t(n,type_p,f"{LV}type/Order"), tl(n,label_p,o), t(n,sub_of,KINGDOM)]
for f in FAMILIES:
    n = f"{LV}family/{f}"
    lines += [t(n,type_p,f"{LV}type/Family"), tl(n,label_p,f), t(n,sub_of,KINGDOM)]
g = f"{LV}genus/Lama"
lines += [t(g,type_p,f"{LV}type/Genus"), tl(g,label_p,"Lama"), t(g,sub_of,KINGDOM)]
for key in SUBSPECIES_KEYS:
    n = f"{LV}species/{key}"
    lines += [t(n,type_p,f"{LV}type/Species"), tl(n,label_p,key.replace("_"," ")), t(n,sub_of,g)]
onto_nt = "\n".join(lines) + "\n"
print(f"  {len(lines)} ontology triples")

# ─── Llama->species triples ───────────────────────────────────────────────────
print("Building llama->species triples...")
has_species = f"{LV}hasSpecies"
llama_lines = []
for path in sorted(glob.glob(os.path.join(LLAMAS,"*.json"))):
    with open(path) as fh: doc = json.load(fh)
    llama_id = doc.get("id") or doc.get("llamaId","")
    if not llama_id: continue
    sk = doc.get("classificationSpeciesKey") or classify_llama(llama_id)
    llama_lines.append(t(f"{LV}llama/{llama_id}", has_species, f"{LV}species/{sk}"))
llama_nt = "\n".join(llama_lines) + "\n"
print(f"  {len(llama_lines)} llama->species triples")

# ─── Save N-Triples files ─────────────────────────────────────────────────────
nt_dir = os.path.join(BASE, "src/main/ml-data/cleverllamas/llamaverse/content/triples")
os.makedirs(nt_dir, exist_ok=True)
with open(os.path.join(nt_dir,"llama-classification-ontology.nt"),"w") as fh: fh.write(onto_nt)
with open(os.path.join(nt_dir,"llama-species.nt"),"w") as fh: fh.write(llama_nt)
print(f"  N-Triples saved to {nt_dir}")

# ─── Upload via /v1/graphs ────────────────────────────────────────────────────
def upload_graph(graph_uri, nt_content, label):
    r = requests.put(
        REST_GRAPHS,
        params={"graph": graph_uri},
        auth=AUTH,
        headers={"Content-Type": "application/n-triples"},
        data=nt_content.encode("utf-8"),
        timeout=120,
    )
    if r.status_code in (200,201,204):
        print(f"  ✓ {label}: HTTP {r.status_code}")
    else:
        print(f"  ✗ {label}: HTTP {r.status_code} — {r.text[:300]}")

print("\nUploading to MarkLogic via /v1/graphs...")
upload_graph(ONTO_GRAPH,  onto_nt,  "ontology graph")
upload_graph(LLAMA_GRAPH, llama_nt, "llama-species graph")

# ─── Verify ───────────────────────────────────────────────────────────────────
print("\nVerifying via SPARQL...")
sparql_url = "http://localhost:8010/v1/graphs/sparql"
q1 = "SELECT (COUNT(*) AS ?n) WHERE { ?s <http://cleverllamas.com/llamaverse/hasSpecies> ?o }"
q2 = "SELECT (COUNT(*) AS ?n) WHERE { ?s <http://cleverllamas.com/llamaverse/subClassOf> ?o }"
q3 = "SELECT ?llama ?species WHERE { ?llama <http://cleverllamas.com/llamaverse/hasSpecies> ?species } LIMIT 2"

for q,label in [(q1,"hasSpecies count"),(q2,"subClassOf count"),(q3,"sample")]:
    r = requests.get(sparql_url, params={"query":q}, auth=AUTH,
                     headers={"Accept":"application/sparql-results+json"})
    if r.status_code==200:
        data = r.json()
        for row in data["results"]["bindings"]:
            vals = {k:v["value"] for k,v in row.items()}
            print(f"  {label}: {vals}")
    else:
        print(f"  {label}: HTTP {r.status_code} — {r.text[:200]}")
