-- 磁盘状态消息处理
-- 参数: moid diskInfo
local moid = ARGV[1]
local totalUserate = ARGV[2]
local diskInfo = cjson.decode(ARGV[3])

local result = {}
local pServerResourceKey = "p_server:" .. moid .. ":resource"
redis.call("HSET", pServerResourceKey, "disk_count", #diskInfo)
redis.call("HSET", pServerResourceKey, "disk_total_userate", totalUserate)
local maxUserate = 0
for i, info in pairs(diskInfo) do
    redis.call(
        "HMSET",
        pServerResourceKey,
        "disk" .. i .. "_name",
        info["diskname"],
        "disk" .. i .. "_total",
        info["totalsize"],
        "disk" .. i .. "_userate",
        info["userate"],
        "disk" .. i .. "_used",
        info["usesize"]
    )
    redis.call("ZADD", "disk_userate", info["userate"], moid .. ":" .. info["diskname"])
    maxUserate = math.max(maxUserate, info["userate"])
end

-- 阈值判定
local warningLimitKey = "warning:limit:" .. moid
result["threshold_value"] = tonumber(redis.call("HGET", warningLimitKey, "disk") or 80)
result["waring"] = tonumber(maxUserate) >= tonumber(result["threshold_value"])
result["current_value"] = maxUserate
return string.gsub(cjson.encode(result), "{}", "[]")
