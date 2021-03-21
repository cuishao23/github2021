-- 会议终端统计
-- 返回格式: json

local function getMeetingTerminalCount(confE164)
    local count = 0
    count = count + redis.call("SCARD", "meeting:" .. confE164 .. ":terminal")
    count = count + redis.call("SCARD", "meeting:" .. confE164 .. ":telphone")
    count = count + redis.call("SCARD", "meeting:" .. confE164 .. ":ipc")
    count = count + redis.call("SCARD", "meeting:" .. confE164 .. ":ip_e164")
    return count
end

local result = {}
local domainList = redis.call("SMEMBERS", "domain_moids")
for i, domainMoid in pairs(domainList) do
    local info = {
        ["p2p"] = 0,
        ["multiple"] = 0
    }
    local confE164List =
        redis.call(
        "SUNION",
        "domain:" .. domainMoid .. ":t_meeting",
        "domain:" .. domainMoid .. ":p_meeting",
        "domain:" .. domainMoid .. ":sfu_meeting",
        "domain:" .. domainMoid .. ":mix_meeting"
    )
    for i, confE164 in pairs(confE164List) do
        info["multiple"] = info["multiple"] + getMeetingTerminalCount(confE164)
    end
    info["multiple"] = redis.call("SCARD", "domain:" .. domainMoid .. ":p2p_meeting") * 2
    result[domainMoid] = info
end

return string.gsub(cjson.encode(result), "{}", "[]")
