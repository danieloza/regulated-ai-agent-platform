# Regulated AI Workflow Explainer

Reproducible source for the watermark-free workflow animation used in the repository README.

## Regenerate

```bash
npm install
npm run check
npx hyperframes render --quality high --fps 30 --output renders/regulated-ai-workflow-explainer.mp4
```

Narration is generated locally with Kokoro and committed as scene-aligned WAV files. No external API key is required to check or render the existing composition.

## Source Map

- `BRIEF.md` — audience, claims, and boundaries
- `SCRIPT.md` — approved narration
- `STORYBOARD.md` — scene timing and visual intent
- `frame.md` — visual system
- `compositions/` — deterministic scene implementations
- `assets/voice/` — local narration

