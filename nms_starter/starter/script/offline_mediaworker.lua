-- media-worker 下线
-- 参数: moid collectorid

local moid = ARGV[1]
local collectorid = ARGV[2]

local lServerInfoKey = "l_server:" .. moid .. ":info"

--比对collectorid是否相等，不相等就不删除
if redis.call("HGET", lServerInfoKey, "collectorid") == collectorid then
    local MachineRoomMoid = redis.call("HGET", lServerInfoKey, "machine_room_moid")
    local KeyMediaServer = "machine_room:" .. MachineRoomMoid .. ":mediaresource"
    redis.call("SREM", KeyMediaServer, moid)

    local KeyMediaAbility = "mediaresource:" .. moid .. ":ability"
    redis.call("DEL", KeyMediaAbility)

    local ResultKeyMediaServer = redis.call("EXISTS", KeyMediaServer)
    if ResultKeyMediaServer == 0 then
        redis.call("SREM", "mediaresource_platform_domains", MachineRoomMoid)
    end
end
