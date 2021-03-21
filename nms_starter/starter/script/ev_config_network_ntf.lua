-- 终端网络配置结果通知
-- 参数: moid devType result

local moid = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, ' ', '~')
local result = ARGV[3]

local termicalNetworkResultKey = "termical:" .. moid .. ":" .. devKeyType .. ":network_result"
redis.call("HSET", termicalNetworkResultKey, "result", result)
