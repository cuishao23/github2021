-- 数据会议创建信息
-- 参数: dcsMeetingMoid confE164 dcsMode beginTime mtInfo

local addDcsTerminal = function(confE164, mtE164, coopState, beginTime)
    local dscTerminalsKey = "meeting:" .. confE164 .. ":dcs_terminals"
    local terminalInfoForDcsKey = "terminal:" .. mtE164 .. ":conf:" .. confE164 .. ":info_for_dcs"
    redis.call("SADD", dscTerminalsKey, mtE164)
    local name = redis.call("HGET", "terminal:" .. mtE164 .. ":baseinfo", "name")
    redis.call(
        "HMSET",
        terminalInfoForDcsKey,
        "name",
        name,
        "e164",
        mtE164,
        "coop_state",
        coopState,
        "begin_time",
        beginTime
    )
end

local dcsMeetingMoid = ARGV[1]
local confE164 = ARGV[2]
local dcsMode = ARGV[3]
local beginTime = ARGV[4]
local mtInfo = cjson.decode(ARGV[5])

local meetingDcs = "meeting:" .. confE164 .. ":dcs_info"
local meetingMoid = redis.call("HGET", "meeting_moid_map", confE164) or ""

redis.call(
    "HMSET",
    meetingDcs,
    "meeting_moid",
    meetingMoid,
    "dcs_moid",
    dcsMeetingMoid,
    "dcs_start_time",
    beginTime,
    "dcs_mode",
    dcsMode,
    "dcs_mode_start_time",
    beginTime
)

for i, info in pairs(mtInfo) do
    if info["onlinestate"] == 1 or info["onlinestate"] == "1" then
        addDcsTerminal(confE164, info["mtaccount"], info["coopstate"], beginTime)
    end
end
