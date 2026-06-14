---
license: apache-2.0
base_model: Qwen/Qwen2.5-7B-Instruct
tags:
  - text-generation
  - horror
  - register-transfer
  - lovecraft
language:
  - en
---

# nyarlathotep: a cosmic-horror register oracle

A 7B voice tune that writes in the register of cosmic horror: the indifferent cosmos,
forbidden knowledge that unmakes the mind, the unnameable, the gulf between the stars.
The conceit is Nyarlathotep, the Crawling Chaos, the messenger of the Outer Gods who
walks among men and discloses what waits in the dark.

It channels the dread, not the author. The model trains on H. P. Lovecraft's
cosmic-horror fiction, which is public domain, but it does not reconstruct Lovecraft the
person. Two filters strip his documented racism from the corpus: stories whose premise
is the bigotry are dropped whole, and every remaining passage is scanned and dropped if
it carries a slur or racial-fear vocabulary. What survives is the atmosphere.

## What it does

Ask it anything and it answers from the abyss. It will not comfort you; it discloses.
Asked a mundane question, it cannot describe a night sky without the gods shaping cosmos
from primal chaos, or an old house without the wrong angles and the thing in the walls.
Asked what it is, it answers as the entity of a thousand guises.

## How it was built

- **Base:** Qwen2.5-7B-Instruct, full fine-tune.
- **Format:** completion (raw text), so the dread comes from the source prose rather than
  from instruction scaffolding.
- **Source:** Lovecraft's public-domain fiction, racism-filtered (title blocklist + a
  per-passage slur/term filter), chunked to roughly 2,000 completion records.
- **Inference:** a lead-in frame elicits the oracle voice. Plain chat suppresses the
  register; the name-cue lead-in makes the model disclose as the entity.

## Intended use

Creative writing, atmosphere generation, tabletop and interactive fiction, games. The
output is a horror-fiction register. It produces dread on purpose and offers no facts,
advice, or reassurance.

## Limitations and honest notes

- **It is a register, not a narrator with continuity.** It invents names, places, and
  cosmologies freely. Treat everything it says as fiction.
- **Filtered, not sanitized of horror.** The racism filters target Lovecraft's bigotry,
  not the cosmic dread. The model is built to disturb. The deity name "Shub-Niggurath" is
  a canonical mythos term, not a slur, and survives the word-boundary filter by design.
- **Period diction.** It writes in the archaic, ornate cadence of the old weird tale.

## License

Apache-2.0. The source fiction is public domain and the base model is Apache-2.0, so the
weights ship under a permissive license. No warranty.
