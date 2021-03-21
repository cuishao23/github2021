-- 获取告警通知联系方式
-- 参数: code
local code = ARGV[1]

local result = {}
local emailKey = "warning:notify:" .. code .. ":email"
local phoneKey = "warning:notify:" .. code .. ":phone"
local wechatKey = "warning:notify:" .. code .. ":wechat"

result["email"] = redis.call("SMEMBERS", emailKey)
result["phone"] = redis.call("SMEMBERS", phoneKey)
result["wechat"] = redis.call("SMEMBERS", wechatKey)

return string.gsub(cjson.encode(result), "{}", "[]")
