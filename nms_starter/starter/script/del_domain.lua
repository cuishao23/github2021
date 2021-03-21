-- 删除一个域(散列类型数据)
-- 要删除的域下面,如果还有子域/设备,则不允许删除
-- 参数: moid
local moid = ARGV[1]
local domainTerminalKey = "domain:" .. moid .. ":terminal"
local domainSubKey = "domain:" .. moid .. ":sub"
local terminalNum = redis.call("SCARD", domainTerminalKey)
local subDomainNum = redis.call("SCARD", domainSubKey)
if terminalNum + subDomainNum == 0 then
    local domainInfoKey = "domain:" .. moid .. ":info"

    -- machine_room
    local machineRoomMoid = redis.call("HGET", domainInfoKey, "machine_room_moid")
    if machineRoomMoid then
        local machineRoomDomainKey = "machine_room:" .. machineRoomMoid .. ":domain"
        redis.call("SREM", machineRoomDomainKey, moid)
    end

    -- parent
    local parentDomainSubKey = "domain:" .. redis.call("HGET", domainInfoKey, "parent_moid") .. ":sub"
    redis.call("SREM", parentDomainSubKey, moid)

    -- info
    redis.call("DEL", domainInfoKey)

    -- domain_moids
    redis.call("SREM", "domain_moids", moid)
end
