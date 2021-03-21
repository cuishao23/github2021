-- 预约会议
-- 参数: confE164 operation startTime expiredTime userDomainMoid
-- domain:moid:a_meeting
-- a_meeting:confE164:info :预约会议详情

local function delApplintmentMeeting(confE164)
    local domainMoid = redis.call("HGET", "a_meeting:" .. confE164 .. ":info", "domain_moid")
    if domainMoid then
        redis.call("SREM", "domain:" .. domainMoid .. ":a_meeting", confE164)
    end
    redis.call("DEL", "a_meeting:" .. confE164 .. ":info")
end

local function addApplintmentMeeting(confE164, startTime, endTime, expiredTime, userDomainMoid, confInfo)
    redis.call("SADD", "domain:" .. userDomainMoid .. ":a_meeting", confE164)
    redis.call(
        "HMSET",
        "a_meeting:" .. confE164 .. ":info",
        "start_time",
        startTime,
        "end_time",
        endTime,
        "domain_moid",
        userDomainMoid,
        "info",
        confInfo
    )
    redis.call("EXPIRE", "a_meeting:" .. confE164 .. ":info", expiredTime)
end

local confE164 = ARGV[1]
local operation = ARGV[2]
if operation == "add" then
    addApplintmentMeeting(confE164, ARGV[3], ARGV[4], ARGV[5], ARGV[6], ARGV[7])
elseif operation == "update" then
    delApplintmentMeeting(confE164)
    addApplintmentMeeting(confE164, ARGV[3], ARGV[4], ARGV[5], ARGV[6], ARGV[7])
elseif operation == "delete" then
    delApplintmentMeeting(confE164)
end
