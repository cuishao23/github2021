-- 终端会议信息
-- 参数: mtMod mtType state confInfo

local function updateTerminalOnlineState(mtMoid, mtType, state)
    -- 更新终端在线状态
    local onlineStateKey = "terminal:" .. mtMoid .. ":onlinestate"
    redis.call("HSET", onlineStateKey, mtType, state)
end

local function initMeetingDetail(confE164, mtMoid, mtType)
    -- 初始化会议详情表: meeting_moid, mt_type, mt_e164
    local meetingDetailKey = "terminal:" .. mtMoid .. ":meetingdetail"
    local mtE164 = redis.call("HGET", "terminal:" .. mtMoid .. ":baseinfo", "e164")
    redis.call("HMSET", meetingDetailKey, "mt_e164", mtE164, "mt_type", mtType, "conf_e164", confE164)
end

local function delVideoAudo(mtMoid)
    for i, suffix in pairs({"privideo_chan", "assvideo_chan"}) do
        local chanKey = "terminal:" .. mtMoid .. "meetingdetail:" .. suffix
        local priNum = redis.call("GET", chanKey) or 0
        for i = 0, tonumber(priNum) - 1 do
            local key = chanKey .. ":" .. i
            redis.call("DEL", key)
        end
    end
end

local function updateLossRateScore(mtMoid, confE164, lossrate, score, time)
    local oldLossrate =
        redis.call("HGET", "terminal:" .. mtMoid .. ":conf:" .. confE164 .. ":lossrate", "lossrate") or 0
    local time = string.gsub(time, ':', ' ', 1)
    if tonumber(lossrate) > tonumber(oldLossrate) then
        redis.call(
            "HMSET",
            "terminal:" .. mtMoid .. ":conf:" .. confE164 .. ":lossrate",
            "lossrate",
            lossrate,
            "score",
            score,
            "time",
            time
        )
    end
end

local mtMoid = ARGV[1]
local mtType = ARGV[2]
local state = ARGV[3]
updateTerminalOnlineState(mtMoid, mtType, state)
if state == "conference" then
    local confInfo = cjson.decode(ARGV[4])
    local confE164 = confInfo["conf_e164"]

    initMeetingDetail(confE164, mtMoid, mtType)
    -- 更新会议详情
    redis.call(
        "HMSET",
        "terminal:" .. mtMoid .. ":meetingdetail",
        "conf_bitrate",
        confInfo["bitrate"],
        "mute",
        confInfo["mute"],
        "dumbness",
        confInfo["dumbness"],
        "encryption",
        confInfo["encryption"]
    )

    delVideoAudo(mtMoid)
    -- 存储主视频信息
    for i, info in pairs(confInfo["privideo_chan"]) do
        redis.call("SADD", "terminal:" .. mtMoid .. ":meetingdetail:privideo_chan", i)
        local key = "terminal:" .. mtMoid .. ":meetingdetail:privideo_chan:" .. i
        for k, v in pairs(confInfo["privideo_chan"][i]) do
            redis.call("HSET", key, k, v)
        end
    end
    -- 存储辅视频信息
    for i, info in pairs(confInfo["assvideo_chan"]) do
        redis.call("SADD", "terminal:" .. mtMoid .. ":meetingdetail:assvideo_chan", i)
        local key = "terminal:" .. mtMoid .. ":meetingdetail:assvideo_chan:" .. i
        for k, v in pairs(confInfo["assvideo_chan"][i]) do
            redis.call("HSET", key, k, v)
        end
    end
    updateLossRateScore(mtMoid, confE164, confInfo['lossrate'], confInfo['score'], confInfo['time'])
end
