python setup.py install
pyinstaller bin/cn_find.py -F
mv dist/cn_find.exe cn_find.exe
#rmdir dist/__pycache__
#rmdir dist
rm bin/__pycache__/cn_find.cpython-37.pyc
rmdir bin/__pycache__
#rmdir catbridge_tools/__pycache__
rm -rf build
rm *.spec
read -p "Press [Enter]"