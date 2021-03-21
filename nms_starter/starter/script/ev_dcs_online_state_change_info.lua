-- 终端在线状态改变
-- 参数: confE164 mtE164 onlineState changeTime

local function getDcsTerminalInfo(confE164, mtE164)
    local r = {}
    local infoList = redis.call("HGETALL", "terminal:" .. mtE164 .. ":conf:" .. confE164 .. ":info_for_dcs")
    for i = 1, #infoList / 2 do
        r[infoList[i * 2 - 1]] = infoList[i * 2]
    end
    r["dcs_meeting_moid"] = redis.call("HGET", "meeting:" .. confE164 .. ":dcs_info", "dcs_meeting_moid")
    return r
end

local confE164 = ARGV[1]
local mtE164 = ARGV[2]
local onlineState = ARGV[3]
local changeTime = ARGV[4]

local result = {}
if onlineState == "0" or onlineState == 0 then
    result = getDcsTerminalInfo(confE164, mtE164)
    result["end_time"] = changeTime
    redis.call("SREM", "meeting:" .. confE164 .. ":dcs_terminals", mtE164)
    redis.call("DEL", "terminal:" .. mtE164 .. ":conf:" .. confE164 .. ":info_for_dcs")
end

return string.gsub(cjson.encode(result), "{}", "[]")
