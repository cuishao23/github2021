-- 会议统计
-- 返回格式: json:{}

local result = {}
local domainList = redis.call("SMEMBERS", "domain_moids")
for i, domainMoid in pairs(domainList) do
    if redis.call("EXISTS", "domain:" .. domainMoid .. ":info") ~= 0 then
        result[domainMoid] = {}
        result[domainMoid]["a_meeting"] = redis.call("SCARD", "domain:" .. domainMoid .. ":a_meeting")
        result[domainMoid]["t_meeting"] = redis.call("SCARD", "domain:" .. domainMoid .. ":t_meeting")
        result[domainMoid]["p_meeting"] = redis.call("SCARD", "domain:" .. domainMoid .. ":p_meeting")
        result[domainMoid]["sfu_meeting"] = redis.call("SCARD", "domain:" .. domainMoid .. ":sfu_meeting")
        result[domainMoid]["mix_meeting"] = redis.call("SCARD", "domain:" .. domainMoid .. ":mix_meeting")
        result[domainMoid]["p2p_meeting"] = redis.call("SCARD", "domain:" .. domainMoid .. ":p2p_meeting")
    end
end
return string.gsub(cjson.encode(result), "{}", "[]")
