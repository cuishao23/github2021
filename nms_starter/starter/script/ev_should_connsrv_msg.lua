-- 更新国密状态
-- 参数: moid devType kwargs
local moid = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, ' ', '~')
local kwargs = cjson.decode(ARGV[3])
local terminalConnectionKey = "terminal:" .. moid .. ":" .. devKeyType .. ":connection"

-- 将ip信息置空
for i, info in pairs(kwargs) do
    redis.call("HSET", terminalConnectionKey, info, "")
end
