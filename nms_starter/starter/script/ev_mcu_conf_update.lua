-- 会议状态更新
-- 参数: meetingType  confE164

local meetingType = ARGV[1]
local confE164 = ARGV[2]
local confName = ARGV[3]

redis.call("HSET", meetingType .. ":" .. confE164 .. ":info", "conf_name", confName)
