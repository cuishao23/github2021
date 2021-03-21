-- ejabberd 服务器下线
-- 参数: moid collectorid

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

local moid = ARGV[1]
local collectorid = ARGV[2]

local lServerInfoKey = "l_server:" .. moid .. ":info"

--比对collectorid是否相等，不相等就不删除
if redis.call("HGET", lServerInfoKey, "collectorid") == collectorid then
    local machineRoomMoid = redis.call("HGET", lServerInfoKey, "machine_room_moid") or ''
    if machineRoomMoid ~= '' then
        local ServiceDomainMoid = get_service_parent_domain_moid(machineRoomMoid)

        local KeyServer = "domain:" .. ServiceDomainMoid .. ":xmpp_server"
        redis.call("SREM", KeyServer, moid)

        local ResultKeyServer = redis.call("EXISTS", KeyServer)
        if ResultKeyServer == 0 then
            local KeyXnsOnline = "domain:" .. ServiceDomainMoid .. ":xmpp_online"
            redis.call("DEL", KeyXnsOnline)

            redis.call("SREM", "xns_service_domains", ServiceDomainMoid)
        end
    end
end
