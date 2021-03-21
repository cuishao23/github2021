-- 修改机房(散列类型数据)
-- 参数: moid name
local moid = ARGV[1]
local name = ARGV[2]
local domain_moid = ARGV[3]

-- machine_room
local machineRoomInfoKey = "machine_room:" .. moid .. ":info"
redis.call("HMSET", machineRoomInfoKey, "moid", moid, "name", name, "domain_moid", domain_moid)
