python setup.py install
pyinstaller bin/cn_find.py -F
mv dist/cn_find.exe cn_find.exe
pyinstaller bin/marc_count.py -F
mv dist/marc_count.exe marc_count.exe
rm bin/__pycache__/cn_find.cpython-37.pyc
rm bin/__pycache__/marc_count.cpython-37.pyc
rm bin/__pycache__
rm -rf build
rm *.spec
read -p "Press [Enter]"