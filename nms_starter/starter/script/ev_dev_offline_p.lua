-- 物理服务离线
-- 参数: moid collectorid
local moid = ARGV[1]
local collectorid = ARGV[2]

local pServerInfoKey = "p_server:" .. moid .. ":info"
local collectorOnlineKey = "collector:" .. collectorid .. ":online"

-- 比对collectorid是否相等，不相等就不删除
if redis.call("HGET", pServerInfoKey, "collectorid") == collectorid then
    -- 删除online信息
    redis.call("HDEL", collectorOnlineKey, moid)

    -- del p_server:moid:online
    local KeyOnline = "p_server:" .. moid .. ":online"
    redis.call("DEL", KeyOnline)

    -- HDEL p_server:moid:info collectorid
    redis.call("HDEL", pServerInfoKey, "collectorid")

    -- del p_server:moid:resource
    local KeyResource = "p_server:" .. moid .. ":resource"
    redis.call("DEL", KeyResource)

    -- del p_server:moid:warning
    local KeyWarning = "p_server:" .. moid .. ":warning"
    redis.call("DEL", KeyWarning)

    local Type = redis.call("HGET", pServerInfoKey, "type")

    -- SMU下线处理
    if Type == "smu" then
        local KeySmu = "smu:" .. moid .. ":card"
        -- 需要把smu上的版本下线
        local CardList = redis.call("SMEMBERS", KeySmu)
        for i = 1, table.getn(CardList) do
            local CardInfo = "p_server:" .. CardList[i] .. ":info"
            local CardType = redis.call("HGET", CardInfo, "type")
            if CardType == "xmpu" or CardType == "xmpu5" then
                local XMPUonline = "p_server:" .. CardList[i] .. ":online"
                redis.call("DEL", XMPUonline)

                local XMPUResource = "p_server:" .. CardList[i] .. ":resource"
                redis.call("DEL", XMPUResource)

                local XMPUWarning = "p_server:" .. CardList[i] .. ":warning"
                redis.call("DEL", XMPUWarning)

                local XMPUCardLight = "card:" .. CardList[i] .. ":light"
                redis.call("DEL", XMPUCardLight)
            end
        end

        -- smu:moid:left_light
        local KeySmuLeftLight = "smu:" .. moid .. ":left_light"
        redis.call("DEL", KeySmuLeftLight)
        -- smu:moid:right_light
        local KeySmuRightLight = "smu:" .. moid .. ":right_light"
        redis.call("DEL", KeySmuRightLight)

        -- smu:moid:frame_light
        local KeySmuFrameLight = "smu:" .. moid .. ":frame_light"
        redis.call("DEL", KeySmuFrameLight)

        -- card:moid:light
        local KeyCardLight = "card:" .. moid .. ":light"
        redis.call("DEL", KeyCardLight)

        redis.call("DEL", KeySmu)
    end

    if Type == "jd6000" or Type == "jd6000_C" or Type == "dx6000" or Type == "jd10000" then
        local KeySmu = "smu:" .. moid .. ":card"
        -- SMU下线时需要把SMU上的XMPU下线掉
        local CardList = redis.call("SMEMBERS", KeySmu)
        for i = 1, table.getn(CardList) do
            local CardInfo = "p_server:" .. CardList[i] .. ":info"
            local CardType = redis.call("HGET", CardInfo, "type")
            if CardType == "xmpu" or CardType == "xmpu5" then
                local XMPUonline = "p_server:" .. CardList[i] .. ":online"
                redis.call("DEL", XMPUonline)

                local XMPUResource = "p_server:" .. CardList[i] .. ":resource"
                redis.call("DEL", XMPUResource)

                local XMPUWarning = "p_server:" .. CardList[i] .. ":warning"
                redis.call("DEL", XMPUWarning)

                local XMPUCardLight = "card:" .. CardList[i] .. ":light"
                redis.call("DEL", XMPUCardLight)
            end
        end

        -- smu:moid:left_light
        local KeySmuLeftLight = "smu:" .. moid .. ":left_light"
        redis.call("DEL", KeySmuLeftLight)
        -- smu:moid:right_light
        local KeySmuRightLight = "smu:" .. moid .. ":right_light"
        redis.call("DEL", KeySmuRightLight)

        -- smu:moid:frame_light
        local KeySmuFrameLight = "smu:" .. moid .. ":frame_light"
        redis.call("DEL", KeySmuFrameLight)

        -- card:moid:light
        local KeyCardLight = "card:" .. moid .. ":light"
        redis.call("DEL", KeyCardLight)

        redis.call("DEL", KeySmu)
    end

    -- kdv8000a
    if Type == "kdv8000a" then
        local KeySmu = "smu:" .. moid .. ":card"
        -- SMU下线时需要把SMU上的XMPU下线掉
        local CardList = redis.call("SMEMBERS", KeySmu)
        for i = 1, table.getn(CardList) do
            local CardInfo = "p_server:" .. CardList[i] .. ":info"
            local CardType = redis.call("HGET", CardInfo, "type")
            if CardType == "xmpu" or CardType == "xmpu5" then
                local XMPUonline = "p_server:" .. CardList[i] .. ":online"
                redis.call("DEL", XMPUonline)

                local XMPUResource = "p_server:" .. CardList[i] .. ":resource"
                redis.call("DEL", XMPUResource)

                local XMPUWarning = "p_server:" .. CardList[i] .. ":warning"
                redis.call("DEL", XMPUWarning)

                local XMPUCardLight = "card:" .. CardList[i] .. ":light"
                redis.call("DEL", XMPUCardLight)
            end
        end

        redis.call("DEL", KeySmu)
    end

    if Type == "tvs4000" then
        local keySmu = "smu:" .. moid .. ":card"
        -- TVS4000下线需要把TVS4000上的设备下线
        local CardList = redis.call("SMEMBERS", keySmu)
        for i = 1, table.getn(CardList) do
            local CardInfo = "p_server:" .. CardList[i] .. ":info"
            redis.call("HDEL", CardInfo, "ip")
            redis.call("HDEL", CardInfo, "smu")
            redis.call("HDEL", CardInfo, "collectorid")

            local CardOnlineInfo = "p_server:" .. CardList[i] .. ":online"
            redis.call("DEL", CardOnlineInfo)

            redis.call("HDEL", collectorOnlineKey, CardList[i])
        end

        redis.call("DEL", keySmu)
    end

    redis.call("HDEL", pServerInfoKey, "layer")

end

-- 阈值告警判定
local result = {}
local limit = redis.call("HGET", "warning:limit:global", "s_nms")
local p_server_count = redis.call("HLEN", collectorOnlineKey)
local collectorInfoKey = "collector:" .. collectorid .. ":info"
result["warning_trigger_flag"] = tonumber(p_server_count) >= tonumber(limit)
result["collector_p_server_moid"] = redis.call("HGET", collectorInfoKey, "p_server_moid")
result["current_value"] = p_server_count
result["threshold_value"] = limit

return string.gsub(cjson.encode(result), "{}", "[]")
