-- 删除物理服务器
-- 参数: moid
local moid = ARGV[1]

local pServerInfoKey = "p_server:" .. moid .. ":info"

-- machine_room
local machineRoomMoid = redis.call("HGET", pServerInfoKey, "machine_room_moid") or ""
local machineRoomPServerKey = "machine_room:" .. machineRoomMoid .. ":p_server"
redis.call("SREM", machineRoomPServerKey, moid)

-- mac
local macId = redis.call("HGET", pServerInfoKey, "mac_id")
if macId then
    local mac = string.gsub(macId, "gfs-", "")
    local macMoidKey = "mac:" .. mac .. ":moid"
    redis.call("DEL", macMoidKey)
end

-- p_server
redis.call("DEL", pServerInfoKey)
redis.call("DEL", "p_server:" .. moid .. ":l_server")
redis.call("DEL", "p_server:" .. moid .. ":online")
redis.call("DEL", "p_server:" .. moid .. ":packet_loss_rate")
redis.call("DEL", "p_server:" .. moid .. ":resource")
