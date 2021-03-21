-- 参数: moid, ip
local moid = ARGV[1]
local ip = ARGV[2]
local KeyMoidInfo = "p_server:" .. moid .. ":info"
redis.call("HSET", KeyMoidInfo, "ip", ip)
