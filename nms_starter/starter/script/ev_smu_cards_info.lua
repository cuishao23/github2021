-- smu 板卡信息
-- 参数: smu_moid card_moid card_ip card_state collector
local smu_moid = ARGV[1]
local card_moid = ARGV[2]
local card_ip = ARGV[3]
local card_state = ARGV[4]
local card_collector = ARGV[5]

local smuCardKey = "smu:" .. smu_moid .. ":card"
redis.call("SADD", smuCardKey, card_moid)

-- p_server:moid:info
local pServerInfoKey = "p_server:" .. card_moid .. ":info"
if redis.call("EXISTS", pServerInfoKey) == 1 then
    redis.call("HMSET", pServerInfoKey, "ip", card_ip, "smu", smu_moid)

    local cardType = redis.call("HGET", pServerInfoKey, "type")
    local pServerOnlineKey = "p_server:" .. card_moid .. ":online"
    if card_state == "1" or card_state == 1 then
        redis.call("SET", pServerOnlineKey, "online")
        if cardType ~= nil and card_collector then
            local collectorOnlineKey = "collector:" .. card_collector .. ":online"
            redis.call("HSET", collectorOnlineKey, card_moid, cardType)
        end
    else
        redis.call("SET", pServerOnlineKey, "offline")
        if card_collector then
            local collectorOnlineKey = "collector:" .. card_collector .. ":online"
            redis.call("HDEL", collectorOnlineKey, card_moid)
        end
    end
end
