-- 更新直播用户
-- 参数: confE164 userE164 userMoid userName changeTime userState

local getLiveUserInfo = function(confE164, userMoid, leaveTime)
    local r = {}
    local key = "user:" .. userMoid .. ":conf:" .. confE164 .. ":info_for_live"
    r["live_moid"] = redis.call("HGET", "meeting:" .. confE164 .. ":live", "live_moid")
    r["user_name"] = redis.call("HGET", key, "name")
    r["user_e164"] = redis.call("HGET", key, "e164")
    r["user_moid"] = redis.call("HGET", key, "moid")
    r["enter_time"] = redis.call("HGET", key, "enter_time")
    r["leave_time"] = leaveTime
    return r
end

local userMoid = ARGV[1]
local confE164 = ARGV[2]
local userE164 = ARGV[3]
local userName = ARGV[4]
local changeTime = ARGV[5]
local userState = ARGV[6]

-- 直播信息
local confLiveKey = "meeting:" .. confE164 .. ":live"
-- 直播用户
local liveUsersKey = "meeting:" .. confE164 .. ":live_users"
-- 用户详细信息
local userInfoForLiveKey = "user:" .. userMoid .. ":conf:" .. confE164 .. ":info_for_live"

local maxUserCount = redis.call("HGET", confLiveKey, "max_user_count")
local currentUserCount
if userState == 1 or userState == "1" then
    currentUserCount = redis.call("HINCRBY", confLiveKey, "current_user_count", 1)
else
    redis.call("HINCRBY", confLiveKey, "current_user_count", -1)
end
if tonumber(currentUserCount) > tonumber(maxUserCount) then
    redis.call("HMSET", confLiveKey, "max_user_time", changeTime, "max_user_count", currentUserCount)
end

local result = {}
if not userMoid or userMoid ~= "" then
    if userState == 1 or userState == "1" then -- 上线
        redis.call("SADD", liveUsersKey, userMoid)
        redis.call(
            "HMSET",
            userInfoForLiveKey,
            "moid",
            userMoid,
            "e164",
            userE164,
            "name",
            userName,
            "enter_time",
            changeTime
        )
    else --下线
        result = getLiveUserInfo(confE164, userMoid, changeTime)
        redis.call("SREM", liveUsersKey, userMoid)
        redis.call("DEL", userInfoForLiveKey)
    end
end

return string.gsub(cjson.encode(result), "{}", "[]")
