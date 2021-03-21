#!/bin/bash
export LC_ALL="en_US.UTF-8"

mkdir -p .files_temp/package
PACKAGE_PATH=$(pwd)/.files_temp/package
RELEASE_PATH=$(pwd)/../../../10-common/version/release/linux/nms
PYTHON_DEPOT_PATH=$(pwd)/../nms_python
ls | grep -v ".files_temp" | grep -v "package.sh" | xargs -i \cp -a {} .files_temp/package

# python3 模块打包
pythonpath=${PACKAGE_PATH}/starter_python3
export PYTHONPATH=${pythonpath}/lib/python3.5/site-packages
PIP=/opt/midware/python3/bin/pip3
PIP_OPTION="--prefix=${pythonpath} --find-links=${PYTHON_DEPOT_PATH}"

\cp -a ${PYTHON_DEPOT_PATH}/* .files_temp/

${PIP} install .files_temp/redis-3.3.7-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/docutils-0.15.2-py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/setuptools-42.0.2-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/lockfile-0.12.2-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/python_daemon-2.2.4-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/pika-1.1.0-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/setproctitle-1.1.10.tar.gz ${PIP_OPTION}
${PIP} install .files_temp/SQLAlchemy-1.3.8.tar.gz ${PIP_OPTION}
${PIP} install .files_temp/PyMySQL-0.9.3-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/ ${PIP_OPTION}
${PIP} install .files_temp/urllib3-1.25.7-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/certifi-2019.11.28-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/chardet-3.0.4-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/idna-2.8-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/requests-2.22.0-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/xlrd-1.2.0-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/decorator-4.4.2-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/py-1.8.1-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/retry-0.9.2-py2.py3-none-any.whl ${PIP_OPTION}
${PIP} install .files_temp/APScheduler-3.6.3-py2.py3-none-any.whl ${PIP_OPTION}

# 拷贝飞腾依赖
\cp -a ${PYTHON_DEPOT_PATH}/ft/psycopg2 ${pythonpath}/lib/python3.5/site-packages/

# make starter.bin
cd .files_temp
makeself package/ ./nms_starter.bin "Installing nms starter..." ./install.sh
mv ./nms_starter.bin ${RELEASE_PATH}/
cd - 
rm -rf .files_temp