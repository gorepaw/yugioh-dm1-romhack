# Project 2 — opponent roster & decks

Separate from `docs/DECKLISTS.md` (that's Product 1). P2 opponents get freshly
built **creatures-only** decks from our MTG creature pool (`work/p2/cards.json`).

**Opponents summon monsters only** — no magic/equip/field cards ever appear in a
deck. Decks are authored in `work/p2/deck_config.json` as `{pool: {card_id:
weight}}`, normalized to the engine's 2048 total and written to bank 8 by
`build.py` via `decks.py` (which refuses any non-monster card). Build order is
**top-down by deck power**, since slot id is only a data index, not the campaign
order (the encounter order/gating is unmapped; difficulty is set purely by deck).

## The 16-opponent ladder (slot → pool → identity)

| Slot | DM1 name | Pool | Opponent | Color | Tier | Deck |
|--:|---|--:|---|---|---|---|
| 15 | YamiYugi | 4 | **Yawgmoth** | Black | Final | ✅ done |
| 14 | Pegasus | 15 | **Urza** | White/Artifact | Brothers | ✅ done |
| 13 | Simon | 16 | **Mishra** | Red/Artifact | Brothers | ✅ done |
| 12 | Bakura | 11 | **Nicol Bolas** | Black | Elder Dragons | |
| 11 | Joey | 7 | **Vaevictis** | Red | Elder Dragons | |
| 10 | Tristan | 10 | **Palladia** | Green | Elder Dragons | |
| 9 | Yugi | 5 | **Chromium** | Blue | Elder Dragons | |
| 8 | Keith | 14 | **Arcades** | White | Elder Dragons | |
| 7 | PaniK | 13 | **Teferi** ⭐ | Blue | Master mages | |
| 6 | Puppeter | 12 | **Tawnos** | Artifact | Master mages | |
| 5 | Mokuba | 9 | **Ashnod** | Black | Master mages | |
| 4 | Kaiba | 8 | **Serra** | White | Rising mages | |
| 3 | Mako | 3 | **Jasmine** | Green | Rising mages | |
| 2 | Rex | 2 | **Feldon** | Red | Rising mages | |
| 1 | Mai | 1 | **Ali Baba** | Red | Novices | |
| 0 | Weevil | 0 | **Sindbad** | Blue | Novices | |

## 15 — Yawgmoth (pool 4) — DONE
Black demons/horrors + colorless Phyrexian war-machines. 21 monsters, weighted
toward the bombs so the final duel is brutal. No spells; Nicol Bolas excluded
(he's a rival on slot 12).

| Card | ATK/DEF | share |
|---|--:|--:|
| Yawgmoth Demon | 2800/2400 | 9.8% |
| Cosmic Horror | 3000/2800 | 8.8% |
| Colossus of Sardia | 3750/3600 | 6.8% |
| Lord of the Pit | 3200/2800 | 6.4% |
| Mold Demon | 2400/2400 | 6.3% |
| Nightmare | 2400/2000 | 5.9% |
| Ebon Praetor | 2350/2000 | 5.4% |
| Sengir Vampire · Juzam Djinn | 2000/… | 4.9% each |
| Demonic Hordes · Juggernaut | 2000–2200 | ~4.7% each |
| Mishra's War Machine · Urza's Avenger | 2000–2100 | ~4% each |
| Fallen Angel · Derelor · Nameless Race | 1500–1600 | ~2% each |
| Bog Wraith · Junun Efreet · Obsianus Golem · Su-Chi · Black Knight | 1200–1600 | tail |

Total = 2048, 21 distinct monsters. Built & verified in the ROM.

## 14 — Urza (pool 15) — DONE
White knights/angels + refined artifact constructs. Signatures: **Urza's Avenger**
(8.2%) + **Akron Legionnaire** 3200/1600 (8.9%) + Colossus. 22 monsters.

## 13 — Mishra (pool 16) — DONE
Red aggression + brutal war-machines. Signature **Mishra's War Machine** (9.3%),
plus Orgg, Ball Lightning, Shivan Dragon, Juggernaut, Colossus. 21 monsters.

## 12–8 — the Elder Dragons (pools 11/7/10/5/14)
Each = their **4000/4000 self as the centerpiece** (high weight) + the top ~20
monsters of their color. Nicol Bolas (B), Vaevictis (R), Palladia (G), Chromium
(U), Arcades (W). Upper-mid tier — strong, but a step under the Brothers.
