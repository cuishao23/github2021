-- 删除一个机房
-- 如果还有l_server, p_server 不允许删除
-- 参数: moid
local moid = ARGV[1]

local machineRoomLServerKey = "machine_room:" .. moid .. ":l_server"
local machineRoomPServerKey = "machine_room:" .. moid .. ":p_server"
local lServerCount = redis.call("SCARD", machineRoomLServerKey)
local lServerCount = redis.call("SCARD", machineRoomPServerKey)

if lServerCount + lServerCount == 0 then
    local machineRoomInfoKey = "machine_room:" .. moid .. ":info"
    local domainMoid = redis.call("HGET", machineRoomInfoKey, "domain_moid")
    local domainMachineRoomKey = "domain:" .. domainMoid .. ":machine_room"
    redis.call("SREM", domainMachineRoomKey, moid)
    redis.call("DEL", machineRoomInfoKey)
    redis.call("SREM", "machine_room_moids", moid)
end
