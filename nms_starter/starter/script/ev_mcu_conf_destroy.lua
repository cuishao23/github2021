-- 结会消息
-- 参数: confE164 time

-- 获取会议详情
local function getMeetingInfo(confE164, time)
    local meetingInfo = {}
    local meetingType = redis.call("HGET", "meeting_type_map", confE164)
    local info = redis.call("HGETALL", meetingType .. ":" .. confE164 .. ":info")
    for i = 1, #info / 2 do
        meetingInfo[info[i * 2 - 1]] = info[i * 2]
    end
    meetingInfo["end_time"] = time
    return meetingInfo
end

-- 获取会议评分
local function getTerminalScore(confE164, terminalMoid, meetingMoid)
    local scoreInfo = {
        ["moid"] = terminalMoid,
        ["meeting_moid"] = meetingMoid
    }
    local infoList = {}
    local score = 0
    -- 卡顿
    if redis.call("EXISTS", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":blunt") == 1 then
        local info = {}
        info["type"] = "blunt"
        info["time"] = redis.call("HGET", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":blunt", "time")
        info["score"] = redis.call("HGET", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":blunt", "score")
        info["count"] = redis.call("HGET", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":blunt", "count")
        score = score + tonumber(info["score"])
        table.insert(infoList, info)
    end
    -- 丢包
    if redis.call("EXISTS", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":lossrate") == 1 then
        local info = {}
        info["type"] = "lossrate"
        info["time"] = redis.call("HGET", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":lossrate", "time")
        info["score"] = redis.call("HGET", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":lossrate", "score")
        info["lossrate"] = redis.call("HGET", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":lossrate", "lossrate")
        score = score + tonumber(info["score"])
        table.insert(infoList, info)
    end
    -- 异常离会
    local enterLeaveInfoKey = "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":enter_leave_info:"
    local enterTimes = redis.call("GET", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":enter_times") or "0"
    for i = 1, tonumber(enterTimes) do
        local info = {}
        local reason = redis.call("HGET", enterLeaveInfoKey .. i, "reason")
        if reason == "1" or reason == "3" or reason == "28" or reason == "29" or reason == "30" or reason == "31" then
            info["time"] = redis.call("HGET", enterLeaveInfoKey .. i, "leave_time")
            info["score"] = 0.5
            info["type"] = "leave"
            info["reason"] = reason
            score = score + tonumber(info["score"])
            table.insert(infoList, info)
        end
    end
    redis.call("DEL", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":lossrate")
    redis.call("DEL", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":blunt")
    if score >= 5 then
        score = 5
    end
    scoreInfo["info"] = infoList
    scoreInfo["score"] = score
    return scoreInfo
end

-- 获取离会原因
local function getEnterLeaveInfo(confE164, terminalMoid, meetingMoid, endTime)
    local leaveInfo = {
        ["moid"] = terminalMoid,
        ["meeting_moid"] = meetingMoid
    }
    local infoList = {}
    local enterLeaveInfoKey = "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":enter_leave_info:"
    local enterTimes = redis.call("GET", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":enter_times") or "0"
    for i = 1, tonumber(enterTimes) do
        local info = {}
        info["enter_time"] = redis.call("HGET", enterLeaveInfoKey .. i, "enter_time")
        info["leave_time"] = redis.call("HGET", enterLeaveInfoKey .. i, "leave_time") or endTime
        info["leave_reason"] = redis.call("HGET", enterLeaveInfoKey .. i, "leave_reason") or ""
        table.insert(infoList, info)
        redis.call("DEL", enterLeaveInfoKey .. i)
    end
    redis.call("DEL", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":enter_times")
    leaveInfo["info"] = infoList
    return leaveInfo
end

-- 清理会议相关表结构
local function cleanMeetingInfo(confE164)
    local meetingType = redis.call("HGET", "meeting_type_map", confE164)
    redis.call("HDEL", "meeting_type_map", confE164)
    redis.call("HDEL", "meeting_moid_map", confE164)

    local domainMoid = redis.call("HGET", meetingType .. ":" .. confE164 .. ":info", "domain_moid")
    redis.call("SREM", "domain:" .. domainMoid .. ":" .. meetingType, confE164)

    redis.call(
        "DEL",
        meetingType .. ":" .. confE164 .. ":info",
        "meeting:" .. confE164 .. ":terminal",
        "meeting:" .. confE164 .. ":ipc",
        "meeting:" .. confE164 .. ":telphone",
        "meeting:" .. confE164 .. ":ip_e164",
        "meeting:" .. confE164 .. ":mps",
        "meeting:" .. confE164 .. ":smu",
        -- 会议资源
        "conf_res:" .. confE164 .. ":info"
    )
end

-- 统计会议信息
-- 统计终端离会信息
-- 清除会议相关信息
local confE164 = ARGV[1]
local endTime = ARGV[2]

local result = {
    ["meeting_info"] = {},
    ["leave_reason"] = {},
    ["score_info"] = {}
}

-- 获取会议统计信息
local meetingType = redis.call("HGET", "meeting_type_map", confE164) or ""
local meetingInfoKey = meetingType .. ":" .. confE164 .. ":info"
if redis.call("EXISTS", meetingInfoKey) == 1 then
    local meetingScore = 0
    result["meeting_info"] = getMeetingInfo(confE164, endTime)
    result["meeting_moid"] = redis.call("HGET", "meeting_moid_map", confE164)
    -- 获取终端离会原因统计信息
    result["leave_reason"] = {}
    for i, mtE164 in pairs(redis.call("SMEMBERS", "meeting:" .. confE164 .. ":terminal")) do
        local mtMoid = redis.call("HGET", "terminal:" .. mtE164 .. ":baseinfo", "moid")
        if mtMoid then
            -- 获取终端离会原因统计信息
            local info = getTerminalScore(confE164, mtMoid, result["meeting_moid"])
            table.insert(result["score_info"], info)
            table.insert(result["leave_reason"], getEnterLeaveInfo(confE164, mtMoid, result["meeting_moid"], endTime))
            meetingScore = meetingScore + info["score"]
        end
    end
    local terminalNum = redis.call("SCARD", "meeting:" .. confE164 .. ":terminal") or 0
    terminalNum = tonumber(terminalNum)
    if terminalNum ~= 0 then
        meetingScore = (terminalNum * 5 - meetingScore) / terminalNum
    else
        meetingScore = 5
    end
    result["meeting_info"]["score"] = meetingScore
    -- 清理会议相关表
    cleanMeetingInfo(confE164)
end
return string.gsub(cjson.encode(result), "{}", "[]")
