-- dcs离线
-- 参数: moid collectorid

local moid = ARGV[1]
local collectorid = ARGV[2]

local lServerInfoKey = "l_server:" .. moid .. ":info"
local CollectorID = redis.call("HGET", lServerInfoKey, "collectorid")

--比对collectorid是否相等，不相等就不删除
if redis.call("HGET", lServerInfoKey, "collectorid") == collectorid then
    local DomainMoid = redis.call("HGET", lServerInfoKey, "machine_room_moid")
    local KeyDcsServer = "machine_room:" .. DomainMoid .. ":dcs"
    redis.call("SREM", KeyDcsServer, moid)

    local KeyDcsResource = "dcs:" .. moid .. ":resource"
    redis.call("DEL", KeyDcsResource)

-- local ResultKeyDcsServer = redis.call('EXISTS', KeyDcsServer)
-- if ResultKeyDcsServer == 0 then
--     redis.call('SREM','vrs_platform_domains',DomainMoid)
-- end
end
