---
colors:
  canvas: "#0B1020"
  panel: "#14213D"
  panelRaised: "#1A2A4A"
  line: "#2B4162"
  text: "#F5F7FA"
  muted: "#A8B3C7"
  teal: "#36D1C4"
  green: "#51D88A"
  amber: "#F4B400"
  red: "#FF5C6C"
typography:
  display:
    family: "Arial Black"
    weight: 900
  body:
    family: "Segoe UI"
    weight: 500
  data:
    family: "Consolas"
    weight: 700
spacing:
  frameX: 112
  frameY: 76
  grid: 16
components:
  cornerRadius: 18
  border: "1px solid #2B4162"
  glow: "0 0 42px rgba(54, 209, 196, 0.16)"
---

# Evidence Corridor

## The Frame

Every scene lives inside a fixed control-plane shell: a top metadata rail, a numbered scene index, a large central mechanism, and a bottom narration rail. The composition should feel engineered and legible at laptop scale.

## Composition Rules

- Use an explicit 1920 × 1080 root.
- Keep critical text inside 112 px horizontal and 76 px vertical safe areas.
- Use sharp grid alignment and restrained 18 px radii.
- Reserve teal for governed routing and active evidence.
- Reserve status colors for decisions; do not use them as decoration.
- Prefer large sentence fragments over dense paragraphs.
- Use depth only through subtle panel elevation and ambient glow.

## Motion Rules

- Animate opacity and transforms, not layout properties.
- Connector movement should lead the eye from evidence to authority.
- Entrances settle quickly; important results hold long enough to read.
- All motion must remain deterministic when the timeline is seeked.

