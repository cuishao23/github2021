-- 添加老终端
-- 参数: moid, domain_moid, name, e164, ip

local moid = ARGV[1]
local domain_moid = ARGV[2]
local name = ARGV[3]
local e164 = ARGV[4]
local ip = ARGV[5]
local terminalBaseinfoKey = "terminal:" .. moid .. ":baseinfo"
redis.call("HSET", "terminal:ip2moid", ip, moid)
redis.call("HMSET", terminalBaseinfoKey, "moid", moid, "domain_moid", domain_moid, "name", name, "e164", e164, "ip", ip)
