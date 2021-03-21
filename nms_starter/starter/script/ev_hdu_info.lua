local info = cjson.decode(ARGV[1])


if info['hdu_info'] == 1 or info['hdu_info'] == '1' then
    -- 上线
    redis.call('HSET', 'p_server:'..info['hdu_guid']..':info', 'ip', info['hdu_ip'])
    redis.call('SET', 'p_server:'..info['hdu_guid']..':online', 'online')
else
    -- 下线
    redis.call('SET', 'p_server:'..info['hdu_guid']..':online', 'offline')
end