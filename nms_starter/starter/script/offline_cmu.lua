-- cmu下线处理
-- 参数: moid collectorid

local moid = ARGV[1]
local collectorid = ARGV[2]
local lServerInfoKey = "l_server:" .. moid .. ":info"

--比对collectorid是否相等，不相等就不删除
if redis.call("HGET", lServerInfoKey, "collectorid") == collectorid then
    local KeyTMeeting = "cms:" .. moid .. ":t_meeting"
    local TMeetingList = redis.call("SMEMBERS", KeyTMeeting)
    redis.call("DEL", KeyTMeeting)

    for i, ConfE164 in ipairs(TMeetingList) do
        -- del meeting ip_e164
        redis.call("DEL", "meeting:" .. ConfE164 .. ":ip_e164")

        -- del meeting terminal
        local KeyMeetingTerminal = "meeting:" .. ConfE164 .. ":terminal"
        local TerminalList = redis.call("SMEMBERS", KeyMeetingTerminal)
        redis.call("DEL", KeyMeetingTerminal)

        -- del meeting info
        local KeyMeetingInfo = "t_meeting:" .. ConfE164 .. ":info"
        local DomainMoid = redis.call("HGET", KeyMeetingInfo, "domain_moid")
        redis.call("DEL", KeyMeetingInfo)

        if DomainMoid then
            local KeyMeeting = "domain:" .. DomainMoid .. ":t_meeting"
            redis.call("SREM", KeyMeeting, ConfE164)
        end
    end

    local KeyPMeeting = "cms:" .. moid .. ":p_meeting"
    local PMeetingList = redis.call("SMEMBERS", KeyPMeeting)
    redis.call("DEL", KeyPMeeting)

    for i, ConfE164 in ipairs(PMeetingList) do
        -- del meeting ip_e164
        redis.call("DEL", "meeting:" .. ConfE164 .. ":ip_e164")

        -- del meeting terminal
        local KeyMeetingTerminal = "meeting:" .. ConfE164 .. ":terminal"
        local TerminalList = redis.call("SMEMBERS", KeyMeetingTerminal)
        redis.call("DEL", KeyMeetingTerminal)

        -- del meeting info
        local KeyMeetingInfo = "p_meeting:" .. ConfE164 .. ":info"
        local DomainMoid = redis.call("HGET", KeyMeetingInfo, "domain_moid")
        redis.call("DEL", KeyMeetingInfo)

        if DomainMoid ~= nil then
            local KeyMeeting = "domain:" .. DomainMoid .. ":p_meeting"
            redis.call("SREM", KeyMeeting, ConfE164)
        end
    end
end
