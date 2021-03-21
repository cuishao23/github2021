local function getLicensePServer(mac)
    return redis.call("GET", "mac:" .. string.lower(string.gsub(mac, ":", "")) .. ":moid") or ""
end

local license = ARGV[1]
return getLicensePServer(redis.call("HGET", "license:" .. license .. ":info", "mac_id"))
