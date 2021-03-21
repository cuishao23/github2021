-- 网卡状态消息处理
-- 参数: moid portin portout recvpktloserate count netcard1_name netcard1_recvkbps netcard1_sendkbps netcard1_recvpktloserate ...
local moid = ARGV[1]
local portin = ARGV[2]
local portout = ARGV[3]
local recvpktloserate = ARGV[4]
local count = tonumber(ARGV[5])

local pServerResourceKey = "p_server:" .. moid .. ":resource"
redis.call(
    "HMSET",
    pServerResourceKey,
    "portin",
    portin,
    "portout",
    portout,
    "recvpktloserate",
    recvpktloserate,
    "netcard_count",
    count
)

local result = {}
local warningLimitKey = "warning:limit:" .. moid
result["threshold_value"] = redis.call("HGET", warningLimitKey, "port") or 60
-- 服务器收发流量限制: 单位 Mbps
result["threshold_value"] = result["threshold_value"] * 1024
result["current_value"] = 0

for i = 1, count do
    local nameKey = "netcard" .. i .. "_name"
    local recvKey = "netcard" .. i .. "_recvkbps"
    local sendKey = "netcard" .. i .. "_sendkbps"
    local loserateKey = "netcard" .. i .. "_recvpktloserate"
    redis.call(
        "HMSET",
        pServerResourceKey,
        nameKey,
        ARGV[4 * (i - 1) + 6],
        recvKey,
        ARGV[4 * (i - 1) + 7],
        sendKey,
        ARGV[4 * (i - 1) + 8],
        loserateKey,
        ARGV[4 * (i - 1) + 9]
    )
    result["current_value"] = math.max(result["current_value"], ARGV[4 * (i - 1) + 7], ARGV[4 * (i - 1) + 8])
end

-- 网卡速率告警
result["warning"] = tonumber(result["current_value"]) >= tonumber(result["threshold_value"])
result["machine_room_moid"] = redis.call("HGET", "p_server:" .. moid .. ":info", "machine_room_moid")
return string.gsub(cjson.encode(result), "{}", "[]")
