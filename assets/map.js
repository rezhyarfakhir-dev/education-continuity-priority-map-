// Education Continuity Priority Map - Leaflet renderer

// Severity palette tuned to the brand (teal/orange/gray):
//   high    = red       (semantic: highest risk)
//   medium  = brand orange
//   low     = amber
//   validation_needed = gray
const COLORS = {
  high: "#b91c1c",
  medium: "#ea7317",
  low: "#fbbf24",
  validation_needed: "#9ca3af",
};
const CLASS_LABEL = {
  high: "High priority",
  medium: "Medium priority",
  low: "Lower priority",
  validation_needed: "Validation needed",
};

const map = L.map("map", { zoomControl: true, scrollWheelZoom: false }).setView([11.4, 12.7], 7);

L.tileLayer("https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png", {
  maxZoom: 11,
  minZoom: 6,
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
}).addTo(map);

function styleLGA(feature) {
  const cls = feature.properties.priority_class || "validation_needed";
  return {
    color: "#333",
    weight: 0.6,
    fillColor: COLORS[cls] || COLORS.validation_needed,
    fillOpacity: 0.78,
  };
}

function fmt(n) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  if (typeof n === "number") return n.toLocaleString();
  return n;
}
function fmtPct(n) {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return `${Number(n).toFixed(1)}%`;
}

function popupHtml(p) {
  const cls = p.priority_class || "validation_needed";
  const badgeCls = { high: "pop-hi", medium: "pop-med", low: "pop-lo", validation_needed: "pop-val" }[cls] || "pop-val";
  const reason = p.priority_reason ? `<p style="margin:6px 0 0;color:#555;font-size:12px;font-style:italic;">${p.priority_reason}</p>` : "";
  return `
    <h3>${p.lga} <small style="color:#666;font-weight:400;">(${p.state})</small></h3>
    <span class="pop-class ${badgeCls}">${CLASS_LABEL[cls]}</span>
    <table>
      <tr><td class="k">ACLED events 2020-26</td><td class="v">${fmt(p.events)}</td></tr>
      <tr><td class="k">Fatalities</td><td class="v">${fmt(p.fatalities)}</td></tr>
      <tr><td class="k">IDP individuals (DTM R50)</td><td class="v">${fmt(p.idp_individuals)}</td></tr>
      <tr><td class="k">Schools listed (iMMAP 2019)</td><td class="v">${fmt(p.total_schools)}</td></tr>
      <tr><td class="k">Schools closed</td><td class="v">${fmt(p.closed_schools)} (${fmtPct(p.pct_closed)})</td></tr>
      <tr><td class="k">School-age within 5km of school</td><td class="v">${fmtPct(p.school_age_within_5km_pct)}</td></tr>
      <tr><td class="k">Composite score</td><td class="v">${p.composite_score === null ? "—" : Number(p.composite_score).toFixed(2)}</td></tr>
    </table>
    ${reason}
  `;
}

function onEachFeature(feature, layer) {
  layer.bindPopup(popupHtml(feature.properties), { maxWidth: 320 });
  layer.on({
    mouseover: e => e.target.setStyle({ weight: 2, color: "#000" }),
    mouseout: e => e.target.setStyle({ weight: 0.6, color: "#333" }),
  });
}

function buildLegend() {
  const el = document.getElementById("legend");
  el.innerHTML = `
    <span class="title">Priority class (LGA)</span>
    <div><span class="swatch sw-hi"></span> High priority</div>
    <div><span class="swatch sw-med"></span> Medium priority</div>
    <div><span class="swatch sw-lo"></span> Lower priority</div>
    <div><span class="swatch sw-val"></span> Validation needed</div>
  `;
}

async function load() {
  const [polys, states, caps, insights] = await Promise.all([
    fetch("assets/data.geojson").then(r => r.json()),
    fetch("assets/state_boundaries.geojson").then(r => r.json()),
    fetch("assets/capitals.geojson").then(r => r.json()),
    fetch("assets/insights.json").then(r => r.json()),
  ]);

  const lgaLayer = L.geoJSON(polys, { style: styleLGA, onEachFeature }).addTo(map);

  L.geoJSON(states, {
    style: { color: "#222", weight: 1.6, fill: false, opacity: 0.85 },
  }).addTo(map);

  L.geoJSON(caps, {
    pointToLayer: (f, latlng) =>
      L.circleMarker(latlng, { radius: 4, color: "#000", weight: 1, fillColor: "#fff", fillOpacity: 1 })
        .bindTooltip(f.properties.name || "", { permanent: true, direction: "right", offset: [6, 0], className: "cap-label" }),
  }).addTo(map);

  map.fitBounds(lgaLayer.getBounds(), { padding: [10, 10] });

  buildLegend();
  renderInsights(insights);
}

function renderInsights(d) {
  document.getElementById("insight-conflict-t").textContent =
    `Borno accounts for ${d.borno_share_of_recent_conflict_pct}% of the ${fmt(d.bay_acled_events_2020_2026)} ACLED political-violence events recorded across BAY since 2020. Conflict exposure is geographically concentrated, which lets a small number of LGAs be prioritised.`;

  document.getElementById("insight-displaced-t").textContent =
    `IOM DTM Round 50 (Oct 2025) records ${fmt(d.bay_idp_individuals_dtm_r50)} displaced individuals across ${d.total_lgas_bay} BAY LGAs. The school-age population (5-14) of the three states is ${fmt(d.total_school_age_5_14)}.`;

  document.getElementById("insight-validation-t").textContent =
    `${d.priority_counts.validation_needed} Adamawa LGAs are flagged "validation needed" because the iMMAP 2019 school list records 0 closed schools state-wide — a data ceiling, not a finding. Field validation must precede classification.`;
}

load().catch(err => {
  document.getElementById("map").textContent = "Failed to load map data: " + err.message;
});
