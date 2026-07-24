# DM1 opponent progression (the REAL play order)

The duelist **index** in the ROM data (0–15) is *not* the play order. The game gates
opponents into **5 stages**; you must beat every duelist in a stage 5× to advance.
Sources: GameFAQs (deathcrush94), Yugipedia, Yu-Gi-Oh Wiki. Confirmed the endpoints
against the ROM's own deck/reward data.

| Stage | Opponents (roster index) | Role |
|---|---|---|
| 1 | Yugi (9), Tristan (10), Joey (11), Bakura (12) | your friends — tutorial-easy, "set and pass" |
| 2 | Weevil (0), Mai (1), Rex (2), Mako (3), Kaiba (4), Mokuba (5), Puppeteer (6), PaniK (7), Keith (8) | the Duelist Kingdom pack — bulk of the game |
| 3 | **Simon Muran (13)** | game-original character; the sole gate before Pegasus |
| 4 | **Pegasus (14)** | main-game **final boss** — beating him 5× rolls credits |
| 5 | **Yami Yugi (15)** | secret post-credits "Dark Stage" — the **true final** |

Notes:
- **Pegasus is the main final boss; Yami Yugi is the secret true-final** unlocked after
  the credits. So the index order (Yami=15, Pegasus=14) *does* happen to end the game,
  which is why working from index 15 downward has been correct so far.
- Puppeteer (6) and PaniK (7) are two separate roster slots though the anime treats
  Panik/the Puppeteer of Doom as one character; both sit in Stage 2.
- Within a stage, order is free — you can duel them in any sequence.

## Working backwards from the end (our design order)

1. **Yami Yugi** (Stage 5, true final) — ✅ done
2. **Pegasus** (Stage 4, main final) — ✅ done
3. **Simon Muran** (Stage 3, lone gate) — ◀ **next**
4. **Stage 2 pack** (Keith, PaniK, Puppeteer, Mokuba, Kaiba, Mako, Rex, Mai, Weevil)
5. **Stage 1 friends** (Bakura, Joey, Tristan, Yugi)

The two hardest/most-marquee opponents (Yami, Pegasus) are done. Simon is a mini-boss;
after him the Stage 2 pack is where the **budget discipline** kicks in — 9 duelists that
should mostly stay near-stock, with maybe Kaiba as the one big themed set (Blue-Eyes).

## Simon Muran — stock profile (Stage 3)

Duelist 13 / pool 16. His stock deck is **19 cards, every one a Spellcaster** — a clean
"mage" identity already. But it's weak for a gatekeeper: top end is Rogue Doll (1600)
and Spirit of Winds (1700); the body is 800–1300 mages. Rewards notably include
**Exodia's head (#21) at 90 wins**.

He's a **game-original character** (not from the manga), so his new identity is wide
open — the existing all-Spellcaster theme is a strong anchor to build a proper
"sorcerer mini-boss" on.
