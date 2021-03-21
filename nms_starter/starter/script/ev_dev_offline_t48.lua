-- 48终端上线消息处理
-- 参数: ip dev_type collectorid

local ip = ARGV[1]
local collectorid = ARGV[2]

local moid = redis.call("HGET", "terminal:ip2moid", ip)
if moid then
    local collectorOnlineKey = "collector:" .. collectorid .. ":online"
    local result = {
        ["moid"] = moid,
        ["domain_moid"] = redis.call("HGET", "terminal:" .. moid .. ":baseinfo", "user_domain")
    }
    redis.call("HREM", collectorOnlineKey, moid)

    -- 阈值告警判定
    local limit = redis.call("HGET", "warning:limit:global", "s_nms")
    local server_count = redis.call("HLEN", collectorOnlineKey)
    local collectorInfoKey = "collector:" .. collectorid .. ":Finfo"
    result["warning_trigger_flag"] = tonumber(server_count) >= tonumber(limit)
    result["collector_p_server_moid"] = redis.call("HGET", collectorInfoKey, "p_server_moid")
    result["current_value"] = server_count
    result["threshold_value"] = limit

    return string.gsub(cjson.encode(result), "{}", "[]")
end
