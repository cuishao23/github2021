-- 数据会议模式切换
-- 参数: confE164 mode time

local function getDcsModeInfo(confE164, endTime)
    local r = {}
    local dcsInfoKey = "meeting:" .. confE164 .. ":dcs_info"
    r["dcs_mode"] = redis.call("HGET", dcsInfoKey, "dcs_mode")
    r["dcs_moid"] = redis.call("HGET", dcsInfoKey, "dcs_moid")
    r["mode_start_time"] = redis.call("HGET", dcsInfoKey, "mode_start_time")
    r["mode_end_time"] = endTime
    return r
end

local confE164 = ARGV[1]
local mode = ARGV[2]
local time = ARGV[3]
local result = {}

local dcsInfoKey = "meeting:" .. confE164 .. ":dcs_info"
local oldMode = redis.call("HGET", dcsInfoKey, "dcs_mode")
if oldMode and tonumber(oldMode) ~= tonumber(mode) then
    result = getDcsModeInfo(confE164, time)
    redis.call("HMSET", dcsInfoKey, "dcs_mode", mode, "mode_start_time", time)
end

return string.gsub(cjson.encode(result), "{}", "[]")
