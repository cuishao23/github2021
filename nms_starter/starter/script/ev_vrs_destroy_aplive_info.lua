local confE164 = ARGV[1]

local apLiveInfoKey = "aplive:" .. confE164 .. ":info"
if redis.call("EXISTS", apLiveInfoKey) == 1 then
    local UserDomainMoid = redis.call("HGET", apLiveInfoKey, "domain_moid") or ""
    local DomainApLiveKey = "domain:" .. UserDomainMoid .. ":aplive"
    redis.call("SREM", DomainApLiveKey, confE164)
    redis.call("DEL", apLiveInfoKey)
end
