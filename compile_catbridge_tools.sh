python setup.py install
pyinstaller bin/cn_find.py -F
mv dist/cn_find.exe cn_find.exe
pyinstaller bin/marc_count.py -F
mv dist/marc_count.exe marc_count.exe
pyinstaller bin/keep_fld.py -F
mv dist/keep_fld.exe keep_fld.exe
pyinstaller bin/fix_fmt.py -F
mv dist/fix_fmt.exe fix_fmt.exe
rm bin/__pycache__/*.cpython-37.pyc
rmdir bin/__pycache__
rm -rf build
rm *.spec
read -p "Press [Enter]"