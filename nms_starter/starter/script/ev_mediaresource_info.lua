-- 端口会议资源
-- 参数: moid kwargs

local moid = ARGV[1]
local kwargs = cjson.decode(ARGV[2])

local lServerInfoKey = "l_server:" .. moid .. ":info"
local machineRoomMoid = redis.call("HGET", lServerInfoKey, "machine_room_moid")
redis.call("SADD", "mediaresource_machine_rooms", machineRoomMoid)

local machineRoomMediaresourceKey = "machine_room:" .. machineRoomMoid .. ":mediaresource"
redis.call("SADD", machineRoomMediaresourceKey, moid)

local mediaresourceAbilityKey = "mediaresource:" .. moid .. ":ability"
redis.call(
    "HMSET",
    mediaresourceAbilityKey,
    "total_port",
    kwargs["total_port"],
    "used_port",
    kwargs["used_port"],
    "h265_total_port",
    kwargs["h265_total_port"],
    "h265_used_port",
    kwargs["h265_used_port"],
    "total_vmp",
    kwargs["total_vmp"],
    "used_vmp",
    kwargs["used_vmp"],
    "total_mixer",
    kwargs["total_mixer"],
    "used_mixer",
    kwargs["used_mixer"]
)

local pServerMoid = redis.call("HGET", lServerInfoKey, "p_server_moid")
local smuMoid = redis.call("HGET", "p_server:" .. pServerMoid .. ":info", "smu")

-- mps
if not smuMoid then
    smuMoid = pServerMoid
end

for i, confE164 in ipairs(kwargs["conf_info"]) do
    redis.call("set", "meeting:" .. confE164["conf_e164"] .. ":smu", smuMoid)
end

-- 阈值信息
local result = {}
local limit = redis.call("HGET", "warning:limit:global", "s_media_resource")
result["threshold_value"] = tonumber(limit)

return string.gsub(cjson.encode(result), "{}", "[]")
