'use strict';

/**
 * Example graph traversal for pets:
 * pet -> species -> genus -> family -> order -> class -> phylum -> kingdom
 */
function traversePetClassification(petId) {
  const safePetId = String(petId || '').trim();
  if (!safePetId) {
    return {
      status: 'error',
      message: 'petId is required'
    };
  }

  const petIri = 'http://cleverllamas.llamaverse/ontology/pet#' + safePetId;
  const query = `
PREFIX lv: <http://cleverllamas.llamaverse/ontology/>
SELECT ?pet ?species ?genus ?family ?order ?class ?phylum ?kingdom
WHERE {
  BIND(<${petIri}> AS ?pet)
  ?pet lv:hasSpecies ?species .
  ?genus lv:containsSpecies ?species .
  ?family lv:containsGenus ?genus .
  ?order lv:containsFamily ?family .
  ?class lv:containsOrder ?order .
  ?phylum lv:containsClass ?class .
  ?kingdom lv:containsPhylum ?phylum .
}
LIMIT 1
`;

  const rows = [];
  for (const row of sem.sparql(query)) {
    const obj = row && row.toObject ? row.toObject() : row;
    rows.push(obj);
  }

  return {
    status: 'ok',
    petId: safePetId,
    petIri: petIri,
    rowCount: rows.length,
    rows: rows
  };
}

// Optional request-field usage when invoked as REST extension endpoint.
const requestField = xdmp.getRequestField('petId');
if (requestField) {
  traversePetClassification(requestField);
} else {
  ({
    status: 'ok',
    message: 'Invoke with ?petId=<uuid>, or import this module and call traversePetClassification(petId).'
  });
}

exports.traversePetClassification = traversePetClassification;
