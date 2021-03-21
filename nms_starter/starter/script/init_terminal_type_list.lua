-- 初始化终端类型对应表

local typeList = cjson.decode(ARGV[1])
local key = "terminal_type_list"
redis.call("DEL", key)
for i, type in pairs(typeList) do
    redis.call("HSET", key, string.gsub(type, " ", "~"), type)
end
