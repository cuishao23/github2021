-- 更新国密状态
-- 参数: moid devType pkt_loss_resend audio_first fec decode_payload_auto
local moid = ARGV[1]
local devType = ARGV[2]
local devKeyType = string.gsub(devType, ' ', '~')
local terminalRuninginfoKey = "terminal:" .. moid .. ":" .. devKeyType .. ":runinginfo"

redis.call(
    "HMSET",
    terminalRuninginfoKey,
    "pkt_loss_resend",
    ARGV[3],
    "audio_first",
    ARGV[4],
    "fec",
    ARGV[5],
    "decode_payload_auto",
    ARGV[6]
)
