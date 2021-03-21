-- 音量能量
-- 参数: moid input output

local termicalMeetingdetailKey = "termical:" .. ARGV[1] .. ":meetingdetail"
redis.call("HMSET", termicalMeetingdetailKey, "input_volume", ARGV[2], "output_volume", ARGV[3])
