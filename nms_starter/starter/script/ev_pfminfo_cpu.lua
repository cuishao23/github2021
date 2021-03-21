-- CPU消息处理
-- 参数: moid 总使用率 json
local moid = ARGV[1]
local cpu = ARGV[2]
local cpuCount = ARGV[3]
local coreInfo = cjson.decode(ARGV[4])
local pServerResourceKey = "p_server:" .. moid .. ":resource"
local warning = false
local warningLimitKey = "warning:limit:" .. moid
local limit = redis.call("HGET", warningLimitKey, "cpu") or 80

redis.call("HSET", pServerResourceKey, "cpu", cpu)
redis.call("HSET", pServerResourceKey, "cpu_count", cpuCount)

local result = {}
result["threshold_value"] = limit
result["current_value"] = 0
for core, value in pairs(coreInfo) do
    if tonumber(value) >= tonumber(limit) then
        warning = true
    end
    if tonumber(value) > tonumber(result["current_value"]) then
        result["current_value"] = value
    end
    redis.call("HSET", pServerResourceKey, core, value)
end
result["warning"] = warning
result["machine_room_moid"] = redis.call("HGET", "p_server:" .. moid .. ":info", "machine_room_moid")
return string.gsub(cjson.encode(result), "{}", "[]")
