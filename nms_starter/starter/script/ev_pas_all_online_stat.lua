-- 用户域在线终端数统计(统计用)
-- 参数: pasMoid info

local pasMoid = ARGV[1]
local info = cjson.decode(ARGV[2])

-- 接入上报，在用户域无注册终端的情况下，不会上报为0 的数字，需自行清除上次上报结果
-- domain:moid:pas_sip用户域下sip终端统计
-- domain:moid:pas_h323用户域下h323终端统计
local domainList = redis.call("SMEMBERS", "domain_moids")
for i, domainMoid in pairs(domainList) do
    redis.call("DEL", "domain:" .. domainMoid .. ":pas_sip")
    redis.call("DEL", "domain:" .. domainMoid .. ":pas_h323")
    redis.call("DEL", "domain:" .. domainMoid .. ":pas_rtc")
end
for i, v in pairs(info) do
    local domainMoid = v["domain_moid"]
    if domainMoid and domainMoid ~= "" then
        local sip_count = v["sip_count"] or 0
        local h323_count = v["h323_count"] or 0
        local rtc_count = v["rtc_count"] or 0
        redis.call("HSET", "domain:" .. domainMoid .. ":pas_sip", pasMoid, sip_count)
        redis.call("HSET", "domain:" .. domainMoid .. ":pas_h323", pasMoid, h323_count)
        redis.call("HSET", "domain:" .. domainMoid .. ":pas_rtc", pasMoid, rtc_count)
    end
end
