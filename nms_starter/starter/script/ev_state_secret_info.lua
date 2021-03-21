-- 更新国密状态
-- 参数: moid devType state
local moid = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, ' ', '~')
local state = ARGV[3]
local terminalRuninginfoKey = "terminal:" .. moid .. ":" .. devKeyType .. ":runinginfo"

redis.call("HSET", terminalRuninginfoKey, "state_secret", state)
