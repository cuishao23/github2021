-- 添加终端
-- 信息结构
-- terminal:{E164}:baseinfo   |
-- terminal:{modi1}:baseinfo  | --> 一组信息, 可以互查, 为方便通过E164号查找到两个moid, 增加 'bak_moid'字段
-- terminal:{moid2}:baseinfo  |
-- bak_moid 记录name=E164号的那条信息的moid
--
-- 参数: moid domain_moid name [E164]
local moid = ARGV[1]
local domain_moid = ARGV[2]
local name = ARGV[3]
local E164 = ARGV[4]
local KeyDomainTerminal = "domain:" .. domain_moid .. ":terminal"
local KeyDomainTerminalE164 = "domain:" .. domain_moid .. ":terminal_e164"
local KeyTerminalInfo = "terminal:" .. moid .. ":baseinfo"
-- E164
if redis.call("EXISTS", KeyTerminalInfo) ~= 1 then
    if E164 and E164 ~= "" then
        local KeyE164Info = "terminal:" .. E164 .. ":baseinfo"

        local ResultBaseInfo = redis.call("EXISTS", KeyE164Info)

        if 1 == ResultBaseInfo then
            if name == E164 then
                redis.call("HSET", KeyE164Info, "bak_moid", moid)
            else
                local BackMoid = redis.call("HGET", KeyE164Info, "moid")
                redis.call("HSET", KeyE164Info, "moid", moid)
                redis.call("HSET", KeyE164Info, "domain_moid", domain_moid)
                redis.call("HSET", KeyE164Info, "name", name)
                redis.call("HSET", KeyE164Info, "e164", E164)
                redis.call("HSET", KeyE164Info, "bak_moid", BackMoid)
            end
        else
            redis.call("HSET", KeyE164Info, "moid", moid)
            redis.call("HSET", KeyE164Info, "domain_moid", domain_moid)
            redis.call("HSET", KeyE164Info, "name", name)
            redis.call("HSET", KeyE164Info, "e164", E164)
            redis.call("HSET", KeyE164Info, "bak_moid", "")
        end

        redis.call("HSET", KeyTerminalInfo, "moid", moid)
        redis.call("HSET", KeyTerminalInfo, "domain_moid", domain_moid)
        redis.call("HSET", KeyTerminalInfo, "name", name)
        redis.call("HSET", KeyTerminalInfo, "e164", E164)

        redis.call("SADD", KeyDomainTerminal, moid)
        redis.call("SADD", KeyDomainTerminalE164, E164)
    else
        -- 不存在 E164号
        -- terminal
        redis.call("HSET", KeyTerminalInfo, "moid", moid)
        redis.call("HSET", KeyTerminalInfo, "domain_moid", domain_moid)
        redis.call("HSET", KeyTerminalInfo, "name", name)
        redis.call("HSET", KeyTerminalInfo, "e164", "")
        -- domain
        redis.call("SADD", KeyDomainTerminal, moid)
    end
end
