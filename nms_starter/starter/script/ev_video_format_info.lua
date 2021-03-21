-- 参数: moid devType videoFormat
local moid = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, ' ', '~')
local videoFormat = ARGV[3]
local terminalRuninginfoKey = "terminal:" .. moid .. ":" .. devKeyType .. ":runinginfo"

redis.call("HSET", terminalRuninginfoKey, "video_format", videoFormat)
