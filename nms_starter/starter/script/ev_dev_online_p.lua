-- 物理服务器设备上线
-- 参数: moid type collectorid
local moid = ARGV[1]
local type = ARGV[2]
local collectorid = ARGV[3]

local pServerInfoKey = "p_server:" .. moid .. ":info"
local pServerOnlineKey = "p_server:" .. moid .. ":online"
local collectorOnlineKey = "collector:" .. collectorid .. ":online"
redis.call("HSET", pServerInfoKey, "collectorid", collectorid)
redis.call("SET", pServerOnlineKey, "online")
redis.call("HSET", collectorOnlineKey, moid, type)

-- 阈值告警判定
local result = {}
local limit = redis.call("HGET", "warning:limit:global", "s_nms")
local p_server_count = redis.call("HLEN", collectorOnlineKey)
local collectorInfoKey = "collector:" .. collectorid .. ":info"
result["warning_trigger_flag"] = tonumber(p_server_count) >= tonumber(limit)
result["collector_p_server_moid"] = redis.call("HGET", collectorInfoKey, "p_server_moid")
result["current_value"] = p_server_count
result["threshold_value"] = limit

return string.gsub(cjson.encode(result), "{}", "[]")
