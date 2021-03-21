-- 卡顿次数上报
-- 参数: moid count score time
local moid = ARGV[1]
local count = ARGV[2]
local termicalMeetingdetailKey = "terminal:" .. moid .. ":meetingdetail"
redis.call("HSET", termicalMeetingdetailKey, "blunt_count", count)

local confE164 = redis.call("HGET", termicalMeetingdetailKey, "conf_e164")

if confE164 and confE164 ~= "" then
    local oldCount = redis.call("HGET", "terminal:" .. moid .. ":conf:" .. confE164 .. ":blunt", "count") or 0
    local time = string.gsub(ARGV[4], ':', ' ', 1)
    if tonumber(count) > oldCount then
        redis.call(
            "HMSET",
            "terminal:" .. moid .. ":conf:" .. confE164 .. ":blunt",
            "count",
            count,
            "score",
            ARGV[3],
            "time",
            time
        )
    end
end
