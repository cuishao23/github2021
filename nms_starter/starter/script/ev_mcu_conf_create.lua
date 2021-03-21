-- 多点会议创建
-- 参数: meetingType meetingMoid meetingInfo

-- 创建会议基本信息
local function createMeetingInfo(meetingType, confE164, meetingMoid, meetingInfo)
    local meetingInfoKey = meetingType .. ":" .. confE164 .. ":info"
    local domainMeetingKey = "domain:" .. meetingInfo["domain_moid"] .. ":" .. meetingType
    local cmsMeeting = "cms:" .. meetingInfo["cms"] .. ":" .. meetingType

    -- 删除老的记录
    if redis.call("EXISTS", meetingInfoKey) == 1 then
        local oldDomainMoid = redis.call("HGET", meetingInfoKey, "domain_moid") or ""
        redis.call("SREM", "domain:" .. oldDomainMoid .. ":" .. meetingType, confE164)

        local oldCmsMoid = redis.call("HGET", meetingInfoKey, "cms") or ""
        redis.call("SREM", "cms:" .. oldCmsMoid .. ":" .. meetingType, confE164)
    end

    -- 记录confE164号和moid对应关系
    redis.call("HSET", "meeting_moid_map", confE164, meetingMoid)
    redis.call("HSET", "meeting_type_map", confE164, meetingType)
    redis.call("SADD", domainMeetingKey, confE164)
    redis.call("HSET", meetingInfoKey, "meeting_moid", meetingMoid)

    -- cms记录, 离线时下线所有会议
    redis.call("SADD", cmsMeeting, confE164)

    for k, v in pairs(meetingInfo) do
        redis.call("HSET", meetingInfoKey, k, v)
    end
end

local meetingType = ARGV[1]
local meetingMoid = ARGV[2]
local meetingInfo = cjson.decode(ARGV[3])

local confE164 = meetingInfo["e164"]

createMeetingInfo(meetingType, confE164, meetingMoid, meetingInfo)
