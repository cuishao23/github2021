-- 参数: moid kwargs
local moid = ARGV[1]
local kwargs = cjson.decode(ARGV[2])

local terminalAudioInputSignKey = "terminal:" .. moid .. ":audio_input_sign"
local terminalAudioOutputSignKey = "terminal:" .. moid .. ":audio_output_sign"
local terminalVideoInputSignKey = "terminal:" .. moid .. ":video_input_sign"
local terminalVideoOutputSignKey = "terminal:" .. moid .. ":video_output_sign"

for i, info in kwargs["audio_input_sign"] do
    redis.call("HSET", terminalAudioInputSignKey, info["type"], info["status"])
end

for i, info in kwargs["audio_output_sign"] do
    redis.call("HSET", terminalAudioOutputSignKey, info["type"], info["status"])
end

for i, info in kwargs["video_input_sign"] do
    redis.call("HSET", terminalVideoInputSignKey, info["type"], info["status"])
end

for i, info in kwargs["video_output_sign"] do
    redis.call("HSET", terminalVideoOutputSignKey, info["type"], info["status"])
end
