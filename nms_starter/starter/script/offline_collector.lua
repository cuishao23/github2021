-- 下线collector
-- 参数 collectorID
local collectorID = ARGV[1]

local collectorOnlineKey = "collector:" .. collectorID .. ":online"

redis.call("DEL", collectorOnlineKey)
redis.call("SREM", "collector", collectorID)
