-- 获取终端的详细信息
-- 参数: moid
local Key = "terminal:" .. ARGV[1] .. ":baseinfo"

local result = {}
local info = redis.call("HGETALL", Key)
for i, v in pairs(info) do
    if i % 2 == 0 then
        result[info[i - 1]] = v
    end
end
return string.gsub(cjson.encode(result), "{}", "[]")
