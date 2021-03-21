-- 终端基本信息(兼容26终端)
-- 参数 moid devType kwargs

local moidOrE164 = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, " ", "~")
local kwargs = cjson.decode(ARGV[3])
local moid = redis.call("HGET", "terminal:" .. moidOrE164 .. ":baseinfo", "moid")

if moid and moid ~= "" then
    local terminalRunningInfoKey = "terminal:" .. moid .. ":" .. devKeyType .. ":runninginfo"
    local terminalNetinfoKey = "terminal:" .. moid .. ":" .. devKeyType .. ":netinfo"
    local terminalPeripheralCameraKey = "terminal:" .. moid .. ":" .. devKeyType .. ":peripheral:camera"
    local terminalPeripheralMicrophoneKey = "terminal:" .. moid .. ":" .. devKeyType .. ":peripheral:microphone"

    redis.call("HMSET", terminalRunningInfoKey, "moid", moid, "type", devType)
    if kwargs["runninginfo"] then
        for i, info in pairs(kwargs["runninginfo"]) do
            redis.call("HSET", terminalRunningInfoKey, i, info)
        end
    end

    redis.call("HSET", terminalNetinfoKey, "moid", moid)
    if kwargs["netinfo"] then
        for i, info in pairs(kwargs["netinfo"]) do
            redis.call("HSET", terminalNetinfoKey, i, info)
        end
    end

    if kwargs["cameras"] then
        for i, info in pairs(kwargs["cameras"]) do
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
    end

    if kwargs["microphones"] then
        for i, info in pairs(kwargs["microphones"]) do
            redis.call("SADD", terminalPeripheralMicrophoneKey, info["id"])
            local peripheralMicrophoneInfoKey = "peripheral:microphone:" .. info["id"] .. ":info"
            redis.call(
                "HMSET",
                peripheralMicrophoneInfoKey,
                "id",
                info["id"],
                "type",
                info["type"],
                "version",
                info["version"],
                "status",
                info["status"]
            )
        end
    end
end
