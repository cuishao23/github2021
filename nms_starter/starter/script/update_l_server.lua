-- 逻辑服务器修改
-- 参数: moid name type machine_room_moid p_server_moid
local moid = ARGV[1]
local name = ARGV[2]
local type = ARGV[3]
local machine_room_moid = ARGV[4]
local p_server_moid = ARGV[5]

-- l_server
local lServerInfoKey = "l_server:" .. moid .. ":info"
redis.call(
    "HMSET",
    lServerInfoKey,
    "moid",
    moid,
    "name",
    name,
    "type",
    type,
    "machine_room_moid",
    machine_room_moid,
    "p_server_moid",
    p_server_moid
)
