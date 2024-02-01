##############################################################
#	Simple Password Manager
##############################################################
#   - Update README to link to all relevant Docs needed
#	- User can download SQLite Studio to interact with DB
#   - Decided to use SQLite over MySQL due to SQLite being
#		more lightweight and restricted to only 1 user
# ##############################################################

Libraries and Packages used:
-	DateTime
-	Cryptography
	https://cryptography.io
-	SQLite
	https://www.sqlite.org/docs.html
	https://docs.python.org/3/library/sqlite3.html
	https://sqlitestudio.pl/
-	Tabulate
	https://pypi.org/project/tabulate/
-	PyInstaller
	https://pyinstaller.org/en/stable/
	### From DIR <path\script.py> in CMD
	### python -m PyInstaller --onefile --name <script.py> <path\script.py>
	### Edit SPEC file to start with:
	### Import kivy
	### from kivy.deps import sdl2, glew, gstreamer
	### SPEC file body amendments:
	### exe = EXE(pyz, Tree('<path\\>'), a.scripts, a.binaries, a.zipfiles, a.datas, *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)], upx=True, name='<script>')
	### Remember to use double \\ in above
	### python -m PyInstaller <path\script.py>