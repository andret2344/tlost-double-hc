local mod = RegisterMod("Double Holy Cards for Tainted Lost", 1)

local DEBUG = false
local LOG_TAG = "[TLOST_DOUBLE_HC] "

-- Extra roll on top of vanilla's own Tainted Lost roll, which is exactly 10%
-- (`RandomInt(10) == 0` in REPENTOGON's reimplementation of ItemPool::GetCardEx).
-- Combined chance = 0.1 + 0.9 * HOLY_CARD_CHANCE, so 1/9 (~11.1%) gives 20% total, twice vanilla.
local HOLY_CARD_CHANCE = 1 / 9

-- Only real cards get the extra roll; runes, soul stones and objects like Dice Shard stay as rolled
-- (vanilla's 10% roll still applies to them).
local REPLACEABLE_CARD_TYPES = {
    [ItemConfig.CARDTYPE_TAROT] = true,
    [ItemConfig.CARDTYPE_SUIT] = true,
    [ItemConfig.CARDTYPE_SPECIAL] = true,
    [ItemConfig.CARDTYPE_TAROT_REVERSE] = true,
}

local itemConfig = Isaac.GetItemConfig()

local function log(message)
    if DEBUG then
        Isaac.DebugString(LOG_TAG .. message)
    end
end

-- Same condition as vanilla: any player in the game being Tainted Lost counts, also in co-op.
local function isTaintedLostInGame()
    local game = Game()
    for i = 0, game:GetNumPlayers() - 1 do
        if Isaac.GetPlayer(i):GetPlayerType() == PlayerType.PLAYER_THELOST_B then
            return true
        end
    end
    return false
end

-- MC_GET_CARD fires only when the game rolls a random card, so cards dropped from the
-- inventory and scripted spawns with a fixed subtype never reach this callback (verified in game).
-- The game-provided rng keeps the extra roll deterministic per seed.
---@param rng RNG
---@param card Card
function mod:onGetCard(rng, card)
    if card == Card.CARD_HOLY or not isTaintedLostInGame() then
        return nil
    end
    local config = itemConfig:GetCard(card)
    if not config or not REPLACEABLE_CARD_TYPES[config.CardType] then
        return nil
    end
    if rng:RandomFloat() < HOLY_CARD_CHANCE then
        log("Replaced card " .. card .. " with Holy Card")
        return Card.CARD_HOLY
    end
    return nil
end

mod:AddCallback(ModCallbacks.MC_GET_CARD, mod.onGetCard)
