-- 内存消息处理
-- 参数: moid memtotal memused memory
local moid = ARGV[1]
local memtotal = ARGV[2]
local memused = ARGV[3]
local memory = ARGV[4]
local result = {}
local pServerResourceKey = "p_server:" .. moid .. ":resource"
local warningLimitKey = "warning:limit:" .. moid
redis.call("HMSET", pServerResourceKey, "memtotal", memtotal, "memused", memused, "memory", memory)

-- 阈值判定
result["threshold_value"] = redis.call("HGET", warningLimitKey, "memory") or 80
result["waring"] = tonumber(memory) >= tonumber(result["threshold_value"])
result["current_value"] = memory
result["machine_room_moid"] = redis.call("HGET", "p_server:" .. moid .. ":info", "machine_room_moid")
return string.gsub(cjson.encode(result), "{}", "[]")
