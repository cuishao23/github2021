-- 获取告警详情
-- 参数: code
local code = ARGV[1]
local Key = "warning:code:" .. code

local result = {}
local info = redis.call("HGETALL", Key)
for i, v in pairs(info) do
    if i % 2 == 0 then
        result[info[i - 1]] = v
    end
end
result["code"] = tonumber(code)
return string.gsub(cjson.encode(result), "{}", "[]")
