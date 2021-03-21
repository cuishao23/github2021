-- xmpp在线数
-- 参数: moid online_number

local moid = ARGV[1]
local onlineNumber = ARGV[2]

local function get_service_parent_domain_moid(machineRoomMoid, domainMoid)
    if machineRoomMoid ~= "" then
        local KeyMachineRoomDetail = "machine_room:" .. machineRoomMoid .. ":info"
        domainMoid = redis.call("HGET", "machine_room:" .. machineRoomMoid .. ":info", "domain_moid") or ""
    end
    local domainType = redis.call("HGET", "domain:" .. domainMoid .. ":info", "type")
    if domainType == "service" or domainType == "kernel" then
        return domainMoid
    else
        local ParentDomainMoid = redis.call("HGET", "domain:" .. domainMoid .. ":info", "parent_moid")
        return get_service_parent_domain_moid("", ParentDomainMoid)
    end
end

local lServerInfoKey = "l_server:" .. moid .. ":info"
local machineRoomMoid = redis.call("HGET", lServerInfoKey, "machine_room_moid") or ""
if machineRoomMoid ~= "" then
    local serviceDomainMoid = get_service_parent_domain_moid(machineRoomMoid, "")

    local domainXmppServerKey = "domain:" .. serviceDomainMoid .. ":xmpp_server"
    redis.call("SADD", domainXmppServerKey, moid)

    local domainXmppOnlineKey = "domain:" .. serviceDomainMoid .. ":xmpp_online"
    redis.call("SET", domainXmppOnlineKey, onlineNumber)

    redis.call("SADD", "xns_service_domains", serviceDomainMoid)
end
