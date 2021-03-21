-- 逻辑服务器删除
-- 参数: moid
local moid = ARGV[1]
local lServerInfoKey = "l_server:" .. moid .. ":info"

-- machine_room
local machineRoomMoid = redis.call("HGET", lServerInfoKey, "machine_room_moid") or ""
local machineRoomLServerKey = "machine_room:" .. machineRoomMoid .. ":l_server"
redis.call("SREM", machineRoomLServerKey, moid)

-- p_server
local pServerMoid = redis.call("HGET", lServerInfoKey, "p_server") or ""
local pServerLServerKey = "p_server:" .. pServerMoid .. ":l_server"
redis.call("SREM", pServerLServerKey, moid)

-- l_server
redis.call("DEL", lServerInfoKey)
