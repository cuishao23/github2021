-- 添加机房(散列类型数据)
-- 添加机房的时候,除了添加机房的详细信息,同时需要把机房moid添加到上级平台域的子项下面
-- 参数: moid name domain_moid
local moid = ARGV[1]
local name = ARGV[2]
local domain_moid = ARGV[3]

-- domain
local domainMachineRoomKey = "domain:" .. domain_moid .. ":machine_room"
redis.call("SADD", domainMachineRoomKey, moid)

-- machine_room
local machineRoomInfoKey = "machine_room:" .. moid .. ":info"
redis.call("HMSET", machineRoomInfoKey, "moid", moid, "name", name, "domain_moid", domain_moid)

-- machine_room_moids
redis.call("SADD", "machine_room_moids", moid)
