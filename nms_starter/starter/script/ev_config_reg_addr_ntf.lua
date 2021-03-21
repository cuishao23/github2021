-- 终端注册地址配置结果通知
-- 参数: moid devType result

local moid = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, ' ', '~')
local result = ARGV[3]

local termicalRegAddrResultKey = "termical:" ..moid .. ":" .. devKeyType .. ":reg_addr_result"
redis.call("HSET", termicalRegAddrResultKey, "result", result)
