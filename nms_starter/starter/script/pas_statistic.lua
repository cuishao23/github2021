-- pas在线终端统计

local result = {}

local function getPasTerminalCount(domainMoid)
    local sip = 0
    local h323 = 0
    local rtc = 0
    for i, info in pairs(redis.call("HVALS", "domain:" .. domainMoid .. ":pas_sip")) do
        sip = sip + tonumber(info)
    end
    for i, info in pairs(redis.call("HVALS", "domain:" .. domainMoid .. ":pas_h323")) do
        h323 = h323 + tonumber(info)
    end
    for i, info in pairs(redis.call("HVALS", "domain:" .. domainMoid .. ":pas_rtc")) do
        rtc = rtc + tonumber(info)
    end
    return sip, h323, rtc
end

local domainList = redis.call("SMEMBERS", "domain_moids")
for i, domainMoid in pairs(domainList) do
    local sip, h323, rtc
    sip, h323, rtc = getPasTerminalCount(domainMoid)
    result[domainMoid] = {
        ["sip"] = sip,
        ["h323"] = h323,
        ["rtc"] = rtc
    }
end

return string.gsub(cjson.encode(result), "{}", "[]")
