-- 删除数据会议终端
-- 参数: confE164 mtE164 time

local function getDcsTerminalInfo(confE164, mtE164)
    local r = {}
    local infoList = redis.call("HGETALL", "terminal:" .. mtE164 .. ":conf:" .. confE164 .. ":info_for_dcs")
    for i = 1, #infoList / 2 do
        r[infoList[i * 2 - 1]] = infoList[i * 2]
    end
    r["dcs_moid"] = redis.call("HGET", "meeting:" .. confE164 .. ":dcs_info", "dcs_moid")
    return r
end

local function delDcsTerminalInfo(confE164, mtE164)
    redis.call("SREM", "meeting:" .. confE164 .. ":dcs_terminals", mtE164)
    redis.call("DEL", "terminal:" .. confE164 .. ":conf:" .. mtE164 .. ":info_for_dcs")
end

local confE164 = ARGV[1]
local mtE164 = ARGV[2]
local time = ARGV[3]
local result = {}

result = getDcsTerminalInfo(confE164, mtE164)
result["end_time"] = time

delDcsTerminalInfo(confE164, mtE164)

return string.gsub(cjson.encode(result), "{}", "[]")
