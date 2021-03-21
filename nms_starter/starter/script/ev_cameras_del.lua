-- 参数: moid devType kwargs
local moid = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, ' ', '~')
local kwargs = cjson.decode(ARGV[3])

local terminalPeripheralCameraKey = "terminal:" .. moid .. ":" .. devKeyType .. ":peripheral:camera"

for i, id in pairs(kwargs) do
    redis.call("SREM", terminalPeripheralCameraKey, id)
    local peripheralCameraInfoKey = "peripheral:camera:" .. id .. ":info"
    redis.call("DEl", peripheralCameraInfoKey)
end
