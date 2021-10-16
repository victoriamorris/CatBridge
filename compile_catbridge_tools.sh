python setup.py install
pyinstaller bin/get_fields.py -F
mv dist/get_fields.exe get_fields.exe
#rmdir dist/__pycache__
rmdir dist
rm bin/__pycache__/get_fields.cpython-37.pyc
rmdir bin/__pycache__
#rmdir catbridge_tools/__pycache__
rm -rf build
rm get_fields.spec
read -p "Press [Enter]"