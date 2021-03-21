-- 终端性能
-- 参数: moid terminalType kwargs
local moid = ARGV[1]
local terminalType = ARGV[2]
local devType = string.gsub(terminalType, ' ', '~')
local kwargs = cjson.decode(ARGV[3])
local terminalNetinfoKey = "terminal:" .. moid .. ":" .. devType .. ":netinfo"

-- netcards
local terminalNetcardsKey = "terminal:" .. moid .. ":" .. devType .. ":netcards"
for i, info in pairs(kwargs["netcards"]) do
    redis.call("SADD", terminalNetcardsKey, info["name"])
    kwargs["pfm_info"][info["name"] .. "_type"] = info["netcardtype"]
    kwargs["pfm_info"][info["name"] .. "_sendkbps"] = info["sendkbps"]
    kwargs["pfm_info"][info["name"] .. "_recvkbps"] = info["recvkbps"]
end

-- pfm_info
local terminalPfminfoKey = "terminal:" .. moid .. ":" .. devType .. ":pfm_info"
for key, info in pairs(kwargs["pfm_info"]) do
    redis.call("HSET", terminalPfminfoKey, key, info)
end

-- video
local terminalVideoKey = "terminal:" .. moid .. ":" .. devType .. ":video"
for i, info in pairs(kwargs["video_redource_name"]) do
    local terminalVideoInfoKey = terminalVideoKey .. ":" .. info["video_index"] .. ":info"
    redis.call("SADD", terminalVideoKey, info["video_index"])
    redis.call("HSET", terminalVideoInfoKey, "type", info["type"])
end

-- microphone
local terminalMicrophoneKey = "terminal:" .. moid .. ":" .. devType .. ":microphone"
for i, info in pairs(kwargs["microphones"]) do
    local terminalMicrophoneInfoKey = terminalMicrophoneKey .. ":" .. info["name"] .. ":info"
    redis.call("SADD", terminalMicrophoneKey, info["name"])
    redis.call("HSET", terminalMicrophoneInfoKey, "status", info["status"])
end

-- loudspeaker
local terminalLoudspeakersKey = "terminal:" .. moid .. ":" .. devType .. ":loudspeaker"
for i, info in pairs(kwargs["loudspeakers"]) do
    local terminalLoudspeakersInfoKey = terminalLoudspeakersKey .. ":" .. info["name"] .. ":info"
    redis.call("SADD", terminalLoudspeakersKey, info["name"])
    redis.call("HSET", terminalLoudspeakersInfoKey, "status", info["status"])
end
