-- 创建直播
-- 参数: vrsMoid confE164 liveMoid liveName liveStartTime encmode authmode

local vrsMoid = ARGV[1]
local confE164 = ARGV[2]
local meetingMoid = redis.call("HGET", "meeting_moid_map", confE164) or ""

redis.call("SADD", "vrs:" .. vrsMoid .. ":live", confE164)

redis.call(
    "HMSET",
    "meeting:" .. confE164 .. ":live",
    "vrs_moid",
    vrsMoid,
    "meeting_moid",
    meetingMoid,
    "live_moid",
    ARGV[3],
    "live_name",
    ARGV[4],
    "live_start_time",
    ARGV[5],
    "encmode",
    ARGV[6],
    "authmode",
    ARGV[7],
    "max_user_time",
    ARGV[5],
    "max_user_count",
    0,
    "current_user_count",
    0
)

-- 清理可能残留的直播用户信息
local users = redis.call("SMEMBERS", "meeting:" .. confE164 .. ":live_users")
for i, userMoid in pairs(users) do
    redis.call("DEL", "user:" .. userMoid .. "conf:" .. confE164 .. ":info_for_live")
end
redis.call("DEL", "meeting:" .. confE164 .. ":live_users")
