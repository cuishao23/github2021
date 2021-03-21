local result = {}

local function getLicensePServer(mac)
    return redis.call("GET", "mac:" .. string.lower(string.gsub(mac, ":", '')) .. ":moid") or ""
end
local licenses = redis.call("SMEMBERS", "licenses")

for i, license in pairs(licenses) do
    local info = {}
    info["date"] = redis.call("HGET", "license:" .. license .. ":info", "mcu_exp_date")
    info["p_server_moid"] = getLicensePServer(redis.call("HGET", "license:" .. license .. ":info", "mac_id"))
    table.insert(result, info)
end

return string.gsub(cjson.encode(result), "{}", "[]")
