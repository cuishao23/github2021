-- 结束直播
-- 参数: vrsMoid confE164 endTime

local function getLiveInfo(confE164, endTime)
    local r = {}
    local key = "meeting:" .. confE164 .. ":live"
    r["live_name"] = redis.call("HGET", key, "live_name")
    r["meeting_moid"] = redis.call("HGET", key, "meeting_moid")
    r["live_moid"] = redis.call("HGET", key, "live_moid")
    r["live_start_time"] = redis.call("HGET", key, "live_start_time")
    r["live_end_time"] = endTime
    r["max_user_time"] = redis.call("HGET", key, "max_user_time")
    r["max_user_count"] = redis.call("HGET", key, "max_user_count")
    return r
end

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

local vrsMoid = ARGV[1]
local confE164 = ARGV[2]
local endTime = ARGV[3]

local result = {}

-- user
local liveUsersKey = "meeting:" .. confE164 .. ":live_users"
local LiveUserList = redis.call("SMEMBERS", liveUsersKey)
result["live_users"] = {}
for i, userMoid in ipairs(LiveUserList) do
    table.insert(result["live_users"], getLiveUserInfo(confE164, userMoid, endTime))
    redis.call("DEL", "user:" .. userMoid .. ":conf:" .. confE164 .. ":info_for_live")
end
result["live_info"] = getLiveInfo(confE164, endTime)
redis.call("DEL", liveUsersKey)
redis.call("DEL", "meeting:" .. confE164 .. ":live")
redis.call("SREM", "vrs:" .. vrsMoid .. ":live", confE164)

return string.gsub(cjson.encode(result), "{}", "[]")
