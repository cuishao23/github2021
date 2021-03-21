-- 获取告警相关的所有信息
-- 参数: moid, code, server_type
local moid = ARGV[1]
local code = ARGV[2]
local server_type = ARGV[3]

local serverInfoKey
local domainMoid
local parentDomainMoid
local parentDomainMoids = {}

local result = {}
result["server_info"] = {}

if (server_type == "terminal") then
    serverInfoKey = server_type .. ":" .. moid .. ":baseinfo"
    domainMoid = redis.call("HGET", serverInfoKey, "domain_moid") or ""
    parentDomainMoid = redis.call("HGET", "domain:" .. domainMoid .. ":info", "parent_moid") or ""
    local terminalType = ARGV[4] or ''
    terminalType = string.gsub(terminalType, ' ', '~')
    result["server_info"]['ip'] = redis.call('HGET', 'terminal:'..moid..':'..terminalType..':netinfo', 'ip')
else
    serverInfoKey = server_type .. ":" .. moid .. ":info"
    domainMoid = redis.call("HGET", serverInfoKey, "machine_room_moid") or ""
    result["server_info"]["machine_room_name"] = redis.call("HGET", "machine_room:" .. domainMoid .. ":info", "name")
    parentDomainMoid = redis.call("HGET", "machine_room:" .. domainMoid .. ":info", "domain_moid") or ""
end

-- 告警屏蔽信息
local warningStop = redis.call("SISMEMBER", "warning:stop", domainMoid)
if warningStop == "1" or warningStop == 1 then
    return nil
end

-- 服务器信息
local info = redis.call("HGETALL", serverInfoKey)
for i, v in pairs(info) do
    if i % 2 == 0 then
        result["server_info"][info[i - 1]] = v
    end
end

-- 未修复告警
local serverWarningKey = server_type .. ":" .. moid .. ":warning"
result["warning_unrepaired"] = redis.call("HEXISTS", serverWarningKey, code)

-- 告警信息
local warningCodeKey = "warning:code:" .. code
if redis.call("EXISTS", warningCodeKey) == 1 then
    local info = redis.call("HGETALL", warningCodeKey)
    result["warning_info"] = {}
    for i, v in pairs(info) do
        if i % 2 == 0 then
            result["warning_info"][info[i - 1]] = v
        end
    end
    result["warning_info"]["code"] = tonumber(code)
end

-- 告警通知信息
-- 查询所有父级域, 查询域下是否有配置告警通知
result["notify_info"] = {
    ["email"] = {},
    ["phone"] = {},
    ["wechat"] = {}
}
while (true) do
    parentDomainMoid = redis.call("HGET", "domain:" .. parentDomainMoid .. ":info", "parent_moid")
    if (parentDomainMoid ~= "-1" and parentDomainMoid) then
        table.insert(parentDomainMoids, parentDomainMoid)
    else
        break
    end
end
for i, domainMoid in pairs(parentDomainMoids) do
    for j, notifyID in pairs(redis.call("SMEMBERS", "warning:notify:" .. domainMoid)) do
        if redis.call("SISMEMBER", "warning:notify:" .. notifyID .. ":codes", code) then
            local notifyInfo = redis.call("HMGET", "warning:notify:" .. notifyID .. ":info", "email", "phone", "wechat")
            if notifyInfo[1] ~= "" and notifyInfo[1] then
                table.insert(result["notify_info"]["email"], notifyInfo[1])
            end
            if notifyInfo[2] ~= "" and notifyInfo[2] then
                table.insert(result["notify_info"]["phone"], notifyInfo[2])
            end
            if notifyInfo[3] ~= "" and notifyInfo[3] then
                table.insert(result["notify_info"]["wechat"], notifyInfo[3])
            end
        end
    end
end
return string.gsub(cjson.encode(result), "{}", "[]")
