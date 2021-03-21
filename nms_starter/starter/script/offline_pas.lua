-- pas下线
-- 参数: moid collectorid

local function del_p2p_meeting(CallerE164)
    local KeyInfo = "p2p_meeting:" .. CallerE164 .. ":info"
    local CallerDomainMoid = redis.call("HGET", KeyInfo, "caller_domain_moid")
    local CalleeDomainMoid = redis.call("HGET", KeyInfo, "callee_domain_moid")

    if CallerDomainMoid ~= nil and CalleeDomainMoid ~= nil then
        local KeyCallerMeeting = "domain:" .. CallerDomainMoid .. ":p2p_meeting"
        local KeyCalleeMeeting = "domain:" .. CalleeDomainMoid .. ":p2p_meeting"

        redis.call("SREM", KeyCallerMeeting, CallerE164)
        redis.call("SREM", KeyCalleeMeeting, CallerE164)
        redis.call("DEL", KeyInfo)
    end
end

local moid = ARGV[1]
local collectorid = ARGV[2]

local lServerInfoKey = "l_server:" .. moid .. ":info"

-- collectorid 相同, 做下线处理
if redis.call("HGET", lServerInfoKey, "collectorid") == collectorid then
    -- del pas:moid:online
    local KeyPasStatistic = "pas:" .. moid .. ":online"
    redis.call("DEL", KeyPasStatistic)

    -- del pas:moid:domain:d_moid:online
    local PasKeys = redis.call("KEYS", "pas:" .. moid .. ":domain:*:online")
    for i = 1, #PasKeys do
        redis.call("DEL", PasKeys[i])
    end

    -- 清除机房下的pas信息
    local MachineRoomMoid = redis.call("HGET", lServerInfoKey, "machine_room_moid") or ""
    if MachineRoomMoid ~= "" then
        local KeyPasServer = "machine_room:" .. MachineRoomMoid .. ":pas_server"
        redis.call("SREM", KeyPasServer, moid)
    end

    -- del p2p conf info
    local KeyPasMeeting = "pas:" .. moid .. ":p2p_meeting"
    local P2PMeetingList = redis.call("SMEMBERS", KeyPasMeeting)
    redis.call("DEL", KeyPasMeeting)

    for i, CallerE164 in ipairs(P2PMeetingList) do
        del_p2p_meeting(CallerE164)
    end
end
