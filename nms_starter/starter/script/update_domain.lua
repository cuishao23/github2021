-- 更新域信息
-- 需要将moid信息添加到父级域
-- 用户域: 需要将moid添加到绑定机房
-- 参数: moid parent_moid name type [machine_room_moid]
local moid = ARGV[1]
local parent_moid = ARGV[2]
local name = ARGV[3]
local type = ARGV[4]

-- parent
local domainInfoKey = "domain:" .. moid .. ":info"
local oldParentMoid = redis.call("HGET", domainInfoKey, "parent_moid")
if oldParentMoid ~= parent_moid then
    local oldParentDomainSubKey = "domain:" .. oldParentMoid .. ":sub"
    local parentDomainSubKey = "domain:" .. parent_moid .. ":sub"
    redis.call("SREM", oldParentDomainSubKey, moid)
    redis.call("SADD", parentDomainSubKey, moid)
end

-- machine_room
if type == "user" then
    local oldMachineRoomMoid = redis.call("HGET", domainInfoKey, "machine_room_moid")
    local machine_room_moid = ARGV[5]
    if machine_room_moid ~= oldMachineRoomMoid then
        local oldMachineRoomDomainKey = "machine_room:" .. oldMachineRoomMoid .. ":domain"
        local machineRoomDomainKey = "machine_room:" .. machine_room_moid .. ":domain"
        redis.call("SREM", oldMachineRoomDomainKey, moid)
        redis.call("SADD", machineRoomDomainKey, moid)
        redis.call("HSET", domainInfoKey, "machine_room_moid", machine_room_moid)
    end
end

-- info
redis.call("HMSET", domainInfoKey, "moid", moid, "parent_moid", parent_moid, "name", name, "type", type)
