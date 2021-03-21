-- TODO
local moid = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, " ", "~")
local microphoneId = ARGV[3]

--add terminal microphone info --
local microphoneListKey = "terminal:" .. moid .. ":" .. devKeyType .. ":microphone"

redis.call("SREM", microphoneListKey, microphoneId)

local microphoneInfoKey = "microphone:" .. microphoneId .. ":info"
redis.call("DEL", microphoneInfoKey)
