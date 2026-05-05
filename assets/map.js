// Education Continuity Priority Map, editorial briefing renderer.
// Visual goal (per the Visual Artifact Strategy doc):
//   conclusion in the foreground, data in the background.
// High priority polygons sit on top; medium and lower polygons
// are desaturated so the eye lands on red first.

const COLORS = {
  high:    "#b42318",   // red - high priority (per Visual Artifact Strategy)
  medium:  "#e8853b",   // orange - medium
  low:     "#f3d77a",   // yellow - lower
};
const FILL_OPACITY = {
  high:    0.88,
  medium:  0.62,
  low:     0.55,
};
const STROKE = {
  high:    { color: "#7a1410", weight: 0.9 },
  medium:  { color: "#a35820", weight: 0.5 },
  low:     { color: "#a08a3a", weight: 0.4 },
};
const CLASS_LABEL = {
  high:    "High priority",
  medium:  "Medium priority",
  low:     "Lower priority",
};

const map = L.map("map", {
  zoomControl: true,
  scrollWheelZoom: false,
  attributionControl: true,
}).setView([11.4, 12.7], 7);

// CartoDB Positron (light, no labels) keeps basemap quiet so the
// choropleth dominates.
L.tileLayer("https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_nolabels/{z}/{x}/{y}.png", {
  maxZoom: 11,
  minZoom: 6,
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
}).addTo(map);

function styleLGA(feature) {
  const cls = feature.properties.priority_class || "low";
  return {
    color: STROKE[cls].color,
    weight: STROKE[cls].weight,
    fillColor: COLORS[cls],
    fillOpacity: FILL_OPACITY[cls],
  };
}

function fmt(n) {
  if (n === null || n === undefined || Number.isNaN(n)) return "n/a";
  if (typeof n === "number") return n.toLocaleString();
  return n;
}

// Trimmed popup. Per the Visual Artifact Strategy section 4
// (conclusion in foreground, data in background) and reviewer
// feedback (too many indicators visible), the popup now shows
// only the four indicators that actually drive the score, the
// composite, and one source line. Nothing else.
function popupHtml(p) {
  const cls = p.priority_class || "low";
  const badgeCls = { high: "pop-hi", medium: "pop-med", low: "pop-lo" }[cls];
  const sevTxt = p.education_severity
    ? `${p.education_severity}${p.education_severity_label ? ", " + p.education_severity_label : ""}`
    : "n/a";
  const accessTxt = (p.school_age_within_5km_pct === null || p.school_age_within_5km_pct === undefined || Number.isNaN(p.school_age_within_5km_pct))
    ? "n/a"
    : `${(100 - Number(p.school_age_within_5km_pct)).toFixed(0)}% beyond 5 km`;
  return `
    <h3>${p.lga} <span class="pop-state">(${p.state})</span></h3>
    <span class="pop-class ${badgeCls}">${CLASS_LABEL[cls]}</span>
    <table>
      <tr><td class="k">Conflict events since 2020</td><td class="v">${fmt(p.events)}</td></tr>
      <tr><td class="k">Displaced individuals</td><td class="v">${fmt(p.idp_individuals)}</td></tr>
      <tr><td class="k">Education severity (JIAF 2026)</td><td class="v">${sevTxt}</td></tr>
      <tr><td class="k">School access</td><td class="v">${accessTxt}</td></tr>
      <tr><td class="k">Composite score</td><td class="v">${p.composite_score === null ? "n/a" : Number(p.composite_score).toFixed(2)}</td></tr>
    </table>
    <p class="pop-foot">Sources: ACLED, IOM DTM R50, OCHA JIAF 2026, HeiGIT.</p>
  `;
}

function onEachFeature(feature, layer) {
  const cls = feature.properties.priority_class || "low";
  layer.bindPopup(popupHtml(feature.properties), { maxWidth: 320, autoPan: true });
  layer.on({
    mouseover: e => e.target.setStyle({ weight: 1.6, color: "#000" }),
    mouseout:  e => e.target.setStyle(STROKE[cls]),
  });
  // Bring high priority polygons to the top so they read first.
  if (cls === "high") setTimeout(() => layer.bringToFront(), 0);
}

function buildLegend() {
  const el = document.getElementById("legend");
  el.innerHTML = `
    <span class="title">Priority class (LGA)</span>
    <div><span class="swatch sw-hi"></span> High priority</div>
    <div><span class="swatch sw-med"></span> Medium</div>
    <div><span class="swatch sw-lo"></span> Lower</div>
  `;
}

// Two permanent map callouts. The strategy doc allows two to four;
// fewer is better. The inline finding line above the map already
// names the Adamawa count, so the third callout was removed to
// reduce visual noise.
function addCallouts(map) {
  const callouts = [
    {
      // Anchor sits east of Bama in the empty Cameroon area; tooltip
      // floats further east so it never covers the southern Borno cluster.
      latlng: [11.45, 14.20],
      direction: "right",
      html: `<strong>Southern Borno belt</strong>10 high priority LGAs cluster here<span class="co-sub">Bama, Gwoza, Damboa, Konduga</span>`,
    },
    {
      // Anchor sits north of Yobe in the empty Niger area; tooltip floats
      // further north so it stays clear of the frontier LGAs.
      latlng: [13.80, 12.20],
      direction: "top",
      html: `<strong>Northern frontier corridor</strong>Lake Chad and Yobe border<span class="co-sub">Monguno, Mobbar, Abadam, Geidam</span>`,
    },
  ];
  callouts.forEach(c => {
    L.marker(c.latlng, { opacity: 0, interactive: false, keyboard: false })
      .addTo(map)
      .bindTooltip(c.html, {
        permanent: true,
        direction: c.direction,
        className: "map-callout",
        offset: [0, 0],
      });
  });
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
    style: { color: "#1a1a1a", weight: 1.2, fill: false, opacity: 0.7 },
  }).addTo(map);

  L.geoJSON(caps, {
    pointToLayer: (f, latlng) =>
      L.circleMarker(latlng, { radius: 3, color: "#1a1a1a", weight: 1, fillColor: "#fff", fillOpacity: 1 })
        .bindTooltip(f.properties.name || "", {
          permanent: true,
          direction: "right",
          offset: [6, 0],
          className: "cap-label",
        }),
  }).addTo(map);

  addCallouts(map);
  // Extend bounds so the off-polygon callouts (east in Cameroon,
  // north in Niger) stay on canvas at any viewport width.
  const b = lgaLayer.getBounds();
  b.extend([11.45, 14.60]);   // east room for Southern Borno callout
  b.extend([14.30, 12.20]);   // north room for Northern frontier callout
  map.fitBounds(b, { padding: [12, 12] });

  buildLegend();
  renderFindings(insights);
}

function renderFindings(d) {
  const high = d.priority_counts.high;
  const kpiEl = document.getElementById("kpi-high-num");
  if (kpiEl) kpiEl.textContent = high;

  const cellConflict = document.getElementById("cell-conflict");
  if (cellConflict) cellConflict.textContent = fmt(d.bay_acled_events_2020_2026);

  const cellIdp = document.getElementById("cell-idp");
  if (cellIdp) cellIdp.textContent = fmt(d.bay_idp_individuals_dtm_r50);

  const cellPin = document.getElementById("cell-pin");
  if (cellPin) cellPin.textContent = fmt(d.bay_education_pin_jiaf_2026);
}

load().catch(err => {
  document.getElementById("map").textContent = "Failed to load map data: " + err.message;
});
