# The culling — analysis

Goal: free **~84 monster slots** (#1–#300 and the #351–365 tail) for the new cards,
without wrecking the opponents we designed. The natural first idea — "cut the weakest
cards that no opponent plays" — turns out to free almost nothing. DM1 is **densely
packed**.

## Finding: only 24 of 315 monsters are unused by opponents

Of **163 monsters at ≤1000 ATK, just 8 are in no deck.** Skull Servant — the archetypal
"weak card to cut" — is in **5** opponent decks. Almost every weak card is load-bearing
filler in multiple decks.

### The non-deck monsters (24 total), split

**Genuinely cullable (~15)** — weak, unused, not in any of our designs:

| # | name | ATK/DEF | zone |
|---:|---|---|---|
| 362 | Millennium Shield | 0/3000 | tail |
| 359 | 3-Legged Zombies | 1100/800 | tail |
| 354 | Stuffed Animal | 1200/900 | tail |
| 361 | Flying Penguin | 1200/1000 | tail |
| 351 | Yaranzo | 1300/1500 | tail |
| 363 | Fairy's Gift | 1400/1000 | tail |
| 352 | Kanan Swordmistress | 1400/1400 | tail |
| 353 | Takriminos | 1500/1200 | tail |
| 355 | Megasonic Eye | 1500/1800 | tail |
| 357 | Yamadron | 1600/1800 | tail |
| 365 | Fiend's Mirror | 2100/1800 | tail |
| 356 | Super War Lion | 2300/2100 | tail |
| 358 | Seiyaryu | 2500/2300 | tail |
| 360 | Zera the Mant | 2800/2300 | tail |
| 56 | Larvae Moth | 500/400 | #1–300 (Moth-line material — marginal) |

**Must keep (9)** — used in our designs:
Exodia pieces #17–21 (Simon rewards), Great Moth #57 & Perfect Great Moth #67 (Weevil),
Black Luster Soldier #364 (Kaiba's Dragon Master Knight material), Cocoon of Evolution
#72 (fusion material).

So the "not in any deck" cull yields **~15 slots** — the whole #351–365 tail plus a
couple. We need ~84.

## Consequence: the culling must touch decks — and that's fine

The other ~69 slots have to come from cards opponents currently play. This is not a
problem, because:

1. **We're already redesigning every opponent's deck** (adding new cards). Removing a
   weak card from a deck is the same edit.
2. **Weak cards sit in many decks at once** — culling Skull Servant (in 5 decks) cleans
   all 5 simultaneously. The current decks are padded with low-ATK filler; thinning it
   is the whole "modernize" goal.
3. The tighter decks that result are *more* on-theme, not less.

## Recommended method: slot-coherent culling (not a flat list)

Rather than a global kill-list, assign slots **opponent by opponent**: overwrite an
opponent's weakest filler with a new card destined for *that same opponent*, so the deck
stays coherent automatically.

Example — Weevil: overwrite a weak insect he plays (e.g. Basic Insect 500, in his deck)
with **Insect Queen** (his new card). His deck weight for that slot now points at Insect
Queen — no separate deck edit needed. Repeat across the roster.

This folds the culling and slot-assignment into one pass, keeps every deck valid, and
naturally retires exactly the weak filler we want gone.

## Protection rule: high DEF is immune (owner)

**Any card with 1500+ DEF is exempt from the big cut** — a 1200/2200 wall or an 800/2000
blocker has real defensive value even at low ATK, so ATK alone shouldn't condemn it.

Feasibility (verified): of 266 weak monsters (ATK ≤ 1500), **234 have DEF < 1500** and are
cull-eligible — far more than the ~84 slots we need. The rule **protects 32 cards**,
including Millennium Shield (0/3000), Faceless Mage (1200/2200), Metal Guardian
(1150/2150), Mystical Elf (800/2000), Catapult Turtle (1000/2000), Aqua Madoor (1200/2000),
Giant Rock Soldier (1300/2000), and Castle of Illusions (920/1930). Plenty of low-DEF
filler remains to cut, so the protection costs us nothing.

Cull-eligibility going forward: **weak (low ATK) AND DEF < 1500 AND not used in a design.**

## Next step

Two ways to proceed:
- **(A)** Do the slot-coherent pass now — I map all 84 new cards onto specific weak-card
  slots, opponent by opponent, and produce the assignment table.
- **(B)** First lock a flat "retire these N" list for the tail + obvious junk (the ~15
  free ones), then handle the #1–300 overwrites during the compiler build.

The tail 15 are free either way. The interesting decisions are all in #1–300.
