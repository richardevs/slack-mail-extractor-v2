# Build function.zip for Lambda upload (Have not fully tested)
pip3 install --target ./package slackclient pyyaml
rm -f function.zip
zip -r9 -g function.zip lambda_function.py secrets.py package templates