-- 终端上线统计
-- 返回json

local result = {}
local domainList = redis.call("SMEMBERS", "domain_moids")
for i, domainMoid in pairs(domainList) do
    if redis.call("EXISTS", "domain:" .. domainMoid .. ":info") ~= 0 then
        local info = {}
        info["total"] = redis.call("SCARD", "domain:" .. domainMoid .. ":terminal_e164")
        info["online"] = 0
        for i, moid in pairs(redis.call("SMEMBERS", "domain:" .. domainMoid .. ":terminal")) do
            if redis.call("EXISTS", "terminal:" .. moid .. ":onlinestate") ~= 0 then
                info["online"] = info["online"] + 1
            end
        end
        result[domainMoid] = info
    end
end
return string.gsub(cjson.encode(result), "{}", "[]")
