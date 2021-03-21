-- 逻辑服务器上线
-- 参数: moid type collectorid

local moid = ARGV[1]
local serverType = ARGV[2]
local collectorid = ARGV[3]

local lServerOnlineKey = "l_server:" .. moid .. ":online"
local collectorOnlineKey = "collector:" .. collectorid .. ":online"
local lServerInfoKey = "l_server:" .. moid .. ":info"

-- 上线信息
redis.call("SET", lServerOnlineKey, "online")
redis.call("HSET", collectorOnlineKey, moid, serverType)
redis.call("HSET", lServerInfoKey, "collectorid", collectorid)

-- 物理服务器ip信息
local pServerMoid = redis.call("HGET", lServerInfoKey, "p_server_moid")
local pServerInfoKey = "p_server:" .. pServerMoid .. ":info"
local pServerIP = redis.call("HGET", pServerInfoKey, "ip") or ""
redis.call("HSET", lServerInfoKey, "p_server_ip", pServerIP)

-- 阈值告警判定
local result = {}
local limit = redis.call("HGET", "warning:limit:global", "s_nms")
local server_count = redis.call("HLEN", collectorOnlineKey)
local collectorInfoKey = "collector:" .. collectorid .. ":info"
result["warning_trigger_flag"] = tonumber(server_count) >= tonumber(limit)
result["collector_p_server_moid"] = redis.call("HGET", collectorInfoKey, "p_server_moid")
result["current_value"] = server_count
result["threshold_value"] = limit

return string.gsub(cjson.encode(result), "{}", "[]")
