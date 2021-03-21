-- 数据会议结束
-- 参数: confE164 time

local function delDcsTerminalInfo(confE164, mtE164)
    redis.call("SREM", "meeting:" .. confE164 .. ":dcs_terminals", mtE164)
    redis.call("DEL", "terminal:" .. confE164 .. ":conf:" .. mtE164 .. ":info_for_dcs")
end

local function delDcsMeeting(confE164)
    redis.call("DEL", "meeting:" .. confE164 .. ":dcs_terminals")
    redis.call("DEL", "meeting:" .. confE164 .. ":dcs_info")
end

local function getDcsTerminalInfo(confE164, mtE164)
    local r = {}
    local infoList = redis.call("HGETALL", "terminal:" .. mtE164 .. ":conf:" .. confE164 .. ":info_for_dcs")
    for i = 1, #infoList / 2 do
        r[infoList[i * 2 - 1]] = infoList[i * 2]
    end
    r["dcs_moid"] = redis.call("HGET", "meeting:" .. confE164 .. ":dcs_info", "dcs_moid")
    return r
end

local function getDcsInfo(confE164)
    local r = {}
    local infoList = redis.call("HGETALL", "meeting:" .. confE164 .. ":dcs_info")
    for i = 1, #infoList / 2 do
        r[infoList[i * 2 - 1]] = infoList[i * 2]
    end
    return r
end

local function getDcsModeInfo(confE164, endTime)
    local r = {}
    local dcsInfoKey = "meeting:" .. confE164 .. ":dcs_info"
    r["dcs_mode"] = redis.call("HGET", dcsInfoKey, "dcs_mode")
    r["dcs_moid"] = redis.call("HGET", dcsInfoKey, "dcs_moid")
    r["mode_start_time"] = redis.call("HGET", dcsInfoKey, "mode_start_time")
    r["mode_end_time"] = endTime
    return r
end

local confE164 = ARGV[1]
local time = ARGV[2]
local result = {}

if redis.call("EXISTS", "meeting:" .. confE164 .. ":dcs_info") == 1 then
    result["terminals"] = {}

    local mtE164List = redis.call("SMEMBERS", "meeting:" .. confE164 .. ":dcs_terminals")
    for i, e164 in pairs(mtE164List) do
        local info = getDcsTerminalInfo(confE164, e164)
        info["end_time"] = time
        delDcsTerminalInfo(confE164, e164)
        table.insert(result["terminals"], info)
    end

    result["dcs_info"] = getDcsInfo(confE164)
    result["dcs_info"]["end_time"] = time
    delDcsMeeting(confE164)

    result["mode_recode"] = getDcsModeInfo(confE164, time)
end

return string.gsub(cjson.encode(result), "{}", "[]")
