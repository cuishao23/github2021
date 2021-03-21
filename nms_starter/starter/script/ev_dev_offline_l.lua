-- 逻辑服务器离线
-- 参数: moid, collectorid

local moid = ARGV[1]
local collectorid = ARGV[2]

local lServerInfoKey = "l_server:" .. moid .. ":info"
local collectorOnlineKey = "collector:" .. collectorid .. ":online"

if redis.call("HGET", lServerInfoKey, "collectorid") == collectorid then
    -- del l_server:moid:online
    local KeyOnline = "l_server:" .. moid .. ":online"
    redis.call("DEL", KeyOnline)

    -- del l_server:moid:connection
    local KeyConnection = "l_server:" .. moid .. ":connection"
    redis.call("DEL", KeyConnection)

    -- del l_server:moid:warning
    local KeyWarning = "l_server:" .. moid .. ":warning"
    redis.call("DEL", KeyWarning)
end

redis.call("HDEL", lServerInfoKey, "p_server_ip")
redis.call("HDEL", collectorOnlineKey, moid)

-- 阈值告警判定
local result = {}
local limit = redis.call("HGET", "warning:limit:global", "s_nms")
local p_server_count = redis.call("HLEN", collectorOnlineKey)
local collectorInfoKey = "collector:" .. collectorid .. ":info"
result["warning_trigger_flag"] = tonumber(p_server_count) >= tonumber(limit)
result["collector_p_server_moid"] = redis.call("HGET", collectorInfoKey, "p_server_moid")
result["current_value"] = tonumber(p_server_count)
result["threshold_value"] = tonumber(limit)

return string.gsub(cjson.encode(result), "{}", "[]")
