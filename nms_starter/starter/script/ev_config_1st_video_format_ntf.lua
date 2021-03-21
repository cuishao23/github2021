-- 卡顿次数上报
-- 参数: moid devtype

local moid = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, ' ', '~')
local result = ARGV[3]

local terminalVideoFormatResultKey = "terminal:" .. moid .. ":" .. devKeyType .. ":video_format_result"
redis.call("HSET", terminalVideoFormatResultKey, "result", result)
