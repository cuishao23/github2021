-- 更新国密状态
-- 参数: moid devType state
local moid = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, ' ', '~')
local terminalNetinfoKey = "terminal:" .. moid .. ":" .. devKeyType .. ":netinfo"

redis.call(
    "HMSET",
    terminalNetinfoKey,
    "moid",
    moid,
    "ip",
    ARGV[3],
    "nat_ip",
    ARGV[4],
    "dns",
    ARGV[5],
    "sip_link_protocol",
    ARGV[6]
)
