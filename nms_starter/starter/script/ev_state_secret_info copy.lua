-- 更新国密状态
-- 参数: moid devType state
local moid = ARGV[1]
local devType = ARGV[2]
local state = ARGV[3]
local terminalRuninginfoKey = "terminal:" .. moid .. ":" .. devType .. ":runinginfo"

redis.call("HSET", terminalRuninginfoKey, "state_secret", state)
