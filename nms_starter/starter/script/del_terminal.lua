-- 删除终端
-- 参数: domain_moid moid
local moid = ARGV[1]

local KeyTerminalInfo = "terminal:" .. moid .. ":baseinfo"

local ResultBaseInfo = redis.call("EXISTS", KeyTerminalInfo)

if 1 == ResultBaseInfo then
	local TerminalE164 = redis.call("HGET", KeyTerminalInfo, "e164")
	local TerminalName = redis.call("HGET", KeyTerminalInfo, "name")
	local domain_moid = redis.call("HGET", KeyTerminalInfo, "domain_moid")

	local KeyDomainTerminal = "domain:" .. domain_moid .. ":terminal"
	local KeyDomainTerminalE164 = "domain:" .. domain_moid .. ":terminal_e164"
	local KeyE164Info = "terminal:" .. TerminalE164 .. ":baseinfo"

	local ResultE164BaseInfo = redis.call("EXISTS", KeyE164Info)
	if 1 == ResultE164BaseInfo then
		local BakMoid = redis.call("HGET", KeyE164Info, "bak_moid") or ""
		if BakMoid == "" then
			redis.call("DEL", KeyE164Info)
			redis.call("SREM", KeyDomainTerminalE164, TerminalE164)
		else
			local BakterminalInfoKey = "terminal:" .. BakMoid .. ":baseinfo"
			redis.call("HSET", KeyE164Info, "bak_moid", "")
			if TerminalE164 ~= "" and TerminalE164 ~= TerminalName then
				local BakDomainMoid = redis.call("HGET", BakterminalInfoKey, "domain_moid")
				local bakName = redis.call("HGET", BakterminalInfoKey, "name")
				redis.call("HSET", KeyE164Info, "moid", BakMoid)
				redis.call("HSET", KeyE164Info, "domain_moid", BakDomainMoid)
				redis.call("HSET", KeyE164Info, "name", bakName)
			end
		end
	end
	redis.call("SREM", KeyDomainTerminal, moid)
end

local KeyTerminalInfo = "terminal:" .. moid .. ":*"

local KeyList = redis.call("KEYS", KeyTerminalInfo)
for i = 1, table.getn(KeyList) do
	redis.call("DEL", KeyList[i])
end
