-- 删除老终端
-- 参数: moid
local moid = ARGV[1]
local terminalBaseinfoKey = "terminal:" .. moid .. ":baseinfo"
local ip = redis.call("HGET", terminalBaseinfoKey, "ip")
redis.call("DEL", terminalBaseinfoKey)
redis.call("HDEL", "terminal:ip2moid", ip)
