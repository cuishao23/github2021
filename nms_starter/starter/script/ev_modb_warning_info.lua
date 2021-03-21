-- modb告警
-- 参数: moid

local moid = ARGV[1]

local machineRoomMoid = redis.call("HGET", "l_server:" .. moid .. ":info", "machine_room_moid")
return redis.call("HGET", "machine_room:" .. machineRoomMoid .. ":info", "domain_moid") or ""
