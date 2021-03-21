-- 更新国密状态
-- 参数: moid devType
local moid = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, ' ', '~')
local terminalNetinfoKey = "terminal:" .. moid .. ":" .. devKeyType .. ":netinfo"

redis.call(
    "HMSET",
    terminalNetinfoKey,
    "moid",
    moid,
    "recv_bandwidth",
    ARGV[3],
    "recv_droprate",
    ARGV[4],
    "send_bandwidth",
    ARGV[5],
    "send_droprate",
    ARGV[6],
    "timestamp",
    ARGV[7]
)
