-- 添加域信息
-- 所有: 需要将moid信息添加到父级域
-- 用户域: 需要将moid添加到绑定机房
-- 参数: moid parent_moid name type [machine_room_moid]
local moid = ARGV[1]
local parent_moid = ARGV[2]
local name = ARGV[3]
local type = ARGV[4]

-- info
local domainInfoKey = "domain:" .. moid .. ":info"
redis.call("HMSET", domainInfoKey, "moid", moid, "parent_moid", parent_moid, "name", name, "type", type)

-- parent
local parentDomainSubKey = "domain:" .. parent_moid .. ":sub"
redis.call("SADD", parentDomainSubKey, moid)

-- machine_room
if type == "user" then
    local machine_room_moid = ARGV[5]
    if machine_room_moid and machine_room_moid ~= "" then
        local machineRoomDomainKey = "machine_room:" .. machine_room_moid .. ":domain"
        redis.call("SADD", machineRoomDomainKey, moid)
        redis.call("HSET", domainInfoKey, "machine_room_moid", machine_room_moid)
    end
end

-- domain_moids
redis.call("SADD", "domain_moids", moid)
