-- 参数: moid devType kwargs
local moid = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, ' ', '~')
local kwargs = cjson.decode(ARGV[3])

local terminalPeripheralCameraKey = "terminal:" .. moid .. ":" .. devKeyType .. ":peripheral:camera"

for i, info in pairs(kwargs) do
    redis.call("SADD", terminalPeripheralCameraKey, info["id"])
    local peripheralCameraInfoKey = "peripheral:camera:" .. info["id"] .. ":info"
    redis.call(
        "HMSET",
        peripheralCameraInfoKey,
        "id",
        info["id"],
        "type",
        info["type"],
        "version",
        info["version"],
        "SN",
        info["SN"],
        "status",
        info["status"]
    )
end
