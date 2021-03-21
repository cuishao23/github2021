-- 传统会议资源
-- 参数 moid kwargs

local moid = ARGV[1]
local kwargs = cjson.decode(ARGV[2])

local lServerInfoKey = "l_server:" .. moid .. ":info"
local machineRoomMoid = redis.call("HGET", lServerInfoKey, "machine_room_moid")
redis.call("SADD", "mps_machine_rooms", machineRoomMoid)

redis.call("SADD", "machine_room:" .. machineRoomMoid .. ":mps", moid)

local mpsAbilityKey = "mps:" .. moid .. ":ability"
redis.call(
    "HMSET",
    mpsAbilityKey,
    "total_vmp",
    kwargs["total_vmp"],
    "used_vmp",
    kwargs["used_vmp"],
    "used_h264",
    kwargs["used_h264"],
    "total_h264",
    kwargs["total_h264"],
    "used_h265",
    kwargs["used_h265"],
    "total_h265",
    kwargs["total_h265"],
    "total_mixer",
    kwargs["total_mixer"],
    "used_mixer",
    kwargs["used_mixer"]
)

local mpsMeetingKey = "mps:" .. moid .. ":meeting"
local E164List = redis.call("SMEMBERS", mpsMeetingKey)

-- 清除当前 mps 相关的会议信息
for i = 1, #E164List do
    -- 会议对应的所有mps
    local meetingMpsKey = "meeting:" .. E164List[i] .. ":mps"
    local MpsMoidList = redis.call("SMEMBERS", meetingMpsKey)
    for j = 1, table.getn(MpsMoidList) do
        -- meeting:1118924:mps:ac516b50-82f2-433f-9939-0f200744aec6:ability
        local MeetingMpsAbility = "meeting:" .. E164List[i] .. ":mps:" .. MpsMoidList[j] .. ":ability"
        redis.call("DEL", MeetingMpsAbility)
    end
    redis.call("SREM", meetingMpsKey, moid)
end
redis.call("DEL", mpsMeetingKey)

-- 获取smu moid
local cardMoid = redis.call("HGET", lServerInfoKey, "p_server_moid")
local smuMoid = redis.call("HGET", "p_server:" .. cardMoid .. ":info", "smu")

if not smuMoid then
    smuMoid = cardMoid
end
-- 更新 mps 相关会议信息
for k, v in pairs(kwargs["conf_info"]) do
    local e164 = v["conf_e164"]

    -- mps:xx:metting
    redis.call("SADD", mpsMeetingKey, e164)

    -- meeting:xx:mps
    redis.call("SADD", "meeting:" .. e164 .. ":mps", moid)

    -- ability
    local meetingMpsAbilityKey = "meeting:" .. e164 .. ":mps:" .. moid .. ":ability"
    redis.call(
        "HMSET",
        meetingMpsAbilityKey,
        "vmp_count",
        v["used_vmp"],
        "mixer_count",
        v["used_mixer"],
        "abas_count",
        v["used_abas"],
        "vbas_count",
        v["used_vbas"],
        "device_type",
        kwargs["dev_type"],
        "device_ip",
        kwargs["dev_ip"]
    )

    -- smu
    redis.call("set", "meeting:" .. e164 .. ":smu", smuMoid)
end

-- 阈值信息
local result = {}
local limit = redis.call("HGET", "warning:limit:global", "s_media_resource")
result["threshold_value"] = limit

return string.gsub(cjson.encode(result), "{}", "[]")
