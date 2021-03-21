-- 修改会议预约时间
-- 参数: meetingType confE164 time

local meetingType = ARGV[1]
local confE164 = ARGV[2]
local time = ARGV[3]

redis.call("HSET", meetingType .. ":" .. confE164 .. ":info", "end_time", time)
