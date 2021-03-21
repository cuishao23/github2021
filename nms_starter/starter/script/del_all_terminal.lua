-- 删除用户域下的所有终端
-- 参数: domain_moid
local domain_modi = ARGV[1]
local KeyDomainTerminal = "domain:" .. domain_modi .. ":terminal"
local DevMoidList = redis.call("SMEMBERS", KeyDomainTerminal)
table.foreach(
    DevMoidList,
    function(i, DevMoid)
        redis.call("DEL", "terminal:" .. DevMoid .. ":baseinfo")
        redis.call("DEL", "terminal:" .. DevMoid .. ":onlinestate")
    end
)
redis.call("DEL", KeyDomainTerminal)

local KeyDomainTerminalE164 = "domain:" .. domain_modi .. ":terminal_e164"
local DevE164List = redis.call("SMEMBERS", KeyDomainTerminalE164)
table.foreach(
    DevE164List,
    function(i, DevE164)
        local KeyTerminalE164Info = "terminal:" .. DevE164 .. ":baseinfo"
        redis.call("DEL", KeyTerminalE164Info)
    end
)
redis.call("DEL", KeyDomainTerminalE164)
