-- 点对点创会消息
-- 参数: devmoid meetingMoid confInfo
local pasMoid = ARGV[1]
local meetingMoid = ARGV[2]
local confInfo = cjson.decode(ARGV[3])

local function getTerminalDomainMoid(e164)
    local key = "terminal:" .. e164 .. ":baseinfo"
    return redis.call("HGET", key, "domain_moid")
end

local callerDomainMoid = getTerminalDomainMoid(confInfo["caller"]["deve164"])
local calleeDomainMoid = getTerminalDomainMoid(confInfo["caller"]["deve164"])

if callerDomainMoid ~= nil and calleeDomainMoid ~= nil then
    local confE164 = confInfo["caller"]["deve164"]

    redis.call("SADD", "pas:" .. pasMoid .. ":p2p_meeting", confE164)
    redis.call("SADD", "domain:" .. callerDomainMoid .. ":p2p_meeting", confE164)

    redis.call("HSET", "meeting_moid_map", confE164, meetingMoid)
    redis.call("HSET", "meeting_type_map", confE164, "p2p_meeting")
    redis.call(
        "HMSET",
        "p2p_meeting:" .. confE164 .. ":info",
        "meeting_moid",
        meetingMoid,
        "domain_moid",
        callerDomainMoid,
        "caller_domain_moid",
        callerDomainMoid,
        "caller_e164",
        confInfo["caller"]["deve164"],
        "caller_name",
        confInfo["caller"]["devname"],
        "caller_type",
        confInfo["caller"]["devtype"],
        "callee_domain_moid",
        calleeDomainMoid,
        "callee_e164",
        confInfo["callee"]["deve164"],
        "callee_name",
        confInfo["callee"]["devname"],
        "callee_type",
        confInfo["callee"]["devtype"],
        "bandwidth",
        confInfo["bitrate"],
        "start_time",
        confInfo["time"]
    )
end
