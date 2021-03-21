-- 运营商信息
-- info

local info = cjson.decode(ARGV[1])

for k, v in pairs(info) do
    redis.call("HSET", "terminal:" .. v["mt_moid"] .. ":baseinfo", "operator_type", v["operator_type"])
end
