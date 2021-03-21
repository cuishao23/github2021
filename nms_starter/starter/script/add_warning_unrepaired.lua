-- 添加告警信息
-- 参数: type moid, code, level
local key = ARGV[1] .. ":" .. ARGV[2] .. ":warning"
local code = ARGV[3]
local warningLevel = ARGV[4]
redis.call("HSET", key, code, warningLevel)
