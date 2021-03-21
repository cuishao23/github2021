-- 服务器阈值设置
-- 参数: device_moid, cpu, memory, disk, port, diskwritespeed, rateofflow
local device_moid = ARGV[1]
local cpu = ARGV[2]
local memory = ARGV[3]
local disk = ARGV[4]
local port = ARGV[5]
local diskwritespeed = ARGV[6]
local rateofflow = ARGV[7]

local warningServerLimit = "warning:limit:" .. device_moid

redis.call(
    "HMSET",
    warningServerLimit,
    "cpu",
    cpu,
    "memory",
    memory,
    "disk",
    disk,
    "port",
    port,
    "diskwritespeed",
    diskwritespeed,
    "rateofflow",
    rateofflow
)
