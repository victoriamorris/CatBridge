python -m PyInstaller bin/cn_find.py -F
mv dist/cn_find.exe exe/cn_find.exe
python -m PyInstaller bin/marc_count.py -F
mv dist/marc_count.exe exe/marc_count.exe
python -m PyInstaller bin/keep_fld.py -F
mv dist/keep_fld.exe exe/keep_fld.exe
python -m PyInstaller bin/fix_fmt.py -F
mv dist/fix_fmt.exe exe/fix_fmt.exe
python -m PyInstaller bin/marc_check.py -F
mv dist/marc_check.exe exe/marc_check.exe
rmdir -rf catbridge_tools/__pycache__
rm -rf build
rm *.spec
read -p "Press [Enter]"