-- 会议资源占用情况
-- 参数: args

local args = cjson.decode(ARGV[1])

for i, info in pairs(args) do
    local confE164 = info["conf_e164"]
    local port = info["prot"] or 0
    local tra = info["tra"] or 0
    local key = "conf_res:" .. confE164 .. ":info"
    if tra == 0 and port == 0 then
        redis.call("DEL", key)
    else
        redis.call("HMSET", key, "port", port, "tra", tra)
    end
end
