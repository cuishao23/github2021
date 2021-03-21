-- 添加会议终端
-- 参数: confE164 infoList

-- 入会离会时间统计
local function terminalEnterTime(confE164, mtMoid, time)
    local enterTimesKey = "terminal:" .. mtMoid .. ":conf:" .. confE164 .. ":enter_times"
    local EnterTimes = redis.call("INCRBY", enterTimesKey, "1")
    local enterLeaveInfoKey = "terminal:" .. mtMoid .. ":conf:" .. confE164 .. ":enter_leave_info:" .. EnterTimes
    redis.call("HSET", enterLeaveInfoKey, "enter_time", time)
end

local function addMeetingTerminal(confE164, info)
    local terminal = ""
    local meetingMoid = ""
    local mtE164 = info["e164"]
    local terminalMoid = redis.call("HGET", "terminal:" .. mtE164 .. ":baseinfo", "moid")

    -- 软硬终端入会
    if info["mttype"] == "terminal" and terminalMoid then
        redis.call("SADD", "meeting:" .. confE164 .. ":terminal", info["e164"])
        terminal = info["e164"]
        -- 入会离会时间统计
        terminalEnterTime(confE164, terminalMoid, info["begintime"])
        -- 记录会议E164号
        redis.call('HSET', 'terminal:'.. mtE164 .. ":baseinfo", 'conf', confE164)
    elseif info["mttype"] == "meeting" then
        -- 级联会议
        redis.call("HSET", "meeting:" .. confE164 .. ":meeting", info["e164"], info["type"])
        terminal = info["e164"]
        meetingMoid = redis.call("HGET", "meeting_moid_map", info["e164"])
    elseif info["mttype"] == "telphone" then
        redis.call("SADD", "meeting:" .. confE164 .. ":telphone", info["e164"])
    elseif info["mttype"] == "ipc" then
        redis.call("SADD", "meeting:" .. confE164 .. ":ipc", info["e164"])
    elseif info["mttype"] == "ip_e164" or info["mttype"] == "terminal" then
        redis.call("SADD", "meeting:" .. confE164 .. ":ip_e164", info["e164"])
        -- ip和友商信息
        redis.call(
            "HMSET",
            "ip_e164:" .. info["e164"] .. ":conf:" .. confE164 .. ":info",
            "ip",
            info["e164"],
            "name",
            info["name"]
        )
    end
    return terminal, meetingMoid
end

-- 当前会议的e164
local confE164 = ARGV[1]
local infoList = cjson.decode(ARGV[2])
local result = {}

result["meeting_moid"] = {
    [confE164] = redis.call("HGET", "meeting_moid_map", confE164) or ""
}

-- 记录软硬终端 e164号
result["terminals"] = {}
for i, info in pairs(infoList) do
    local e164, meetingMoid = addMeetingTerminal(confE164, info)
    if e164 ~= "" then
        if meetingMoid == "" then
            table.insert(result["terminals"], e164)
        else
            result["meeting_moid"][e164] = meetingMoid
        end
    end
end
return string.gsub(cjson.encode(result), "{}", "[]")
