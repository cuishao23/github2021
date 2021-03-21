#!/bin/bash

. /opt/data/luban/shells/kdfunctions
BASE_PATH=/opt/mcu/nms_starter
mkdir -p ${BASE_PATH}
ls ${BASE_PATH} | grep -v "shells" | xargs -i rm -rf ${BASE_PATH}/{} 
ls | grep -v "install.sh" | xargs -i cp -a {} ${BASE_PATH}/ 

# 飞腾特殊处理
system_type=$(get_system_type)
if [ x"${system_type}" == x"1" ];then
    set_field_value $BASE_PATH/etc/nms_starter.ini nms db_engine highgodb 
fi