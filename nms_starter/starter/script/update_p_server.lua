-- 修改物理服务器信息
-- 参数: moid name type machine_room_moid location [ip] [mac_id]
-- location: 机房名称
local moid = ARGV[1]
local name = ARGV[2]
local type = ARGV[3]
local machine_room_moid = ARGV[4]
local location = ARGV[5]
local ip = ARGV[6]
local mac_id = ARGV[7]

-- p_server
local pServerInfoKey = "p_server:" .. moid .. ":info"
redis.call(
    "HMSET",
    pServerInfoKey,
    "name",
    name,
    "type",
    type,
    "machine_room_moid",
    machine_room_moid,
    "location",
    location
)

if ip then
    redis.call("HSET", pServerInfoKey, "ip", ip)
end

-- 暂时考虑mac地址存在变更可能
local oldMacId = redis.call("HGET", pServerInfoKey, "mac_id")
if oldMacId and oldMacId ~= mac_id then
    redis.call("HSET", pServerInfoKey, "mac_id", mac_id)

    local oldMacMoidKey = "mac:" .. string.gsub(oldMacId, "gfs-", "") .. ":moid"
    local macMoidKey = "mac:" .. string.gsub(mac_id, "gfs-", "") .. ":moid"
    redis.call("DEL", oldMacMoidKey)
    redis.call("SET", macMoidKey, moid)
end
