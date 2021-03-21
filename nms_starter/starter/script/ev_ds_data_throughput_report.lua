-- 上报转发流量
-- 参数: moid rate

local function getServerLimit(pServerMoid, limitType)
    local defaultLimit = {
        ["cpu"] = 80,
        ["memory"] = 80,
        ["disk"] = 80,
        ["port"] = 60,
        ["diskwritespeed"] = 2,
        ["rateofflow"] = 500
    }
    local limit = redis.call("HGET", "warning:limit:" .. pServerMoid, limitType)
    if not limit then
        limit = defaultLimit[limitType]
    end
    return limit
end

local moid = ARGV[1]
local rate = ARGV[2]

local pServerMoid = redis.call("HGET", "l_server:" .. moid .. ":info", "p_server_moid")

local result = {}

local limit = getServerLimit(pServerMoid, "rateofflow")
result["warning_trigger_flag"] = tonumber(rate) >= tonumber(limit)
result["p_server_moid"] = pServerMoid
result["current_value"] = rate
result["threshold_value"] = limit

return string.gsub(cjson.encode(result), "{}", "[]")
