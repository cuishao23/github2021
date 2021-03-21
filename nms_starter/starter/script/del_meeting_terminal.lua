-- 终端离会
-- 参数: confE164 time [ipOrE164 leaveReason]

-- 获取主视频信息
local function delTerminalPrivideo(meetingMoid, terminalMoid)
    local video = {}
    local privideoChanList = redis.call("SMEMBERS", "terminal:" .. terminalMoid .. ":meetingdetail:privideo_chan")
    for i, chan in pairs(privideoChanList) do
        local detail = {
            ["meeting_moid"] = meetingMoid,
            ["moid"] = terminalMoid
        }
        local detailList = redis.call("HGETALL", "terminal:" .. terminalMoid .. ":meetingdetail:privideo_chan:" .. chan)
        for i = 1, #detailList / 2 do
            detail[detailList[i * 2 - 1]] = detailList[i * 2]
        end
        table.insert(video, detail)
        redis.call("DEL", "terminal:" .. terminalMoid .. ":meetingdetail:privideo_chan:" .. chan)
    end
    redis.call("DEL", "terminal:" .. terminalMoid .. ":meetingdetail:privideo_chan")
    return video
end

-- 获取辅视频信息
local function delTerminalAssvideo(meetingMoid, terminalMoid)
    local video = {}
    local assvideChanList = redis.call("SMEMBERS", "terminal:" .. terminalMoid .. ":meetingdetail:assvideo_chan")
    for i, chan in pairs(assvideChanList) do
        local detail = {
            ["meeting_moid"] = meetingMoid,
            ["moid"] = terminalMoid
        }
        local detailList = redis.call("HGETALL", "terminal:" .. terminalMoid .. ":meetingdetail:assvideo_chan:" .. chan)
        for i = 1, #detailList / 2 do
            detail[detailList[i * 2 - 1]] = detailList[i * 2]
        end
        table.insert(video, detail)
        redis.call("DEL", "terminal:" .. terminalMoid .. ":meetingdetail:assvideo_chan:" .. chan)
    end
    redis.call("DEL", "terminal:" .. terminalMoid .. ":meetingdetail:assvideo_chan")
    return video
end

-- 获取会议评分
local function getTerminalScore(confE164, terminalMoid)
    local score = 0
    -- 卡顿
    if redis.call("EXISTS", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":blunt") == 1 then
        score = score + tonumber(redis.call("HGET", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":blunt", "score") or 0)
    end
    -- 丢包
    if redis.call("EXISTS", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":lossrate") == 1 then
        score = score + tonumber(redis.call("HGET", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":lossrate", "score") or 0)
    end
    -- 异常离会
    local enterLeaveInfoKey = "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":enter_leave_info:"
    local enterTimes = redis.call("GET", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":enter_times") or "0"
    for i = 1, tonumber(enterTimes) do
        local reason = redis.call("HGET", enterLeaveInfoKey .. i, "reason")
        if reason == "1" or reason == "3" or reason == "28" or reason == "29" or reason == "30" or reason == "31" then
            score = score + 0.5
        end
    end
    if score >= 5 then
        score = 5
    end
    return 5 - score
end

-- 终端与会详情
local function delTerminalDetail(confE164, meeting_moid, terminalMoid)
    -- 基本信息: terminal:moid:meetingdetail
    -- 网络信息: terminal:moid:type:netinfo
    -- 名称和运营商: terminal:moid:baseinfo
    local terminalDetail = {
        ["meeting_moid"] = meeting_moid,
        ["moid"] = terminalMoid
    }
    local detailList = redis.call("HGETALL", "terminal:" .. terminalMoid .. ":meetingdetail")
    for i = 1, #detailList / 2 do
        terminalDetail[detailList[i * 2 - 1]] = detailList[i * 2]
    end
    terminalDetail["mt_name"] = redis.call("HGET", "terminal:" .. terminalMoid .. ":baseinfo", "name") or ""
    terminalDetail["operate"] = redis.call("HGET", "terminal:" .. terminalMoid .. ":baseinfo", "operate_type") or ""
    local terminalType = terminalDetail["mt_type"]
    if terminalType then
        local netinfoKey = "terminal:" .. terminalMoid .. ":" .. string.gsub(terminalType, " ", "~") .. ":netinfo"
        local runningInfoKey = "terminal:" .. terminalMoid .. ":" .. string.gsub(terminalType, " ", "~") .. ":runninginfo"
        terminalDetail["ip"] = redis.call("HGET", netinfoKey, "ip") or ""
        terminalDetail["net_ip"] = redis.call("HGET", netinfoKey, "net_ip") or ""
        terminalDetail["softversion"] = redis.call("HGET", runningInfoKey, "version") or ""
    end
    redis.call("DEL", "terminal:" .. terminalMoid .. ":meetingdetail")
    terminalDetail['score'] = getTerminalScore(confE164, terminalMoid)
    return terminalDetail
