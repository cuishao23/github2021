-- 终端上线消息处理
-- 参数: moid dev_type collectorid

local moidOrE164 = ARGV[1]
local devType = ARGV[2]
local collectorid = ARGV[3]
local terminalBaseifoKey = "terminal:" .. moidOrE164 .. ":baseinfo"

local moid = redis.call("HGET", terminalBaseifoKey, "moid")
local result = {}
if moid then
    local terminalOnlinestateKey = "terminal:" .. moid .. ":onlinestate"
    local terminalCollectorKey = "terminal:" .. moid .. ":collectorid"
    local collectorOnlineKey = "collector:" .. collectorid .. ":online"
    result = {
        ["moid"] = moid,
        ["domain_moid"] = redis.call("HGET", terminalBaseifoKey, "domain_moid")
    }
    redis.call("HSET", terminalOnlinestateKey, devType, "online")
    redis.call("HSET", terminalCollectorKey, devType, collectorid)
    redis.call("HSET", collectorOnlineKey, moid, devType)

    -- 阈值告警判定
    local limit = redis.call("HGET", "warning:limit:global", "s_nms")
    local server_count = redis.call("HLEN", collectorOnlineKey)
    local collectorInfoKey = "collector:" .. collectorid .. ":info"
    result["warning_trigger_flag"] = tonumber(server_count) >= tonumber(limit)
    result["collector_p_server_moid"] = redis.call("HGET", collectorInfoKey, "p_server_moid")
    result["current_value"] = server_count
    result["threshold_value"] = limit
end
return string.gsub(cjson.encode(result), "{}", "[]")
