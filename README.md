<div align="center">

# Double Holy Cards for Tainted Lost

**A small, focused mod for The Binding of Isaac: Repentance+**<br>
Tainted Lost finds Holy Cards twice as often. Nothing else changes.

[![CI](../../actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)
![Repentance+](https://img.shields.io/badge/Isaac-Repentance%2B-8b0000)
![Lua 5.3](https://img.shields.io/badge/Lua-5.3-000080?logo=lua)
![No REPENTOGON](https://img.shields.io/badge/REPENTOGON-not%20required-success)

</div>

---

Tainted Lost dies to a single hit, and the Holy Card is the one thing that buys a second chance.
In vanilla, every card that spawns has a **10%** chance to become a Holy Card. This mod raises it
to **20%**: noticeable over a run, but the character keeps its edge.

## At a glance

|                                              | Vanilla | With the mod   |
| -------------------------------------------- | :-----: | :------------: |
| Random card turns into a Holy Card           |   10%   |    **20%**     |
| Runes, soul stones, Dice Shard, Cracked Key… |   10%   | 10% (untouched) |
| Holy Card in a shop                          |  paid   |   still paid   |

## What changes

The extra chance applies to every card the game **rolls at random**:

- room clear rewards, chests and other natural drops,
- shop cards (they keep their price),
- items that roll cards, such as Deck of Cards or Booster Pack.

Eligible card types: tarot, reversed tarot, playing cards and special cards.

## What stays the same

- **Cards you drop from your inventory** come back exactly as they were.
- **Scripted spawns** with a fixed card, such as The Fool on Depths II and its alternates.
- **Runes, soul stones and special objects** (Dice Shard, Cracked Key, …) only get vanilla's 10%.
- **Every other character.** The mod is active only when a Tainted Lost is in the game, also in co-op.
- **No unlock required**, same as vanilla: Tainted Lost gets Holy Cards even before the card is unlocked.

## How it works

The mod hooks `MC_GET_CARD`, which fires only when the game picks a random card. If the rolled card
is eligible and is not already a Holy Card, it gets one extra roll:

```
combined = 0.1 + 0.9 × p        p = 1/9  →  combined = 0.2
```

The roll uses the RNG the game passes to the callback, so runs stay deterministic per seed.

**Where the 10% comes from.** The wiki only says "roughly 10%". The exact value comes from
[REPENTOGON's reimplementation](https://github.com/TeamREPENTOGON/REPENTOGON/blob/main/repentogon/Patches/CardsExtras.cpp)
of `ItemPool::GetCardEx`, which replaces the vanilla function and has to reproduce it: the game
checks `RandomInt(10) == 0` on a separate RNG whenever any player is Tainted Lost.

**Known limitation.** Vanilla skips its Holy Card roll when a card roll excludes special cards.
`MC_GET_CARD` does not expose that information, so in such a roll the mod may still give a Holy
Card. Rune-only rolls are not affected, because runes are never replaced.

## Measured in game

203 random cards spawned in a single Tainted Lost run:

|                         | Result                                                              |
| ----------------------- | ------------------------------------------------------------------- |
| Holy Cards              | 39 / 203 = **19.2%**                                                |
| Expected                | ~18.9% (11% of the rolls were runes and objects, which keep 10%)    |
| 95% confidence interval | 13.8–24.6%                                                          |

Vanilla-only 10% (p < 0.0001) and a stacked 28% (p ≈ 0.003) are both ruled out.

## Compatibility

- Built for **Repentance+** on the vanilla Lua API. REPENTOGON is not required.
- Do not combine it with other mods that replace cards through `MC_GET_CARD`, such as *More Holy
  Cards for Tainted Lost*. The game keeps only the last callback's result, so the odds become
  unpredictable.

## Installation

**Steam Workshop:** the link will be added with the first release.

**Manual:** copy `main.lua` and `metadata.xml` into a new folder inside
`steamapps\common\The Binding of Isaac Rebirth\mods\`, then enable the mod in the in-game Mods menu.

## Development

**Setup**

- VS Code with [Lua](https://marketplace.visualstudio.com/items?itemName=sumneko.lua) and
  [Binding of Isaac Lua API](https://marketplace.visualstudio.com/items?itemName=Filloax.isaac-lua-api-vscode).
- The workspace settings in `.vscode/` turn REPENTOGON definitions off, so autocomplete offers
  only the vanilla API. Accept the extension's prompt to activate it for this workspace.
- The `Isaac: tail log` task (Terminal, Run Task) follows the game log, filtered to this mod and
  errors.
- Link the repo into the game's mods folder:
  ```powershell
  New-Item -ItemType Junction -Path "C:\Program Files (x86)\Steam\steamapps\common\The Binding of Isaac Rebirth\mods\tlost-double-hc" -Target "<path to this repo>"
  ```

**Workflow** (in-game console, enable it with `EnableDebugConsole=1` in `options.ini`)

| Command                   | Purpose                                |
| ------------------------- | -------------------------------------- |
| `luamod tlost-double-hc`  | Reload the mod without restarting      |
| `restart 31`              | New run as Tainted Lost                |
| `spawn 5.300.0`           | Spawn a random card                    |
| `spawn 5.300.1`           | Spawn The Fool (fixed subtype)         |

Logs go to `Documents\My Games\Binding of Isaac Repentance+\log.txt` with the `[TLOST_DOUBLE_HC]`
prefix when `DEBUG = true`.

**Testing.** The game cannot be run headless, so behavior is tested by hand: set
`HOLY_CARD_CHANCE = 1` and `DEBUG = true`, then check that random cards turn into Holy Cards
while inventory drops, fixed spawns, runes and other characters stay untouched. To measure the
rate with the real value, spawn a batch and count `5.300.51` in the log:

```
lua for i = 1, 100 do Isaac.Spawn(5, 300, 0, Isaac.GetRandomPosition(), Vector(0, 0), nil) end
```

**CI** runs on every push and pull request:

- **Lua against the vanilla API:** `lua-language-server --check` with the vanilla API definitions,
  so typos, unknown globals and REPENTOGON-only calls fail the build.
- **Metadata and release config:** `metadata.xml` is valid and its name matches `RegisterMod`,
  and no test values (`DEBUG = true`, `HOLY_CARD_CHANCE = 1`) are left in `main.lua`.

## Credits

- API definitions: [filloax/isaac-lua-api-vscode](https://github.com/filloax/isaac-lua-api-vscode)
- Reverse-engineered card logic: [TeamREPENTOGON/REPENTOGON](https://github.com/TeamREPENTOGON/REPENTOGON)
- API documentation: [IsaacDocs](https://wofsauge.github.io/IsaacDocs/rep/)