end

-- 删除软硬终端
local function delMeetingTerminal(confE164, mtE164, time, leaveReason, meetingMoid)
    local r = {}

    local terminalMoid = redis.call("HGET", "terminal:" .. mtE164 .. ":baseinfo", "moid") or ""
    if confE164 == redis.call("HGET", "terminal:" .. terminalMoid .. ":meetingdetail", "conf_e164") then
        -- 主辅视频信息
        r["privideo"] = delTerminalPrivideo(meetingMoid, terminalMoid)
        r["assvideo"] = delTerminalAssvideo(meetingMoid, terminalMoid)

        -- 终端详情
        r["terminal_detail"] = delTerminalDetail(confE164, meetingMoid, terminalMoid)

        -- 记录终端离会
        if leaveReason ~= "" then
            local enterTimesKey = "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":enter_times"
            local enterTimes = redis.call("GET", enterTimesKey)
            local enterLeaveInfoKey =
                "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":enter_leave_info:" .. enterTimes
            redis.call("HMSET", enterLeaveInfoKey, "leave_time", time, "leave_reason", leaveReason)
        end
    end
    return r
end

local function delMeetingMeeting(confE164, e164)
    redis.call("HDEL", "meeting:" .. confE164 .. ":meeting", e164)
end

local function delMeetingTelphone(confE164, e164)
    redis.call("SREM", "meeting:" .. confE164 .. ":telphone", e164)
end

local function delMeetingIpc(confE164, e164)
    redis.call("SREM", "meeting:" .. confE164 .. ":ipc", e164)
end

local function delMeetingIpE164(confE164, e164)
    redis.call("SREM", "meeting:" .. confE164 .. ":ip_e164", e164)
    redis.call("DEL", "ip_e164:" .. e164 .. ":conf:" .. confE164 .. ":info")
end

local confE164 = ARGV[1]
local time = ARGV[2]
local ipOrE164 = ARGV[3]
local leaveReason = ARGV[4]
local result = {}

local meetingType = redis.call("HGET", "meeting_type_map", confE164) or ''
local meetingMoid = redis.call("HGET", "meeting_moid_map", confE164) or ''
local meetingInfoKey = meetingType .. ":" .. confE164 .. ":info"

-- 会议存在
if redis.call("EXISTS", meetingInfoKey) == 1 then
    -- 单个终端离会, 返回单台信息
    if ipOrE164 then
        if redis.call("SISMEMBER", "meeting:" .. confE164 .. ":terminal", ipOrE164) == 1 then
            result = delMeetingTerminal(confE164, ipOrE164, time, leaveReason, meetingMoid)
        elseif redis.call("HEXISTS", "meeting:" .. confE164 .. ":meeting", ipOrE164) == 1 then
            delMeetingMeeting(confE164, ipOrE164)
        elseif redis.call("SISMEMBER", "meeting:" .. confE164 .. ":telphone", ipOrE164) == 1 then
            delMeetingTelphone(confE164, ipOrE164)
        elseif redis.call("SISMEMBER", "meeting:" .. confE164 .. ":ipc", ipOrE164) == 1 then
            delMeetingIpc(confE164, ipOrE164)
        elseif redis.call("SISMEMBER", "meeting:" .. confE164 .. ":ip_e164", ipOrE164) == 1 then
            delMeetingIpE164(confE164, ipOrE164)
        end
    else
    -- 多终端离会, 返回列表
        for i, e164 in pairs(redis.call("SMEMBERS", "meeting:" .. confE164 .. ":terminal")) do
            local info = delMeetingTerminal(confE164, e164, time, "", meetingMoid)
            table.insert(result, info)
        end
        redis.call("DEL", "meeting:" .. confE164 .. ":meeting")
        redis.call("DEL", "meeting:" .. confE164 .. ":telphone")
        redis.call("DEL", "meeting:" .. confE164 .. ":ipc")
        for i, e164 in pairs(redis.call("SMEMBERS", "meeting:" .. confE164 .. ":terminal")) do
            delMeetingIpE164(confE164, e164)
        end
    end
end

return string.gsub(cjson.encode(result), "{}", "[]")
