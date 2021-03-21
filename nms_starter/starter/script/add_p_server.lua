-- 添加物理服务器信息
-- 1.机房下增加服务器moid, 2.增加物理服务器信息
-- 参数: moid name type machine_room_moid location ip mac_id
-- location: 机房名称
local moid = ARGV[1]
local name = ARGV[2]
local type = ARGV[3]
local machine_room_moid = ARGV[4]
local location = ARGV[5]
local ip = ARGV[6]
local mac_id = ARGV[7]

-- machine_room
local machineRoomPServerKey = "machine_room:" .. machine_room_moid .. ":p_server"
redis.call("SADD", machineRoomPServerKey, moid)

-- p_server
local pServerInfoKey = "p_server:" .. moid .. ":info"
redis.call(
    "HMSET",
    pServerInfoKey,
    "moid",
    moid,
    "name",
    name,
    "type",
    type,
    "machine_room_moid",
    machine_room_moid,
    "location",
    location
)

if ip and ip ~= "" then
    redis.call("HSET", pServerInfoKey, "ip", ip)
end
if mac_id and mac_id ~= "" then
    redis.call("HSET", pServerInfoKey, "mac_id", mac_id)

    -- mac
    local mac = string.gsub(mac_id, "gfs-", "")
    local macMoidKey = "mac:" .. mac .. ":moid"
    redis.call("SET", macMoidKey, moid)
end

redis.call("SADD", "p_server:type", type)
