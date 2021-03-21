-- 服务器上线统计
-- 返回json

local result = {}
local machineRoomMoidList = redis.call("SMEMBERS", "machine_room_moids")
for i, machineRoomMoid in pairs(machineRoomMoidList) do
    if redis.call("EXISTS", "machine_room:" .. machineRoomMoid .. ":info") ~= 0 then
        result[machineRoomMoid] = {}
        result[machineRoomMoid]["total"] = redis.call("SCARD", "machine_room:" .. machineRoomMoid .. ":p_server")
        result[machineRoomMoid]["online"] = 0
        for i, pMoid in pairs(redis.call("SMEMBERS", "machine_room:" .. machineRoomMoid .. ":p_server")) do
            if redis.call("EXISTS", "p_server:" .. pMoid .. ":online") ~= 0 then
                result[machineRoomMoid]["online"] = result[machineRoomMoid]["online"] + 1
            end
        end
    end
end
return string.gsub(cjson.encode(result), "{}", "[]")
