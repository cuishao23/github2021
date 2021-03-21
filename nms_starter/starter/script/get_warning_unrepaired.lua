-- 获取为修复告警信息
-- 参数: type moid code
local key = ARGV[1] .. ":" .. ARGV[2] .. ":" .. "warning"
return redis.call("HGET", key, ARGV[3])
