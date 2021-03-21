-- 更新终端信息
-- moid domain_moid name [e164]
local moid = ARGV[1]
local domainMoid = ARGV[2]
local name = ARGV[3]
local e164 = ARGV[4]
local terminalBaseinfoKey = "terminal:" .. moid .. ":baseinfo"

if e164 and e164 ~= "" then
    local terminalE164BaseinfoKey = "terminal:" .. e164 .. ":baseinfo"
    redis.call("HMSET", terminalE164BaseinfoKey, "moid", moid, "domain_moid", domainMoid, "name", name, "e164", e164)
else
    e164 = ""
end
redis.call("HMSET", terminalBaseinfoKey, "moid", moid, "domain_moid", domainMoid, "name", name, "e164", e164)
