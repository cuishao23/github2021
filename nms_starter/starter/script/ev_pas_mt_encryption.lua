-- 终端加密类型
-- 参数: mt_info

local info = cjson.decode(ARGV[1])

for i, v in pairs(info) do
    local e164 = v["mt_e164"] or ""
    local encryption = v["mt_encryption"] or ""
    local moid = redis.call("HGET", "terminal:" .. e164 .. ":baseinfo", "moid")
    if moid then
        redis.call("HSET", "terminal:" .. moid .. ":meetingdetail", "encryption", encryption)
    end
end
