-- 终端协作状态改变消息
-- 参数: confE164 mtE164 time coopState

local function getDcsTerminalInfo(confE164, mtE164)
    local r = {}
    local infoList = redis.call("HGETALL", "terminal:" .. mtE164 .. ":conf:" .. confE164 .. ":info_for_dcs")
    for i = 1, #infoList / 2 do
        r[infoList[i * 2 - 1]] = infoList[i * 2]
    end
    r["dcs_moid"] = redis.call("HGET", "meeting:" .. confE164 .. ":dcs_info", "dcs_moid")
    return r
end

local function addDcsTerminal(confE164, mtE164, coopState, beginTime)
    local dscTerminalsKey = "meeting:" .. confE164 .. ":dcs_terminals"
    local terminalInfoForDcsKey = "terminal:" .. mtE164 .. ":conf:" .. confE164 .. ":info_for_dcs"
    redis.call("SADD", dscTerminalsKey, mtE164)
    local name = redis.call("HGET", "terminal:" .. mtE164 .. ":baseinfo", "name")
    redis.call(
        "HMSET",
        terminalInfoForDcsKey,
        "name",
        name,
        "e164",
        mtE164,
        "coop_state",
        coopState,
        "begin_time",
        beginTime
    )
end

local confE164 = ARGV[1]
local mtE164 = ARGV[2]
local time = ARGV[3]
local coopState = ARGV[4]
local result = {}

local dcsTerminalsKey = "meeting:" .. confE164 .. ":dcs_terminals"

-- 状态改变, 记录
if redis.call("SISMEMBER", dcsTerminalsKey, mtE164) then
    result = getDcsTerminalInfo(confE164, mtE164)
    result["end_time"] = time
end

addDcsTerminal(confE164, mtE164, coopState, time)

return string.gsub(cjson.encode(result), "{}", "[]")
