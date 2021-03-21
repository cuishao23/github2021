-- 安全告警
-- 参数: moid moduleType alarmCode alarmStatus

local moid = ARGV[1]
local moduleType = ARGV[2]
local alarmCode = ARGV[3]
local alarmStatus = ARGV[4]

local result = {}

local alarmInfoKey = "l_server:" .. moid .. ":" .. alarmCode .. ":alarm_info"
if alarmStatus == "1" or alarmStatus == 1 then
    if redis.call("SCARD", alarmInfoKey) == 0 then
        -- 首次告警
        result["warning_trigger_flag"] = true
    end
    redis.call("SADD", alarmInfoKey, moduleType)
else
    redis.call("SREM", alarmInfoKey, moduleType)
    if redis.call("SCARD", alarmInfoKey) == 0 then
        -- 修复告警
        result["warning_trigger_flag"] = false
    end
end

return string.gsub(cjson.encode(result), "{}", "[]")
