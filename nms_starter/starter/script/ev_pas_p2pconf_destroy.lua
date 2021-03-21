-- 点对点会议结会
-- 参数: pasMoid callerE164 calleeE164 time

-- 获取会议详情
local function getMeetingInfo(confE164, time)
    local meetingInfo = {}
    local info = redis.call("HGETALL", "p2p_meeting:" .. confE164 .. ":info")
    for i = 1, #info / 2 do
        meetingInfo[info[i * 2 - 1]] = info[i * 2]
    end
    meetingInfo["end_time"] = time
    return meetingInfo
end

-- 获取会议评分
local function getTerminalScore(confE164, terminalMoid)
    local score = 0
    -- 卡顿
    if redis.call("EXISTS", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":blunt") == 1 then
        score =
            score +
            tonumber(redis.call("HGET", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":blunt", "score") or 0)
    end
    -- 丢包
    if redis.call("EXISTS", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":lossrate") == 1 then
        score =
            score +
            tonumber(
                redis.call("HGET", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":lossrate", "score") or 0
            )
    end
    if score >= 5 then
        score = 5
    end
    return 5 - score
end

-- 获取会议终端详情
-- 终端与会详情
local function delTerminalDetail(meeting_moid, terminalMoid)
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
        local runningInfoKey =
            "terminal:" .. terminalMoid .. ":" .. string.gsub(terminalType, " ", "~") .. ":runninginfo"
        terminalDetail["ip"] = redis.call("HGET", netinfoKey, "ip") or ""
        terminalDetail["net_ip"] = redis.call("HGET", netinfoKey, "net_ip") or ""
        terminalDetail["softversion"] = redis.call("HGET", runningInfoKey, "version") or ""
    end
    redis.call("DEL", "terminal:" .. terminalMoid .. ":meetingdetail")
    return terminalDetail
end

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

-- 删除软硬终端
local function delMeetingTerminal(confE164, mtE164, time, leaveReason, meetingMoid)
    local r = {}

    local terminalMoid = redis.call("HGET", "terminal:" .. mtE164 .. ":baseinfo", "moid") or ""
    if confE164 == redis.call("HGET", "terminal:" .. terminalMoid .. ":meetingdetail", "conf_e164") then
        -- 主辅视频信息
        r["privideo"] = delTerminalPrivideo(meetingMoid, terminalMoid)
        r["assvideo"] = delTerminalAssvideo(meetingMoid, terminalMoid)

        -- 终端详情
        r["terminal_detail"] = delTerminalDetail(meetingMoid, terminalMoid)

        -- 评分计算
        local score = 5
        score = getTerminalScore(confE164, terminalMoid)
        r["terminal_detail"]["score"] = score
        redis.call("DEL", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":blunt")
        redis.call("DEL", "terminal:" .. terminalMoid .. ":conf:" .. confE164 .. ":lossrate")
    end
    return r
end

-- 清理会议相关表结构
local function cleanMeetingInfo(pasMoid, callerE164, calleeE164)
    local confE164 = callerE164
    local domainMoid = redis.call("HGET", "p2p_meeting:" .. confE164 .. ":info", "domain_moid") or ""
    redis.call("SREM", "pas:" .. pasMoid .. ":p2p_meeting", confE164)
    redis.call("SREM", "domain:" .. domainMoid .. ":p2p_meeting", confE164)
    redis.call("HDEL", "meeting_moid_map", confE164)
    redis.call("HDEL", "meeting_type_map", confE164)

    redis.call(
        "DEL",
        "p2p_meeting:" .. confE164 .. ":info",
        "terminal:" .. callerE164 .. ":meetingdetail",
        "terminal:" .. calleeE164 .. ":meetingdetail",
        "conf_res:" .. confE164 .. ":info"
    )
end

local pasMoid = ARGV[1]
local callerE164 = ARGV[2]
local calleeE164 = ARGV[3]
local time = ARGV[4]
local confE164 = callerE164
local result = {}
if redis.call("EXISTS", "p2p_meeting:" .. confE164 .. ":info") == 1 then
    local meetingMoid = redis.call("HGET", "meeting_moid_map", callerE164)
    result["terminal_info"] = {}
    local callerInfo = delMeetingTerminal(confE164, callerE164, time, "", meetingMoid)
    local calleeInfo = delMeetingTerminal(confE164, calleeE164, time, "", meetingMoid)
    if next(callerInfo) ~= nil and next(calleeInfo) ~= nil then
        result["terminal_info"][callerE164] = callerInfo
        result["terminal_info"][calleeE164] = calleeInfo
        result["meeting_info"] = getMeetingInfo(confE164, time)

        -- 计算会议评分
        local score = (callerInfo["terminal_detail"]["score"] + calleeInfo["terminal_detail"]["score"]) / 2
        result["meeting_info"]["score"] = score
    end
    cleanMeetingInfo(pasMoid, callerE164, calleeE164)
end
return string.gsub(cjson.encode(result), "{}", "[]")
