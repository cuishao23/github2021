-- Sky终端上报网呈IMIX设备信息
-- 参数: moid devType imixType sn mac ip version id
local Moid = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, ' ', '~')
local ImixType = ARGV[3]
local Sn = ARGV[4]
local Mac = ARGV[5]
local Ip = ARGV[6]
local Version = ARGV[7]
local Id = ARGV[8]

-- 添加imix到终端imix列表
local TerminalImixKey = "terminal:" .. Moid .. ":" .. devKeyType .. ":peripheral:imix"
redis.call("SADD", TerminalImixKey, Id)

-- 添加imix信息
local ImixInfoKey = "peripheral:imix:" .. Id .. ":info"
redis.call("HMSET", ImixInfoKey, "type", ImixType, "sn", Sn, "mac", Mac, "ip", Ip, "version", Version)
