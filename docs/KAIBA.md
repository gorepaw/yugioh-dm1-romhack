# Kaiba — deck, drops, rewards (proposal, kaizo)

Duelist 4 / pool 8 · **Stage 2** — the one big themed set in the pack. Nothing here is
in the ROM yet.

Identity: **dragons** (the roster's dragon pillar — Keith takes machines, Rex takes
dinos). Additive: his stock beatdown deck stays as the beatable body, the dragon package
layered on. His stock deck is a 61-card grab-bag with only 3 dragons and Blue-Eyes
buried at 1.2%, so "dragons" is almost entirely the new layer.

## Design — Kaiba is the grind engine

His power cards appear in his deck/drops **less often than the bosses use theirs**, and
the **4k+ cards are commensurately rare** — all at the 0.05% floor, rarer than Yami's
Gods (0.15%). So:

- **Primary path:** grind his **100-win reward ladder** (his 10 best cards, one per 10
  wins) — the reliable way to build toward endgame-tier power.
- **Speedrun path:** don't grind — assemble the dragons yourself via **fusion**, or pump
  lesser dragons with **Mountain fields (+30%) and equips**. Blue-Eyes is now a real
  (rare) drop, so you can farm two and fuse up.

## New cards — 10 dragons (+ featuring existing Blue-Eyes #1)

| in-game name | tiles | ATK/DEF | tag | flavour |
|---|---:|---|---|---|
| D.D. Dragon | 11 | 1200/1500 | | `A wyrm from` / `another dimension.` |
| Luster Dragon 2 | 15 | 2400/1400 | | `A sapphire wyrm` / `of great worth.` |
| Kaiser Glider | 12 | 2400/2200 | | `A golden dragon` / `guards the king.` |
| Tyrant Dragon | 13 | 2900/2500 | | `A ruthless wyrm` / `with no mercy.` |
| Rabidragon | 10 | 2950/2900 | | `A colossal beast` / `of raw fury.` |
| ChaosEmperorDrgn | 16 | 3000/2500 | ⚠ = Blue-Eyes stats | `Envoy of the end` / `and oblivion.` |
| BlueEyesTyrantDrg | 17 | 3400/2900 | fusion | `Blue-Eyes fused` / `with the tyrant.` |
| BlueEyesChaosMax | 16 | 4000/0 | ritual→vanilla | `Blue-Eyes drowned` / `in chaos light.` |
| BlueEyesUltDragon | 17 | 4500/3800 | fusion | `Three white` / `dragons as one.` |
| DragonMasterKnght | 17 | 5000/5000 | fusion | `Rider and dragon,` / `ultimate union.` |

**144 name tiles.** `Dragon Master Knight (5000/5000)` becomes the single strongest card
in the game. One collision: **Chaos Emperor Dragon is 3000/2500 — identical to Blue-Eyes
White Dragon** (no-effects engine). They're stat-twins; nudge Chaos Emperor (e.g.
3000/2600) if you want them distinct, else they're the same card with different art.

## Fusion chain — the speedrun (maps to our 2-material engine)

- **Blue-Eyes + Blue-Eyes → Blue-Eyes Ultimate Dragon** (4500) — the 3-BEWD fusion,
  approximated as two copies
- **Blue-Eyes Ultimate + Black Luster Soldier → Dragon Master Knight** (5000) — the real
  recipe; a two-step apex chain
- **Blue-Eyes + Tyrant Dragon → Blue-Eyes Tyrant Dragon** (3400) — its real recipe; both
  materials are in Kaiba's set
- Blue-Eyes Chaos MAX is a ritual → standalone (reward/drop only, no fusion)

Fusion-zone (#1–#300) needs: Ultimate, Master Knight, Blue-Eyes Tyrant (results) +
Tyrant Dragon (material) + **Black Luster Soldier #364 must move into #1–#300** (material).

## Deck — 71 cards (stock 84% / dragons 16%), weights /2048

Additive. Stock beatdown is the body; dragons layered on with the apex vanishingly rare:

| wt | % | ATK/DEF | dragon |
|---:|---:|---|---|
| 72 | 3.52 | 1200/1500 | D.D. Dragon |
| 67 | 3.27 | 2400/1400 | Luster Dragon 2 |
| 67 | 3.27 | 2400/2200 | Kaiser Glider |
| 46 | 2.25 | 2900/2500 | Tyrant Dragon |
| 42 | 2.05 | 2950/2900 | Rabidragon |
| 34 | 1.66 | 3000/2500 | Blue-Eyes White Dragon (#1, featured) |
| 15 | 0.73 | 3000/2500 | Chaos Emperor Dragon |
| 2 | 0.10 | 3400/2900 | Blue-Eyes Tyrant Dragon |
| 1 | 0.05 | 4000/0 | Blue-Eyes Chaos MAX |
| 1 | 0.05 | 4500/3800 | Blue-Eyes Ultimate Dragon |
| 1 | 0.05 | 5000/5000 | Dragon Master Knight |

The three 4k+ dragons are at the 0.05% floor — you will almost never see them in play,
which is the point.

## Drop table — 44 cards (stock + dragons), weights /2048

Blue-Eyes is a **real rare drop at last** (1.32%) — finally obtainable, and enough to
farm two copies for the Ultimate fusion. Weak/mid dragons ~2.4%; the apex at the 0.05%
floor so drops are *not* a shortcut to the top — the reward grind is:

| % | dragon |
|---:|---|
| 2.39 | D.D. Dragon · Luster Dragon 2 · Kaiser Glider |
| 1.32 | **Blue-Eyes White Dragon** · Tyrant Dragon |
| 1.12 | Rabidragon |
| 0.44 | Chaos Emperor Dragon |
| 0.10 | Blue-Eyes Tyrant Dragon |
| 0.05 | Blue-Eyes Chaos MAX · Blue-Eyes Ultimate · Dragon Master Knight |

## Rewards — his 10 most powerful, 100 → 10 (the primary path)

| Wins | ATK | card | | Wins | ATK | card |
|---:|---:|---|---|---:|---:|---|
| 100 | 5000 | Dragon Master Knight | | 50 | 3000 | Chaos Emperor Dragon |
| 90 | 4500 | Blue-Eyes Ultimate Dragon | | 40 | 2950 | Rabidragon |
| 80 | 4000 | Blue-Eyes Chaos MAX | | 30 | 2900 | Tyrant Dragon |
| 70 | 3400 | Blue-Eyes Tyrant Dragon | | 20 | 2400 | Kaiser Glider |
| 60 | 3000 | Blue-Eyes White Dragon | | 10 | 2400 | Luster Dragon 2 |

(D.D. Dragon at 1200 is the 11th, left off — deck/drop only.) Guardian-style: the ids
for the new cards fill in at slot-assignment time; recorded by name for now.

## Running budget (4 of 16 duelists)

| | new cards | name tiles |
|---|---:|---:|
| Yami | 27 | 420 |
| Pegasus | 18 | 279 |
| Simon | 4 | 55 |
| Kaiba | 10 | 144 |
| **total** | **59** | **898** |

59 of 365 slots, 898 of 4480 tiles. Kaiba is the last big set in Stage 2 — the other 8
duelists there stay near-stock (light additions only), which the remaining budget
comfortably supports.
