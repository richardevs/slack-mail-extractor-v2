# Build function.zip for Lambda upload (Windows Powershell Version)
pip3.exe install --target ./package slackclient pyyaml

Remove-Item function.zip -ErrorAction Ignore

New-Item -Force -ItemType Directory temp
New-Item -Force -ItemType Directory temp\package
Copy-Item -Path (Get-Item -Path "package\*" -Exclude ('__pycache__')).FullName -Destination temp\package -Recurse -Force
New-Item -Force -ItemType Directory temp\templates
Copy-Item -Path (Get-Item -Path "templates\*" -Exclude ('__pycache__')).FullName -Destination temp\templates -Recurse -Force
Copy-Item -Recurse -Force lambda_function.py temp
Copy-Item -Recurse -Force secrets.py temp
Compress-Archive -Path temp\* -DestinationPath function.zip
Remove-Item temp -Recurse