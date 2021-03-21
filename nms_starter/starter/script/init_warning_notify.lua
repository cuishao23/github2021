-- 初始化告警通知信息
-- 参数: [{"domain_moid": "xxxx", "id": "xxx", "code_list": [3001, 3002], "email": xx, ...}]
local kwargs = cjson.decode(ARGV[1])
for i, info in pairs(kwargs) do
    local id = tostring(info["id"])
    redis.call("SADD", "warning:notify:" .. info["domain_moid"], id)
    redis.call(
        "HMSET",
        "warning:notify:" .. id .. ":info",
        "email",
        info["email"],
        "phone",
        info["phone"],
        "wechat",
        info["wechat"]
    )
    for j, code in pairs(info["code_list"]) do
        redis.call("SADD", "warning:notify:" .. id .. ":codes", code)
    end
end
