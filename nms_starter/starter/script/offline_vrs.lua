-- vrs下线
-- 参数: moid collectorid

local moid = ARGV[1]
local collectorid = ARGV[2]

local lServerInfoKey = "l_server:" .. moid .. ":info"

--比对collectorid是否相等，不相等就不删除
if redis.call("HGET", lServerInfoKey, "collectorid") == collectorid then
    local MachineRoomMoid = redis.call("HGET", lServerInfoKey, "machine_room_moid") or ""

    local KeyVrsServer = "machine_room:" .. MachineRoomMoid .. ":vrs"
    redis.call("SREM", KeyVrsServer, moid)

    local KeyMediaAbility = "vrs:" .. moid .. ":ability"
    redis.call("DEL", KeyMediaAbility)

    local KeyVrsLive = "vrs:" .. moid .. ":live"
    for i, v in ipairs(redis.call("SMEMBERS", KeyVrsLive)) do
        redis.call("DEL", v)
    end
    redis.call("DEL", KeyVrsLive)

    local ResultKeyVrsServer = redis.call("EXISTS", KeyVrsServer)
    if ResultKeyVrsServer == 0 then
        redis.call("SREM", "vrs_machine_rooms", MachineRoomMoid)
    end
end
