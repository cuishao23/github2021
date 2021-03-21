-- 上报丢包率
-- 参数: moid 发送丢包率 接收丢包率
local moid = ARGV[1]
local sendPLR = ARGV[2]
local recvPLR = ARGV[3]

local pServerMoid = redis.call("HGET", "l_server:" .. moid .. ":info", "p_server_moid")

if pServerMoid then
    local packetLossKey = "p_server:" .. pServerMoid .. ":packet_loss_rate"
    redis.call("HSET", packetLossKey, "send_loss_rate", sendPLR)
    redis.call("HSET", packetLossKey, "recv_loss_rate", recvPLR)
end
