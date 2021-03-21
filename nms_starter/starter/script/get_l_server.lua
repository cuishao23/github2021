-- 获取逻辑服务器的详细信息
-- 参数: moid
local Key = "l_server:" .. ARGV[1] .. ":info"

local result = {}
local info = redis.call("HGETALL", Key)
for i, v in pairs(info) do
    if i % 2 == 0 then
        result[info[i - 1]] = v
    end
end

local machineRoomInfoKey = "machine_room:" .. result["machine_room_moid"] .. ":info"
result["machine_room_name"] = redis.call("HGET", machineRoomInfoKey, "name")
return string.gsub(cjson.encode(result), "{}", "[]")
