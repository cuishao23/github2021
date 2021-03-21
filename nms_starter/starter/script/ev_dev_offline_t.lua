-- 终端下线(兼容26终端)
-- 参数: moid|e164 dev_type collectorid

local moidOrE164 = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, ' ', '~')
local collectorid = ARGV[3]
local moid = redis.call("HGET", "terminal:" .. moidOrE164 .. ":baseinfo", 'moid')

--比对collectorid是否相等，不相等就不删除
if moid then
    local terminalBaseinfoKey = "terminal:" .. moid .. ":baseinfo"
    local terminalCollectorIDKey = "terminal:" .. moid .. ":collectorid"
    local collectorOnlineKey = "collector:" .. collectorid .. ":online"
    if collectorid == redis.call("HGET", terminalCollectorIDKey, devType) then
        redis.call("HDEL", terminalCollectorIDKey, devType)

        --del terminal:moid:connection
        local KeyConnections = "terminal:" .. moid .. ":" .. devKeyType .. ":connection"
        redis.call("DEL", KeyConnections)

        --del terminal:moid:resource
        local KeyResource = "terminal:" .. moid .. ":" .. devKeyType .. ":resource"
        redis.call("DEL", KeyResource)

        --del terminal:moid:runninginfo
        local KeyRunningInfo = "terminal:" .. moid .. ":" .. devKeyType .. ":runninginfo"
        redis.call("DEL", KeyRunningInfo)

        --del terminal:moid:netinfo
        local KeyNetInfo = "terminal:" .. moid .. ":" .. devKeyType .. ":netinfo"
        local terminalIp = redis.call("HGET", KeyNetInfo, "ip") or ""
        if "" ~= terminalIp then
            redis.call("DEL", "ip:" .. terminalIp .. ":terminal")
        end
        redis.call("DEL", KeyNetInfo)

        -- del imix
        local ImixKey = "terminal:" .. moid .. ":" .. devKeyType .. ":imix"
        if 1 == redis.call("EXISTS", ImixKey) then
            local ImixList = redis.call("SMEMBERS", ImixKey)
            for i = 1, #ImixList do
                local ItemKey = "imix:" .. ImixList[i] .. ":info"
                redis.call("DEL", ItemKey)
            end
            redis.call("DEL", ImixKey)
        end

        --del terminal:moid:onlinestate
        local KeyOnline = "terminal:" .. moid .. ":onlinestate"
        local onlineState = redis.call("HGET", KeyOnline, devType)
        redis.call("HDEL", KeyOnline, devType)
        if "conference" == onlineState then
            --del terminal:moid:meetingdetail
            local KeyMeetingDetail = "terminal:" .. moid .. ":meetingdetail"
            redis.call("DEL", KeyMeetingDetail)
            -- delete privideo_send_chan
            local KeyVPSChan = "terminal:" .. moid .. ":meetingdetail:privideo_send_chan"
            local VPSChanList = redis.call("SMEMBERS", KeyVPSChan)
            for i, index in pairs(VPSChanList) do
                local KeyVPSChanInfo = KeyVPSChan .. ":" .. index
                redis.call("DEL", KeyVPSChanInfo)
            end
            redis.call("DEL", KeyVPSChan)

            -- delete privideo_recv_chan
            local KeyVPRChan = "terminal:" .. moid .. ":meetingdetail:privideo_recv_chan"
            local VPRChanList = redis.call("SMEMBERS", KeyVPRChan)
            for i, index in pairs(VPRChanList) do
                local KeyVPRChanInfo = KeyVPRChan .. ":" .. index
                redis.call("DEL", KeyVPRChanInfo)
            end
            redis.call("DEL", KeyVPRChan)

            -- delete assvideo_send_chan
            local KeyVASChan = "terminal:" .. moid .. ":meetingdetail:assvideo_send_chan"
            local VASChanList = redis.call("SMEMBERS", KeyVASChan)
            for i, index in pairs(VASChanList) do
                local KeyVASChanInfo = KeyVASChan .. ":" .. index
                redis.call("DEL", KeyVASChanInfo)
            end
            redis.call("DEL", KeyVASChan)

            -- delete assvideo_recv_chan
            local KeyVARChan = "terminal:" .. moid .. ":meetingdetail:assvideo_recv_chan"
            local VARChanList = redis.call("SMEMBERS", KeyVARChan)
            for i, index in pairs(VARChanList) do
                local KeyVARChanInfo = KeyVARChan .. ":" .. index
                redis.call("DEL", KeyVARChanInfo)
            end
            redis.call("DEL", KeyVARChan)

            -- delete audio_send_chan
            local KeyASChan = "terminal:" .. moid .. ":meetingdetail:audio_send_chan"
            local ASChanList = redis.call("SMEMBERS", KeyASChan)
            for i, index in pairs(ASChanList) do
                local KeyASChanInfo = KeyASChan .. ":" .. index
                redis.call("DEL", KeyASChanInfo)
            end
            redis.call("DEL", KeyASChan)

            -- delete audio_recv_chan
            local KeyARChan = "terminal:" .. moid .. ":meetingdetail:audio_recv_chan"
            local ARChanList = redis.call("SMEMBERS", KeyARChan)
            for i, index in pairs(ARChanList) do
                local KeyARChanInfo = KeyARChan .. ":" .. index
                redis.call("DEL", KeyARChanInfo)
            end
            redis.call("DEL", KeyARChan)
        end

        -- 删除终端外设信息
        local CameraListKey = "terminal:" .. moid .. ":" .. devKeyType .. ":camera"
        local CameraIds = redis.call("SMEMBERS", CameraListKey)
        for i = 1, table.getn(CameraIds) do
            local cameraInfoKey = "camera:" .. CameraIds[i] .. ":info"
            redis.call("DEL", cameraInfoKey)
        end
        redis.call("DEL", CameraListKey)

        local MicrophoneListKey = "terminal:" .. moid .. ":" .. devKeyType .. ":microphone"
        local MicrophoneIds = redis.call("SMEMBERS", MicrophoneListKey)
        for i = 1, table.getn(MicrophoneIds) do
            local microphoneInfoKey = "microphone:" .. MicrophoneIds[i] .. ":info"
            redis.call("DEL", microphoneInfoKey)
        end
        redis.call("DEL", MicrophoneListKey)

        -- 删除collector中上线信息
        redis.call("HDEL", collectorOnlineKey, moid)

        -- 阈值判定
        local result = {}
        result["domain_moid"] = redis.call("HGET", terminalBaseinfoKey, "domain_moid")
        -- 阈值告警判定
        local limit = redis.call("HGET", "warning:limit:global", "s_nms")
        local server_count = redis.call("HLEN", collectorOnlineKey)
        local collectorInfoKey = "collector:" .. collectorid .. ":info"
        result["warning_trigger_flag"] = tonumber(server_count) >= tonumber(limit)
        result["collector_p_server_moid"] = redis.call("HGET", collectorInfoKey, "p_server_moid")
        result["current_value"] = server_count
        result["threshold_value"] = limit

        return string.gsub(cjson.encode(result), "{}", "[]")
    end
end
